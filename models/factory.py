import torch
from kobert_tokenizer import KoBERTTokenizer
from transformers import AutoTokenizer

from .registry import is_model, model_entrypoint


def create_tokenizer(name: str, **kwargs):
    if name == "bert":
        word_embed = None
        tokenizer = KoBERTTokenizer.from_pretrained("skt/kobert-base-v1")
    else:
        word_embed = None
        tokenizer = AutoTokenizer.from_pretrained(**kwargs)
    return tokenizer, word_embed


def create_model(
    modelname: str,
    hparams: dict,
    word_embed=None,
    tokenizer=None,
    freeze_word_embed: bool = False,
    use_pretrained_word_embed: bool = False,
    checkpoint_path: str = None,
    **kwargs
):

    if not is_model(modelname):
        raise RuntimeError("Unknown model (%s)" % modelname)

    create_fn = model_entrypoint(modelname)

    model = create_fn(hparams=hparams)

    # word embedding
    if use_pretrained_word_embed:
        model.init_w2e(word_embed, len(tokenizer.special_tokens))

    # freeze word embedding
    if freeze_word_embed:
        model.freeze_w2e()

    # load checkpoint weights
    if checkpoint_path:
        model.load_state_dict(torch.load(checkpoint_path))

    return model
