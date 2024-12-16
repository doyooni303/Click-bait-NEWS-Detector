# 뉴스 기사 제목-본문 간 일치성 검사기

## 개요
본 프로젝트는 네이버 뉴스 기사의 제목과 본문 내용의 일치성을 자동으로 검사하는 Chrome 확장 프로그램입니다. BERT 모델을 활용하여 제목과 본문의 의미적 연관성을 분석하고, 실시간으로 결과를 제공합니다.

## 설치 방법

### 필수 요구사항
- Python 3.8 이상
- Chrome 브라우저
- CUDA 지원 GPU (선택사항)

### 백엔드 설치
1. 저장소 클론
```bash
git clone https://github.com/doyooni303/Click-bait-NEWS-Detector.git
```

2. 도커 이미지 및 컨테이너 설치
```
cd docker
docker build . -t [이미지 이름]

<이미지 설치 후 컨테이너 생성>
docker run --gpus all -it \
	-u 0 \
	-p {port1}:{port2} \
	--ipc=host \
	--name {container_name} \
	-v {로컬 위치}:{작업 위치} \
   {image_name}

```

3. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

4. 크롬 드라이버 설치
- 크롬 정보 확인 [chrome://settings/help](chrome://settings/help)
- 크롬 버젼 및 os에 따른 드라이버 선택 후 설치 [https://googlechromelabs.github.io/chrome-for-testing/](https://googlechromelabs.github.io/chrome-for-testing/)
- 압축 파일 풀기


5. 서버 실행
- 4.에서 압축 해제한 폴더 경로를 `./packages/crawling.py`내 `set_chromedriver` 함수의 인자로 변경
```bash
python main.py
```

### Chrome 확장 프로그램 설치
1. `extension` 폴더를 로컬 저장소에 다운로드
2. Chrome 브라우저에서 `chrome://extensions` 접속
3. 우측 상단의 '개발자 모드' 활성화
4. '압축해제된 확장 프로그램을 로드합니다' 클릭
5. 1.에서 다운로드한 경로로 탐색

## 사용 방법
1. 네이버 뉴스 섹션 페이지 접속 (지원 카테고리: 정치, 경제, 사회, 생활/문화, IT/과학, 세계)
2. Chrome 확장 프로그램 아이콘 클릭
3. '검사 시작' 버튼 클릭
4. 분석이 완료된 뉴스 기사에 마우스를 올려 일치성 결과 확인

## 주요 기능
- 실시간 제목-본문 일치성 분석
- 진행률 표시
- 각 기사별 일치율 시각화
- 분석 중단 및 재시작 기능

## 프로젝트 구조
```
.
├── extension/              # Chrome 확장 프로그램 파일
├── models/                 # BERT 모델 관련 파일
├── packages/              # 백엔드 패키지
├── static/               # 백엔드 정적 파일
└── templates/            # 백엔드 HTML 템플릿
```

## 기술 스택
### 백엔드
- FastAPI
- PyTorch
- Selenium
- BERT

### 프론트엔드
- JavaScript
- Chrome Extension API
- HTML/CSS

## API 엔드포인트
- `/BERT/detect`: 뉴스 기사 분석
- `/BERT/extract-urls`: 뉴스 URL 추출

## 개발자 정보
### 백엔드 개발
- Python 3.8 이상 필요
- CUDA 호환 GPU 권장
- `.env` 파일에 환경 변수 설정 필요

### 확장 프로그램 개발
- Chrome 확장 프로그램 개발자 모드 필요
- `manifest.json` 설정 확인
- 개발자 도구를 통한 디버깅 가능

## 주의사항
- 네이버 뉴스 페이지 구조 변경 시 크롤링 기능이 영향을 받을 수 있음
- GPU 메모리 사용량 고려 필요
- 네트워크 상태에 따른 성능 차이 발생 가능

## 라이선스
[라이선스 정보 추가 필요]

## 문의사항
doyooni303@snu.ac.kr

---
※ 본 프로젝트는 지속적으로 업데이트될 예정입니다.

추가나 수정이 필요한 부분이 있으시다면 말씀해 주세요!