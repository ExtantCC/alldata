# Copyright (c) Alibaba, Inc. and its affiliates.
import os
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any, Dict, Optional, Sequence

from modelscope.metainfo import Models, Preprocessors
from modelscope.utils.config import Config, ConfigDict
from modelscope.utils.constant import DEFAULT_MODEL_REVISION, ModeKeys, Tasks
from modelscope.utils.hub import read_config, snapshot_download
from modelscope.utils.logger import get_logger
from .builder import build_preprocessor

logger = get_logger(__name__)

PREPROCESSOR_MAP = {
    # nlp
    # bart
    (Models.bart, Tasks.text_error_correction):
    Preprocessors.text_error_correction,

    # bert
    (Models.bert, Tasks.backbone):
    Preprocessors.sen_cls_tokenizer,
    (Models.bert, Tasks.document_segmentation):
    Preprocessors.document_segmentation,
    (Models.bert, Tasks.fill_mask):
    Preprocessors.fill_mask,
    (Models.bert, Tasks.sentence_embedding):
    Preprocessors.sentence_embedding,
    (Models.bert, Tasks.text_classification):
    Preprocessors.sen_cls_tokenizer,
    (Models.bert, Tasks.nli):
    Preprocessors.sen_cls_tokenizer,
    (Models.bert, Tasks.sentiment_classification):
    Preprocessors.sen_cls_tokenizer,
    (Models.bert, Tasks.sentence_similarity):
    Preprocessors.sen_cls_tokenizer,
    (Models.bert, Tasks.zero_shot_classification):
    Preprocessors.sen_cls_tokenizer,
    (Models.bert, Tasks.text_ranking):
    Preprocessors.text_ranking,
    (Models.bert, Tasks.part_of_speech):
    Preprocessors.token_cls_tokenizer,
    (Models.bert, Tasks.token_classification):
    Preprocessors.token_cls_tokenizer,
    (Models.bert, Tasks.word_segmentation):
    Preprocessors.token_cls_tokenizer,

    # bloom
    (Models.bloom, Tasks.backbone):
    Preprocessors.text_gen_tokenizer,

    # gpt_neo
    # gpt_neo may have different preprocessors, but now only one
    (Models.gpt_neo, Tasks.backbone):
    Preprocessors.sentence_piece,

    # gpt3 has different preprocessors by different sizes of models, so they are not listed here.

    # palm_v2
    (Models.palm, Tasks.backbone):
    Preprocessors.text_gen_tokenizer,

    # T5
    (Models.T5, Tasks.backbone):
    Preprocessors.text2text_gen_preprocessor,
    (Models.T5, Tasks.text2text_generation):
    Preprocessors.text2text_gen_preprocessor,

    # deberta_v2
    (Models.deberta_v2, Tasks.backbone):
    Preprocessors.sen_cls_tokenizer,
    (Models.deberta_v2, Tasks.fill_mask):
    Preprocessors.fill_mask,

    # ponet
    (Models.ponet, Tasks.fill_mask):
    Preprocessors.fill_mask_ponet,

    # structbert
    (Models.structbert, Tasks.backbone):
    Preprocessors.sen_cls_tokenizer,
    (Models.structbert, Tasks.fill_mask):
    Preprocessors.fill_mask,
    (Models.structbert, Tasks.faq_question_answering):
    Preprocessors.faq_question_answering_preprocessor,
    (Models.structbert, Tasks.text_classification):
    Preprocessors.sen_cls_tokenizer,
    (Models.structbert, Tasks.nli):
    Preprocessors.sen_cls_tokenizer,
    (Models.structbert, Tasks.sentiment_classification):
    Preprocessors.sen_cls_tokenizer,
    (Models.structbert, Tasks.sentence_similarity):
    Preprocessors.sen_cls_tokenizer,
    (Models.structbert, Tasks.zero_shot_classification):
    Preprocessors.sen_cls_tokenizer,
    (Models.structbert, Tasks.part_of_speech):
    Preprocessors.token_cls_tokenizer,
    (Models.structbert, Tasks.token_classification):
    Preprocessors.token_cls_tokenizer,
    (Models.structbert, Tasks.word_segmentation):
    Preprocessors.token_cls_tokenizer,

    # veco
    (Models.veco, Tasks.backbone):
    Preprocessors.sen_cls_tokenizer,
    (Models.veco, Tasks.fill_mask):
    Preprocessors.fill_mask,
    (Models.veco, Tasks.text_classification):
    Preprocessors.sen_cls_tokenizer,
    (Models.veco, Tasks.nli):
    Preprocessors.sen_cls_tokenizer,
    (Models.veco, Tasks.sentiment_classification):
    Preprocessors.sen_cls_tokenizer,
    (Models.veco, Tasks.sentence_similarity):
    Preprocessors.sen_cls_tokenizer,

    # space
}


class Preprocessor(ABC):

    def __init__(self, mode=ModeKeys.INFERENCE, *args, **kwargs):
        self._mode = mode
        self.device = int(
            os.environ['LOCAL_RANK']) if 'LOCAL_RANK' in os.environ else None
        pass

    @abstractmethod
    def __call__(self, data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        self._mode = value

    @classmethod
    def from_pretrained(cls,
                        model_name_or_path: str,
                        revision: Optional[str] = DEFAULT_MODEL_REVISION,
                        cfg_dict: Config = None,
                        preprocessor_mode=ModeKeys.INFERENCE,
                        **kwargs):
        """Instantiate a preprocessor from local directory or remote model repo. Note
        that when loading from remote, the model revision can be specified.

        Args:
            model_name_or_path(str): A model dir or a model id used to load the preprocessor out.
            revision(str, `optional`): The revision used when the model_name_or_path is
                a model id of the remote hub. default `master`.
            cfg_dict(Config, `optional`): An optional config. If provided, it will replace
                the config read out of the `model_name_or_path`
            preprocessor_mode(str, `optional`): Specify the working mode of the preprocessor, can be `train`, `eval`,
                or `inference`. Default value `inference`.
                The preprocessor field in the config may contain two sub preprocessors:
                >>> {
                >>>     "train": {
                >>>         "type": "some-train-preprocessor"
                >>>     },
                >>>     "val": {
                >>>         "type": "some-eval-preprocessor"
                >>>     }
                >>> }
                In this scenario, the `train` preprocessor will be loaded in the `train` mode, the `val` preprocessor
                will be loaded in the `eval` or `inference` mode. The `mode` field in the preprocessor class
                will be assigned in all the modes.
                Or just one:
                >>> {
                >>>     "type": "some-train-preprocessor"
                >>> }
                In this scenario, the sole preprocessor will be loaded in all the modes,
                and the `mode` field in the preprocessor class will be assigned.

            **kwargs:
                task(str, `optional`): The `Tasks` enumeration value to replace the task value
                read out of config in the `model_name_or_path`.
                This is useful when the preprocessor does not have a `type` field and the task to be used is not
                equal to the task of which the model is saved.
                Other kwargs will be directly fed into the preprocessor, to replace the default configs.

        Returns:
            The preprocessor instance.

        Examples:
            >>> from modelscope.preprocessors import Preprocessor
            >>> Preprocessor.from_pretrained('damo/nlp_debertav2_fill-mask_chinese-base')

        """
        if not os.path.exists(model_name_or_path):
            model_dir = snapshot_download(
                model_name_or_path, revision=revision)
        else:
            model_dir = model_name_or_path
        if cfg_dict is None:
            cfg = read_config(model_dir)
        else:
            cfg = cfg_dict
        task = cfg.task
        if 'task' in kwargs:
            task = kwargs.pop('task')
        field_name = Tasks.find_field_by_task(task)
        if 'field' in kwargs:
            field_name = kwargs.pop('field')
        sub_key = 'train' if preprocessor_mode == ModeKeys.TRAIN else 'val'

        if not hasattr(cfg, 'preprocessor') or len(cfg.preprocessor) == 0:
            logger.warn('No preprocessor field found in cfg.')
            preprocessor_cfg = ConfigDict()
        else:
            preprocessor_cfg = cfg.preprocessor

        if 'type' not in preprocessor_cfg:
            if sub_key in preprocessor_cfg:
                sub_cfg = getattr(preprocessor_cfg, sub_key)
            else:
                logger.warn(f'No {sub_key} key and type key found in '
                            f'preprocessor domain of configuration.json file.')
                sub_cfg = preprocessor_cfg
        else:
            sub_cfg = preprocessor_cfg

        sub_cfg.update({'model_dir': model_dir})
        sub_cfg.update(kwargs)
        if 'type' in sub_cfg:
            if isinstance(sub_cfg, Sequence):
                # TODO: for Sequence, need adapt to `mode` and `mode_dir` args,
                # and add mode for Compose or other plans
                raise NotImplementedError('Not supported yet!')
            sub_cfg = deepcopy(sub_cfg)

            preprocessor = build_preprocessor(sub_cfg, field_name)
        else:
            logger.warn(
                f'Cannot find available config to build preprocessor at mode {preprocessor_mode}, '
                f'current config: {sub_cfg}. trying to build by task and model information.'
            )
            model_cfg = getattr(cfg, 'model', ConfigDict())
            model_type = model_cfg.type if hasattr(
                model_cfg, 'type') else getattr(model_cfg, 'model_type', None)
            if task is None or model_type is None:
                logger.warn(
                    f'Find task: {task}, model type: {model_type}. '
                    f'Insufficient information to build preprocessor, skip building preprocessor'
                )
                return None
            if (model_type, task) not in PREPROCESSOR_MAP:
                logger.warn(
                    f'No preprocessor key {(model_type, task)} found in PREPROCESSOR_MAP, '
                    f'skip building preprocessor.')
                return None

            sub_cfg = ConfigDict({
                'type': PREPROCESSOR_MAP[(model_type, task)],
                **sub_cfg
            })
            preprocessor = build_preprocessor(sub_cfg, field_name)
        preprocessor.mode = preprocessor_mode
        return preprocessor
