# 낚시성 뉴스 기사 탐지 (Clickbait News Detector)

네이버 뉴스의 낚시성 기사를 탐지하는 Chrome 확장 프로그램입니다. BERT 모델을 활용하여 기사의 낚시성 여부를 분석합니다.

## 기능 소개

- 네이버 뉴스 기사의 낚시성 여부 실시간 분석
- 8개 카테고리 지원 (정치, 경제, 사회, 생활/문화, 세계, IT/과학, 스포츠, 연예)
- 분석 결과 공유 기능 (클립보드 복사, 트위터, 카카오톡)
- 직관적인 사용자 인터페이스

## 지원 도메인
- n.news.naver.com/article/*
- m.sports.naver.com/article/*
- entertain.naver.com/article/*


## 사용 방법

1. 네이버 뉴스 기사 페이지 방문
2. Chrome 확장 프로그램 아이콘 클릭
3. 기사 카테고리 선택
4. '분석하기' 버튼 클릭
5. 분석 결과 확인
6. 필요시 결과 공유 (복사, 트위터, 카카오톡)

## 기술 스택

- Frontend: HTML, CSS, JavaScript
- Backend: FastAPI, Python
- ML Model: BERT
- Chrome Extension API
- 데이터 크롤링: BeautifulSoup4

## API 엔드포인트

- `/BERT/detect`: 뉴스 기사 분석 API
  - Method: POST
  - Request Body:
    ```json
    {
        "url": "네이버 뉴스 URL",
        "category": "카테고리"
    }
    ```
  - Response:
    ```json
    {
        "prediction": "Fake/Not Fake",
        "prob": "확률",
        "title": "기사 제목",
        "content": "기사 내용",
        "press": "언론사",
        "date": "작성일",
        "reporter": "기자명",
        "email": "기자 이메일"
    }
    ```

## 개발자

- DY (doyooni303@snu.ac.kr)

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

## 참고사항

- 본 확장 프로그램은 연구 및 교육 목적으로 개발되었습니다.
- 정확한 분석을 위해 네이버 뉴스 기사 URL을 사용해주세요.
- 백엔드 서버가 실행 중이어야 분석이 가능합니다.

## 업데이트 내역

### Version 1.0.0
- 초기 버전 출시
- 기본 분석 기능 구현
- 공유 기능 추가

## 문의사항

버그 리포트나 기능 제안은 GitHub 이슈를 통해 남겨주세요.