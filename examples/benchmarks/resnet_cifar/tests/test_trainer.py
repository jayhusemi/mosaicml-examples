# Copyright 2022 MosaicML Examples authors
# SPDX-License-Identifier: Apache-2.0

import os
import sys

import pytest
import torch
from omegaconf import OmegaConf

# Add tests folder root to path to allow us to use relative imports regardless of what directory the script is run from
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# Add folder root to path to allow us to use relative imports regardless of what directory the script is run from
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import main
from utils import SynthClassificationDirectory


@pytest.mark.parametrize('use_recipe', [True, False])
def test_trainer(use_recipe):
    with open('yamls/resnet56.yaml') as f:
        base_config = OmegaConf.load(f)

    with open('tests/smoketest_config.yaml') as f:
        smoke_config = OmegaConf.load(f)
    config = OmegaConf.merge(base_config, smoke_config)
    config.use_recipe = use_recipe
    config.seed = 1337 + 100 * use_recipe

    with SynthClassificationDirectory() as tmp_datadir:
        config.train_dataset.path = tmp_datadir
        config.train_dataset.local = os.path.join(tmp_datadir, 'local1')
        config.eval_dataset.path = tmp_datadir
        config.eval_dataset.local = os.path.join(tmp_datadir, 'local2')
        # Also save checkpoints in the temporary directory
        config.save_folder = tmp_datadir

        # Train
        trainer1 = main(config)
        model1 = trainer1.state.model.module

        # TODO avoid tests taking a long time to exit without this
        trainer1.state.dataloader._iterator._shutdown_workers()  # type: ignore

        # Check that the checkpoint was saved
        chkpt_path = os.path.join(tmp_datadir, 'ep0-ba1-rank0.pt')
        assert os.path.isfile(chkpt_path)

        # Check that the checkpoint was loaded by comparing model weights
        config.load_path = chkpt_path
        config.is_train = False
        config.seed += 10  # change seed
        config.train_dataset.local = os.path.join(tmp_datadir, 'local3')
        config.eval_dataset.local = os.path.join(tmp_datadir, 'local4')
        trainer2 = main(config)
        model2 = trainer2.state.model.module

        for param1, param2 in zip(model1.parameters(), model2.parameters()):
            torch.testing.assert_close(param1, param2)
