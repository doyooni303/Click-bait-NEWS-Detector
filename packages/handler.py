import yaml
import torch
from models import create_tokenizer, create_model


class ModelHandler:
    def __init__(self, yaml_path):
        self.yaml_cfg = yaml.load(open(yaml_path, "r"), Loader=yaml.FullLoader)

    def load_model(self):
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        print(device)

        # tokenizer
        tokenizer, word_embed = create_tokenizer(
            name=self.yaml_cfg["TOKENIZER"]["name"],
            vocab_path=self.yaml_cfg["TOKENIZER"].get("vocab_path", None),
            max_vocab_size=self.yaml_cfg["TOKENIZER"].get("max_vocab_size", None),
        )

        # Build Model
        model = create_model(
            modelname=self.yaml_cfg["MODEL"]["modelname"],
            hparams=self.yaml_cfg["MODEL"]["PARAMETERS"],
            word_embed=word_embed,
            tokenizer=tokenizer,
            freeze_word_embed=self.yaml_cfg["MODEL"].get("freeze_word_embed", False),
            use_pretrained_word_embed=self.yaml_cfg["MODEL"].get(
                "use_pretrained_word_embed", False
            ),
            checkpoint_path=self.yaml_cfg["MODEL"]["CHECKPOINT"]["checkpoint_path"],
        )
        model.to(device)
        return model, tokenizer, device


class DataHandler:
    def check_type(self, check_class, data):
        data = check_class(**data)

        return data
