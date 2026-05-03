# 🗺️ OnBid AI Curation Master 전략 지도 (STRATEGY_MAP v4.0)

## 1. 비즈니스 방향성 (Business Model)
- **가치 제안 (Value Proposition)**: "공매(온비드) 시장에서 무위험 차익(Arbitrage)이 가능한 실물 자산만을 선별하여, 리셀러와 일반인에게 가장 빠른 환금성과 확실한 마진을 보장하는 대시보드 제공"
- **핵심 타겟**: 중고거래 리셀러, 앱테크족, 소액 투자자
- **수익화 전략**: 
  - (Phase 1) 트래픽 확보: 고마진 알짜 매물 실시간 중계로 MAU 극대화
  - (Phase 2) 프리미엄 구독: 알림 기능(특정 지역/카테고리 '직접 수령' 급매물 핑) 유료화

## 2. 타겟팅 및 필터링 정책
1. **타겟 자산군 (환금성 최상)**
   - 최신 전자기기 (미개봉 애플 제품, 하이엔드 PC)
   - 명품 (가방, 시계 - 롤렉스, 샤넬 등)
   - 귀금속 (순금, 14K, 18K, 골드바 등)
   - 상품권 (백화점, 기프트카드 등 액면가 할인율 5% 이상)
2. **배제 대상 (Noise Cut)**
   - 자동차(이륜차 포함), 토지, 상가, 산업용 폐기물
   - iCloud 락, 비밀번호 분실 기기, 심각한 파손 기기
   - 마진율 15% 미만으로 수지타산이 맞지 않는 매물

## 3. 시스템 파이프라인
1. **수집 (Collector)**: `collector.py`가 확장된 키워드(명품, 귀금속 등)로 온비드 API 검색
2. **필터링 및 분석 (AI Analyzer)**: `ai_analyzer.py`가 Gemini 1.5 Pro/Flash 모델의 시스템 프롬프트(v4.0)를 통해 JSON 기반 정밀 마진 분석
3. **가비지 컬렉터 (Garbage Collection)**: AI 판단 결과 `is_target_item=false` 이거나 `investment_score < 60`인 쓰레기 매물은 DB 저장 생략 (서버 최적화)
4. **전시 (Frontend)**: Next.js 기반 UI에서 **'예상 수익금(expected_profit_krw)'**을 최상단 우선순위로 노출

## 4. 핵심 지표 (North Star Metric)
- **사용자당 일일 확인 매물 수 (Daily Items Viewed per User)**
- **알림 구독 전환율 (Notification Subscription Rate)**
