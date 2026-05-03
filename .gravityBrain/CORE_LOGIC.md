# 🧠 핵심 비즈니스 로직 (CORE_LOGIC)

## 1. 가치 중심 수집 로직 (`collector.py`)
- **감정평가액(Appraisal Value) 수집**: 온비드 API의 `apslEvlAmt` 필드를 정수형으로 변환하여 `apsl_evl_amt` 컬럼에 저장.
- **안정적 매핑**: `onbidPbancNo`를 상세 API의 `pbancMngNo`로 매핑하여 상세 설명 수집 성공률 확보.

## 2. AI 분석 파이프라인 (`ai_analyzer.py`)
- **Stage 1.5 (Selective Classifier)**: 
  - **가치 기반 분석 강행**: 귀금속(`sub_category == '귀금속'`) 또는 명품 카테고리이면서 `apsl_evl_amt > 0`인 경우, 상세 설명 텍스트가 짧아도 `MISSING` 판별을 생략하고 분석 진행.
- **Stage 2 (Deep Dive)**: 
  - **감정가 가이드라인**: AI 프롬프트에 `{appraisal_price}`를 주입하여, "감정가 대비 낙찰 시 이득"을 계산하도록 지시.
  - 금/보석류는 감정가를 시장 기준가로 삼아 2026년 시세 변동분을 반영하도록 유도.

## 3. 수익성 지표 및 점수
- **Investment Score**: `(시장가 / 최저입찰가)` 비율 및 `순수익` 절대 금액을 종합하여 0~100점 산출.
- **Hold 처리**: 일괄 매각(Bundle) 건은 여전히 분석 보류하여 리포트 품질 유지.
