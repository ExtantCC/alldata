# Copyright (c) Alibaba, Inc. and its affiliates.
import os
import os.path as osp
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Union

from modelscope.hub.snapshot_download import snapshot_download
from modelscope.models.builder import MODELS, build_model
from modelscope.utils.checkpoint import save_checkpoint, save_pretrained
from modelscope.utils.config import Config
from modelscope.utils.constant import DEFAULT_MODEL_REVISION, ModelFile, Tasks
from modelscope.utils.device import verify_device
from modelscope.utils.logger import get_logger

logger = get_logger()

Tensor = Union['torch.Tensor', 'tf.Tensor']


class Model(ABC):

    def __init__(self, model_dir, *args, **kwargs):
        self.model_dir = model_dir
        device_name = kwargs.get('device', 'gpu')
        verify_device(device_name)
        self._device_name = device_name

    def __call__(self, *args, **kwargs) -> Dict[str, Any]:
        return self.postprocess(self.forward(*args, **kwargs))

    @abstractmethod
    def forward(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Run the forward pass for a model.

        Returns:
            Dict[str, Any]: output from the model forward pass
        """
        pass

    def postprocess(self, inputs: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """ Model specific postprocess and convert model output to
        standard model outputs.

        Args:
            inputs:  input data

        Return:
            dict of results:  a dict containing outputs of model, each
                output should have the standard output name.
        """
        return inputs

    @classmethod
    def _instantiate(cls, **kwargs):
        """ Define the instantiation method of a model,default method is by
            calling the constructor. Note that in the case of no loading model
            process in constructor of a task model, a load_model method is
            added, and thus this method is overloaded
        """
        return cls(**kwargs)

    @classmethod
    def from_pretrained(cls,
                        model_name_or_path: str,
                        revision: Optional[str] = DEFAULT_MODEL_REVISION,
                        cfg_dict: Config = None,
                        device: str = None,
                        **kwargs):
        """Instantiate a model from local directory or remote model repo. Note
        that when loading from remote, the model revision can be specified.

        Args:
            model_name_or_path(str): A model dir or a model id to be loaded
            revision(str, `optional`): The revision used when the model_name_or_path is
                a model id of the remote hub. default `master`.
            cfg_dict(Config, `optional`): An optional model config. If provided, it will replace
                the config read out of the `model_name_or_path`
            device(str, `optional`): The device to load the model.
            **kwargs:
                task(str, `optional`): The `Tasks` enumeration value to replace the task value
                read out of config in the `model_name_or_path`. This is useful when the model to be loaded is not
                equal to the model saved.
                For example, load a `backbone` into a `text-classification` model.
                Other kwargs will be directly fed into the `model` key, to replace the default configs.
        Returns:
            A model instance.

        Examples:
            >>> from modelscope.models import Model
            >>> Model.from_pretrained('damo/nlp_structbert_backbone_base_std', task='text-classification')
        """
        prefetched = kwargs.get('model_prefetched')
        if prefetched is not None:
            kwargs.pop('model_prefetched')

        if osp.exists(model_name_or_path):
            local_model_dir = model_name_or_path
        else:
            if prefetched is True:
                raise RuntimeError(
                    'Expecting model is pre-fetched locally, but is not found.'
                )
            local_model_dir = snapshot_download(model_name_or_path, revision)
        logger.info(f'initialize model from {local_model_dir}')
        if cfg_dict is not None:
            cfg = cfg_dict
        else:
            cfg = Config.from_file(
                osp.join(local_model_dir, ModelFile.CONFIGURATION))
        task_name = cfg.task
        if 'task' in kwargs:
            task_name = kwargs.pop('task')
        model_cfg = cfg.model
        if hasattr(model_cfg, 'model_type') and not hasattr(model_cfg, 'type'):
            model_cfg.type = model_cfg.model_type
        model_cfg.model_dir = local_model_dir
        for k, v in kwargs.items():
            model_cfg[k] = v
        if device is not None:
            model_cfg.device = device
            model = build_model(
                model_cfg, task_name=task_name, default_args=kwargs)
        else:
            model = build_model(
                model_cfg, task_name=task_name, default_args=kwargs)

        # dynamically add pipeline info to model for pipeline inference
        if hasattr(cfg, 'pipeline'):
            model.pipeline = cfg.pipeline

        if not hasattr(model, 'cfg'):
            model.cfg = cfg

        model.name = model_name_or_path
        return model

    def save_pretrained(self,
                        target_folder: Union[str, os.PathLike],
                        save_checkpoint_names: Union[str, List[str]] = None,
                        save_function: Callable = save_checkpoint,
                        config: Optional[dict] = None,
                        **kwargs):
        """save the pretrained model, its configuration and other related files to a directory,
            so that it can be re-loaded

        Args:
            target_folder (Union[str, os.PathLike]):
            Directory to which to save. Will be created if it doesn't exist.

            save_checkpoint_names (Union[str, List[str]]):
            The checkpoint names to be saved in the target_folder

            save_function (Callable, optional):
            The function to use to save the state dictionary.

            config (Optional[dict], optional):
            The config for the configuration.json, might not be identical with model.config

        """
        if config is None and hasattr(self, 'cfg'):
            config = self.cfg
        assert config is not None, 'Cannot save the model because the model config is empty.'
        if isinstance(config, Config):
            config = config.to_dict()
        if 'preprocessor' in config and config['preprocessor'] is not None:
            if 'mode' in config['preprocessor']:
                config['preprocessor']['mode'] = 'inference'
            elif 'val' in config['preprocessor'] and 'mode' in config[
                    'preprocessor']['val']:
                config['preprocessor']['val']['mode'] = 'inference'

        save_pretrained(self, target_folder, save_checkpoint_names,
                        save_function, config, **kwargs)
