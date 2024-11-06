from fastapi import APIRouter
import torch


from packages.config import DataInput, PredictOutput, ProjectConfig


# Project config 설정
project_config = ProjectConfig("BERT")
# 모델 가져오기
model, tokenizer, device = project_config.load_model()

model.eval()

bert = APIRouter(prefix="/BERT")


def convert_device(inputs: dict, device: str) -> dict:
    for k in inputs.keys():
        inputs[k] = inputs[k].to(device)

    return inputs


def preprocess(tokenizer, title, text) -> dict:
    if isinstance(title, tuple):
        title = title[0]
    if isinstance(text, list):
        src = " ".join([title] + text)
    else:
        src = " ".join([title, text])
    doc = tokenizer(
        text=src,
        truncation=True,
        max_length=project_config.yaml_cfg["TOKENIZER"]["max_word_len"],
        padding="max_length",
        return_tensors="pt",
    )
    return doc


# router 마다 경로 설정
@bert.get("/", tags=["BERT"])
async def start_ncf():
    return {"msg": "Here is BERT"}


@bert.post("/predict", tags=["BERT"], response_model=PredictOutput)
async def ncf_predict(data_request: DataInput):
    title = data_request.title
    content = data_request.content
    doc = preprocess(tokenizer, title, content)
    doc = convert_device(doc, device)
    outputs = model(**doc)
    outputs = torch.nn.functional.softmax(outputs, dim=1).cpu()
    pred = outputs.argmax(dim=1)  # 비낚시성 = 1, 낚시성 = 0
    prob = outputs[pred]

    prediction = "Fake" if pred == 0 else "Not Fake"

    return {"prob": prob * 100, "prediction": prediction}
