# 🗺️ OnBid Arbitrage Master 시스템 지도 (SYSTEM_MAP)

## 1. 프로젝트 개요
온비드(공매) 데이터를 실시간 수집하여 **환금성 자산(전자기기, 명품, 귀금속, 상품권)**의 중고 시세 대비 차익을 분석하고 '무위험 수익' 매물을 추천하는 리셀링 투자 보조 시스템.

## 2. 기술 스택
- **Backend**: Python (FastAPI), SQLite3
- **Frontend**: Next.js (App Router), TailwindCSS
- **AI Engine**: 
  - **Maverick (NVIDIA NIM)**: Stage 1 광역 필터링 (`meta/llama-3.1-8b-instruct`)
  - **Flash (NVIDIA NIM)**: Stage 2 정밀 분석 (`stepfun-ai/step-3.5-flash`)
- **External API**: 온비드 공공데이터 API (동산 목록/상세)

## 3. AI 분석 파이프라인 (Funnel Architecture)
1. **Stage 0 (Rule-base)**: 블랙리스트 키워드 필터링 및 텍스트 전처리(HTML 제거).
2. **Stage 1 (Maverick)**: 50개 단위 배치 처리로 고수익 후보군(is_maverick_selected) 선별.
3. **Stage 2 (Flash)**: 선별된 정예 매물 대상 정밀 분석 및 외부 시세 검증 리포트 생성.

## 4. 핵심 데이터 로직
- **Arbitrage Calculation**: `(추정 시장가 - 최저입찰가) = 예상 수익금`
- **Filtering**: 투자 점수 60점 미만 또는 비타겟 매물은 `is_substandard` 플래그 보관.

## 5. 디렉토리 구조
- `/backend`: 수집 및 AI 분석 파이프라인
  - `collector.py`: 타겟 키워드 기반 매물 수집기
  - `ai_analyzer.py`: Maverick -> Flash 깔때기 분석 엔진
  - `main.py`: 수익성 데이터 서빙 API
- `/frontend`: 리셀러 특화 대시보드
  - `src/app/page.tsx`: 정예/후보/미달 탭 기반 큐레이션 보드
