# 🗺️ Pbid Hunter 시스템 지도 (SYSTEM_MAP)

## 1. 프로젝트 개요
온비드(공매) 데이터를 실시간으로 수집하여 IT 기기(노트북, 데스크톱, 모니터 등)의 가성비를 AI로 분석하고 최적의 매물을 추천하는 대시보드 시스템.

## 2. 기술 스택
- **Backend**: Python (FastAPI/Flask), SQLite3
- **Frontend**: Next.js (App Router), TailwindCSS
- **AI Engine**: Google Gemini 1.5 Flash (Fallback: Local Heuristic Engine)
- **External API**: 온비드 공공데이터 API (동산 목록, 이미지 정보 등)

## 3. 디렉토리 구조
- `/backend`: 데이터 수집, 분석, API 서버
  - `collector.py`: 온비드 실시간 매물 수집기
  - `ai_analyzer.py`: 매물 심층 분석 및 스코어링 엔진
  - `main.py`: 프론트엔드용 REST API 서버
  - `init_db.py`: DB 스키마 초기화 및 마이그레이션
- `/frontend`: 사용자 인터페이스
  - `src/app/page.tsx`: 실시간 큐레이션 대시보드
  - `src/app/items/[id]/page.tsx`: 매물 상세 및 AI 리포트 페이지
- `/data`: 데이터베이스 파일 (`pbid_local.db`)

## 4. 데이터 흐름
1. `collector.py` 실행 -> 온비드 API 호출 -> IT 관련 매물 필터링 및 DB 저장
2. `ai_analyzer.py` 실행 -> 미분석 매물 추출 -> AI(Gemini) 또는 로컬 룰을 통한 분석 -> DB 업데이트
3. `main.py` 서버 구동 -> 프론트엔드에서 API 호출 -> 대시보드 시각화
