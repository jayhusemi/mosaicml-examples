# Copyright 2022 MosaicML Examples authors
# SPDX-License-Identifier: Apache-2.0

import gc

from composer.core import Callback, State
from composer.loggers import Logger


class ScheduledGarbageCollector(Callback):
    """Disable automatic garbage collection and collect garbage at interval.

    Args:
        batch_interval (int): Number of batches between checkpoints call to gc.collect()
        eval_keep_disabled (bool): keep gc disabled during eval (default: False)
    """

    def __init__(
        self,
        batch_interval: int,
        eval_keep_disabled: bool = False,
    ):
        self.batch_interval = batch_interval
        self.eval_keep_disabled = eval_keep_disabled

    def fit_start(self, state: State, logger: Logger):
        # cache if automatic garbage collection is enabled; reset at fit_end
        self.gc_init_state = gc.isenabled()

        # disable automatic garbage collection
        gc.disable()
        gc.collect()

    def fit_end(self, state: State, logger: Logger):
        gc.collect()

        # reset automatic garbage collection at fit_end
        if self.gc_init_state:
            gc.enable()
        else:
            gc.disable()

    def before_dataloader(self, state: State, logger: Logger):
        if state.timestamp.batch.value % self.batch_interval == 0:
            gc.collect()

    def eval_start(self, state: State, logger: Logger):
        gc.collect()
        if not self.eval_keep_disabled:
            gc.enable()

    def eval_end(self, state: State, logger: Logger):
        if not self.eval_keep_disabled:
            gc.disable()
        gc.collect()