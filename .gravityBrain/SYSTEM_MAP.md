# 🗺️ OnBid Arbitrage Master 시스템 지도 (SYSTEM_MAP)

## 1. 프로젝트 개요
온비드(공매) 데이터를 실시간 수집하여 **환금성 자산(전자기기, 명품, 귀금속, 상품권)**의 중고 시세 대비 차익을 분석하고 '무위험 수익' 매물을 추천하는 리셀링 투자 보조 시스템.

## 2. 기술 스택
- **Backend**: Python (FastAPI), SQLite3
- **Frontend**: Next.js (App Router), TailwindCSS
- **AI Engine (NVIDIA NIM)**: 
  - **Maverick & Flash**: `meta/llama-3.1-8b-instruct`로 모델 단일화.
- **External API**: 온비드 공공데이터 API (동산 목록/상세)

## 3. AI 분석 파이프라인 (Funnel Architecture)
1. **Stage 0 (Rule-base Filter)**: 블랙리스트 키워드 필터링 및 텍스트 전처리.
2. **Stage 1 (Maverick Filtering)**: Llama 8B 배치 분석을 통한 고수익 후보군 선별.
3. **Stage 1.5 (Selective Classifier)**: 
    - 일괄 매각(Bundle) 탐지.
    - 상세 정보 부족 탐지 (**단, 귀금속/명품 등 고가치 자산은 감정평가액이 있을 경우 분석 강행**).
4. **Stage 2 (Deep Dive)**: 감정평가액 및 상세 텍스트 기반 심층 수익성 분석.

## 4. 핵심 데이터 로직
- **Appraisal-based Valuation**: 텍스트가 부실하더라도 전문가 감정가(`apsl_evl_amt`)가 존재하면 이를 제1 지표로 삼아 수익성 산출.
- **Financial Analysis**: `(추정 시장가 - (입찰가 + 부대비용)) = 예상 순수익` 기반의 보수적 스코어링.

## 5. 디렉토리 구조
- `/backend`: 수집 및 AI 분석 파이프라인
  - `collector.py`: 감정가 포함 매물 수집 및 상세 정보 사전 캐싱
  - `ai_analyzer.py`: 가치 기반 판별 및 심층 분석 엔진
- `/frontend`: 리셀러 특화 대시보드
