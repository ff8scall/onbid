# 🧠 핵심 비즈니스 로직 (CORE_LOGIC)

## 1. 가치 중심 수집 로직 (`collector.py`)
- **감정평가액(Appraisal Value) 수집**: 온비드 API의 `apslEvlAmt` 필드를 정수형으로 변환하여 `apsl_evl_amt` 컬럼에 저장.
- **안정적 매핑**: `onbidPbancNo`를 상세 API의 `pbancMngNo`로 매핑하여 상세 설명 수집 성공률 확보.
- **중복 처리 및 Upsert (New)**: `UNIQUE(cltr_mng_no)` 제약을 활용하여 동일 물건의 중복 저장을 방지. 재경매나 유찰로 인해 공고번호(`pbanc_mng_no`)가 바뀌더라도 동일 물건(`cltr_mng_no`)이라면 기존 데이터를 업데이트(Upsert)함. 최저입찰가(`min_bid_prc`)가 변경된 경우에만 `is_ai_processed`를 0으로 초기화하여 재분석을 유도.

## 2. AI 분석 파이프라인 (`ai_analyzer.py`)
- **Stage 1.5 (Selective Classifier)**: 
  - **가치 기반 분석 강행**: 귀금속 또는 명품 카테고리이면서 `apsl_evl_amt > 0`인 경우, 상세 설명 텍스트가 짧아도 분석 진행.
- **Stage 2 (Deep Dive)**: 
  - **손익분기점(Break-even) 분석**: `Estimated Market Price - Est. Costs`를 통해 손익분기점을 산출.
  - **수수료 및 부대비용 반영**: 배송비, 감정비, 수리비, 세금 등을 보수적으로 책정하여 순수익 계산.
  - **자동 필터링**: 최저입찰가가 손익분기점을 초과하거나 마진이 10% 미만인 경우 `Substandard`로 자동 분류.
  - **보석/IT 특화**: 보석류는 감정가를, IT 기기는 사양별 실거래가를 우선 지표로 활용.
- **차액 발생 근거(Price Gap) 분석 (New)**: 단순 마진 계산을 넘어, 왜 해당 매물이 시세 대비 저렴하게 낙찰될 가능성이 있는지(인지도 부족, 특정 브랜드 프리미엄, 시장 트렌드 등)에 대한 구체적인 사유를 추출하여 보고서에 포함.

## 3. 수익성 지표 및 점수
- **Investment Score**: 손익분기점 대비 입찰가율을 핵심 점수 지표로 사용. (마진 20% 이상 시 85점 이상 부여)
- **Hold 처리**: 일괄 매각(Bundle) 건은 첨부파일 판독 불가로 인해 여전히 분석 보류.
