# 🗺️ OnBid Arbitrage Master 시스템 지도 (SYSTEM_MAP)

## 1. 프로젝트 개요
온비드(공매) 데이터를 실시간 수집하여 **환금성 자산(전자기기, 명품, 귀금속, 상품권)**의 중고 시세 대비 차익을 분석하고 '무위험 수익' 매물을 추천하는 리셀링 투자 보조 시스템.

## 2. 기술 스택
- **Backend**: Python (FastAPI), SQLite3
- **Frontend**: Next.js (App Router), TailwindCSS
- **AI Engine (NVIDIA NIM)**: 
  - **Maverick & Flash**: `meta/llama-3.1-8b-instruct`로 모델 단일화.
  - 고속 배치 필터링 및 정밀 분석을 동일 모델로 수행하여 일관성 확보.
- **External API**: 온비드 공공데이터 API (동산 목록/상세)

## 3. AI 분석 파이프라인 (Funnel Architecture)
1. **Stage 0 (Rule-base Filter)**: 블랙리스트 키워드 필터링 및 텍스트 전처리.
2. **Stage 1 (Maverick Filtering)**: Llama 8B 배치 분석을 통한 고수익 후보군 선별.
3. **Stage 1.5 (Selective Classifier)**: 정규식 및 텍스트 분석을 통한 '단건' vs '일괄' vs '정보부족' 판별.
4. **Stage 2 (Deep Dive)**: 단건 매물 대상 심층 수익성 분석 및 한국어 리포트 생성 (보류 건은 API 호출 생략).

## 4. 핵심 데이터 로직
- **Selective Hold**: 분석 데이터가 부족하거나 일괄 매각 건은 `ai_difficulty = 'Hold'`로 분류하여 리포트 신뢰도 보호.
- **Financial Analysis**: `(추정 시장가 - (입찰가 + 부대비용)) = 예상 순수익` 기반의 보수적 스코어링.

## 5. 디렉토리 구조
- `/backend`: 수집 및 AI 분석 파이프라인
  - `collector.py`: 신규 매물 수집 및 상세 정보 사전 캐싱
  - `ai_analyzer.py`: Maverick -> Classifier -> Deep Dive 엔진
  - `export_data.py`: 프론트엔드용 JSON 익스포터
- `/frontend`: 리셀러 특화 대시보드 (SSG 아키텍처)
