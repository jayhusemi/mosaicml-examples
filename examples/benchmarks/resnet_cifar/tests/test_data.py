# Copyright 2022 MosaicML Examples authors
# SPDX-License-Identifier: Apache-2.0

import os
import sys

import pytest
import torch
from torch.utils.data import DataLoader

# Add folder root to path to allow us to use relative imports regardless of what directory the script is run from
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Add tests folder root to path to allow us to use relative imports regardless of what directory the script is run from
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data import build_cifar10_dataspec
from utils import SynthClassificationDirectory

# TODO: streaming dataset and dataloader testing


@pytest.mark.parametrize('is_train', [True, False])
def test_dataloader_builder(is_train, batch_size=2):
    with SynthClassificationDirectory() as datadir:
        cifar_dataspec = build_cifar10_dataspec(data_path=datadir,
                                                is_streaming=True,
                                                local=datadir,
                                                batch_size=batch_size,
                                                is_train=is_train,
                                                download=False)

        assert isinstance(cifar_dataspec.dataloader, DataLoader)
        dataloader = cifar_dataspec.dataloader
        print(len(dataloader))
        assert len(dataloader) == 8

        for batch in dataloader:
            # Check the image and label shapes
            assert batch[0].shape == torch.Size([batch_size, 3, 32, 32])
            assert batch[1].shape == torch.Size([batch_size])
