# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel

# from fastapi import APIRouter
# import torch

# from packages.crawling import crawl, URLExtractor
# from packages.config import ProjectConfig


# class Request(BaseModel):
#     url: str
#     category: str


# # Project config 설정
# project_config = ProjectConfig("BERT")

# # 모델 가져오기
# model, tokenizer, device = project_config.load_model()

# model.eval()

# bert = APIRouter(prefix="/BERT")


# def convert_device(inputs: dict, device: str) -> dict:
#     for k in inputs.keys():
#         inputs[k] = inputs[k].to(device)

#     return inputs


# def preprocess(tokenizer, title, text) -> dict:
#     if isinstance(title, tuple):
#         title = title[0]
#     if isinstance(text, list):
#         src = " ".join([title] + text)
#     else:
#         src = " ".join([title, text])
#     doc = tokenizer(
#         text=src,
#         truncation=True,
#         max_length=project_config.yaml_cfg["TOKENIZER"]["max_word_len"],
#         padding="max_length",
#         return_tensors="pt",
#     )
#     return doc


# # router 마다 경로 설정
# @bert.get("/home", tags=["BERT"])
# async def start_bert():
#     return "Welcome to BERT world!"


# @bert.post("/detect")
# async def bert_predict(request: Request):
#     try:
#         # First try to crawl
#         # try:
#         info = crawl(request.url, request.category)

#         if not info or "title" not in info:
#             raise HTTPException(
#                 status_code=400,
#                 detail="뉴스를 찾을 수 없습니다. URL을 확인해주세요.",
#             )

#         try:
#             doc = preprocess(tokenizer, info["title"], info["content"])
#             doc = convert_device(doc, device)
#             outputs = model(**doc)
#             outputs = torch.nn.functional.softmax(outputs, dim=1).cpu().squeeze()
#             pred = outputs.argmax()
#             prediction = "불일치" if pred == 0 else "일치"
#             prob = 100 - round(outputs[0].item() * 100, 2)

#             del doc
#             torch.cuda.empty_cache()

#             # Generate summary
#             # summary = await generate_summary(info["title"], info["content"])

#             return {
#                 "prob": f"{prob}%",
#                 "prediction": prediction,
#                 "title": info["title"],
#                 "content": info["content"],
#                 "press": info["press"],
#                 "date": info["date"],
#                 "reporter": info["reporter"],
#                 "email": info["email"],
#             }
#         except Exception as e:
#             raise HTTPException(
#                 status_code=500,
#                 detail="분석 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
#             )

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import torch
import torch.nn.functional as F
import logging

from packages.crawling import crawl, URLExtractor
from packages.config import ProjectConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Request(BaseModel):
    url: str
    category: str


class URLRequest(BaseModel):
    url: str


class NewsResponse(BaseModel):
    prob: str
    prediction: str
    title: str
    content: str
    press: str
    date: str
    reporter: str
    email: str


class URLResponse(BaseModel):
    urls: List[str]


class BERTAnalyzer:
    def __init__(self, project_name: str = "BERT"):
        self.project_config = ProjectConfig(project_name)
        self.model, self.tokenizer, self.device = self.project_config.load_model()
        self.model.eval()

    def convert_device(
        self, inputs: Dict[str, torch.Tensor], device: str
    ) -> Dict[str, torch.Tensor]:
        """Convert inputs to specified device."""
        return {k: v.to(device) for k, v in inputs.items()}

    def preprocess(self, title: str, text: str) -> Dict[str, torch.Tensor]:
        """Preprocess input text for BERT model."""
        if isinstance(title, tuple):
            title = title[0]
        if isinstance(text, list):
            src = " ".join([title] + text)
        else:
            src = " ".join([title, text])

        inputs = self.tokenizer(
            src,
            truncation=True,
            max_length=self.project_config.yaml_cfg["TOKENIZER"]["max_word_len"],
            padding="max_length",
            return_tensors="pt",
        )
        return inputs

    async def analyze_news(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze news content using BERT model."""
        try:
            doc = self.preprocess(info["title"], info["content"])
            doc = self.convert_device(doc, self.device)

            outputs = self.model(
                **doc
                # input_ids=doc["input_ids"], attention_mask=doc["attention_mask"]
            )
            outputs = F.softmax(outputs, dim=1).cpu().squeeze()
            pred = outputs.argmax()

            prediction = "불일치" if pred == 0 else "일치"
            prob = 100 - round(outputs[0].item() * 100, 2)

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
            logger.error(f"Error in analyze_news: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="분석 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
            )


# Initialize BERT analyzer
bert_analyzer = BERTAnalyzer()

# Initialize FastAPI router
bert = APIRouter(prefix="/BERT")


@bert.get("/home", tags=["BERT"])
async def start_bert():
    """Health check endpoint."""
    return "Welcome to BERT world!"


@bert.post("/extract-urls", response_model=URLResponse)
async def extract_news_urls(request: URLRequest):
    """Extract news URLs from a given page."""
    try:
        extractor = URLExtractor(browser_type="chrome")

        urls = extractor.extract_urls(request.url, count_clicks=3)
        logger.info(f"Successfully extracted {len(urls)} URLs")
        return {"urls": urls}

    except Exception as e:
        logger.error(f"Error in URL extraction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@bert.post("/detect", response_model=NewsResponse)
async def bert_predict(request: Request):
    """Analyze news content for click-bait detection."""
    try:
        logger.info(f"Received analysis request: {request}")

        # Crawl news content
        info = crawl(request.url, request.category)

        # Crawl news content
        # info = crawl(request.url, request.category)

        if not info or "title" not in info:
            logger.error(f"Failed to crawl news from URL: {request.url}")
            raise HTTPException(
                status_code=400,
                detail="뉴스를 찾을 수 없습니다. URL을 확인해주세요.",
            )

        # Analyze news content
        result = await bert_analyzer.analyze_news(info)
        # logger.info(f"BERT analysis result: {result}")
        return result

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Unexpected error in bert_predict: {str(e)}")
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")
