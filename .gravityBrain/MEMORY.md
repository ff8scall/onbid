# 📝 작업 메모리 (MEMORY)

## 1. 최근 작업 완료 사항 (2026-05-03)
- **기준 미달 매물 분리**: 
  - `onbid_items` 테이블에 `is_substandard` 컬럼 추가.
  - 분석 점수 미달(60점 미만) 또는 비타겟 매물을 삭제하는 대신 플래그 처리하여 보관.
- **깔때기형 AI 파이프라인 (Funnel Architecture)**:
  - **Stage 1 (Maverick/NVIDIA)**: 50개 단위 배치 필터링 구현. 고수익 후보군(`is_maverick_selected`) 선별 로직 최적화.
  - **Stage 2 (Flash/Gemini)**: 정예 매물 대상 Deep Dive 정밀 분석 및 리스크 리포트 생성 기능 추가.
- **데이터베이스 및 API 고도화**:
  - `is_maverick_selected`, `ai_deep_dive_report` 컬럼 추가 및 마이그레이션 완료.
  - `/items/candidates` 엔드포인트 신설.
- **UI/UX 개선**:
  - 대시보드 3단계 탭(정예, 후보, 미달) UI 적용 및 카드 디자인 고도화.

## 2. 다음 작업 컨텍스트
- **자동화**: GitHub Actions를 통한 일일 2회 수집/분석 스케줄러 구축 (Phase 4).
- **시세 검증 고도화**: Flash 모델의 Tool Use(Search) 기능을 활용한 실시간 중고 시세 교차 검증 로직 구현.
- **멀티모달 확장**: 매물 사진(Thumbnails)을 Flash 모델로 분석하여 상태 및 구성품 정밀 판독.
