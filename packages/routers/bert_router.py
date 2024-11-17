from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from fastapi import APIRouter
import torch

from packages.crawling import crawl
from packages.config import PredictOutput, ProjectConfig


class Request(BaseModel):
    url: str
    category: str


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
@bert.get("/home", tags=["BERT"])
async def start_bert():
    return "Welcome to BERT world!"


# @bert.post("/detect", tags=["BERT"], response_model=PredictOutput)
# async def bert_predict(url: str, category: str):
#     info = crawl(url, category)
#     doc = preprocess(tokenizer, info["title"], info["content"])
#     doc = convert_device(doc, device)
#     outputs = model(**doc)
#     outputs = torch.nn.functional.softmax(outputs, dim=1).cpu().squeeze()
#     pred = outputs.argmax()  # 비낚시성 = 1, 낚시성 = 0
#     prediction = "Fake" if pred == 0 else "Not Fake"
#     prob = round(outputs[0].item() * 100, 2)

#     del doc
#     torch.cuda.empty_cache()

#     return {
#         "prob": f"{prob}%",
#         "prediction": prediction,
#         "title": info["title"],
#         "content": info["content"],
#         "press": info["press"],
#         "date": info["date"],
#         "reporter": info["reporter"],
#         "email": info["email"],
#     }


# @bert.post("/detect")
# async def bert_predict(request: Request):
#     try:
#         info = crawl(request.url, request.category)
#         doc = preprocess(tokenizer, info["title"], info["content"])
#         doc = convert_device(doc, device)
#         outputs = model(**doc)
#         outputs = torch.nn.functional.softmax(outputs, dim=1).cpu().squeeze()
#         pred = outputs.argmax()
#         prediction = "Fake" if pred == 0 else "Not Fake"
#         prob = round(outputs[0].item() * 100, 2)

#         del doc
#         torch.cuda.empty_cache()


#         return {
#             "prob": f"{prob}%",
#             "prediction": prediction,
#             "title": info["title"],
#             "content": info["content"],
#             "press": info["press"],
#             "date": info["date"],
#             "reporter": info["reporter"],
#             "email": info["email"],
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
@bert.post("/detect")
async def bert_predict(request: Request):
    try:
        # First try to crawl
        # try:
        info = crawl(request.url, request.category)

        if not info or "title" not in info:
            raise HTTPException(
                status_code=400,
                detail="뉴스를 찾을 수 없습니다. URL을 확인해주세요.",
            )
        # except Exception as e:
        #     raise HTTPException(
        #         status_code=400,
        #         detail="크롤링 중 오류가 발생했습니다. URL이 올바른지 확인해주세요.",
        #     )

        # Then process with BERT
        try:
            doc = preprocess(tokenizer, info["title"], info["content"])
            doc = convert_device(doc, device)
            outputs = model(**doc)
            outputs = torch.nn.functional.softmax(outputs, dim=1).cpu().squeeze()
            pred = outputs.argmax()
            prediction = "Fake" if pred == 0 else "Not Fake"
            prob = round(outputs[0].item() * 100, 2)

            del doc
            torch.cuda.empty_cache()

            return {
                "prob": f"{prob}%",
                "prediction": prediction,
                "title": info["title"],
                "content": info["content"],
                "press": info["press"],
                "date": info["date"],
                "reporter": info["reporter"],
                "email": info["email"],
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail="분석 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
