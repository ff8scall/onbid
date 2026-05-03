# 📝 작업 메모리 (MEMORY)

## 1. 최근 작업 완료 사항 (2026-05-03)
- **기준 미달 매물 분리**: 
  - `onbid_items` 테이블에 `is_substandard` 컬럼 추가.
  - 분석 점수 미달(60점 미만) 또는 비타겟 매물을 삭제하는 대신 플래그 처리하여 보관.
- **SSG(정적 사이트 생성) 아키텍처 전환**:
  - `items.json` 기반 데이터 관리로 변경하여 서버 비용 0원 달성.
  - `generateStaticParams`를 통한 매물별 HTML 사전 생성으로 SEO 최적화 완료.
  - 상세 페이지마다 고유한 메타데이터(Title, Description) 적용.
- **배포 파이프라인 구축**:
  - `npm run deploy` 명령어로 데이터 익스포트부터 빌드까지 자동화.
  - Vercel 배포 시 백엔드 없이 프론트엔드만으로 운영 가능하도록 설계.

## 2. 다음 작업 컨텍스트
- **Vercel 실제 배포**: Git Push를 통한 Vercel 라이브 배포 및 도메인 연결.
- **데이터 자동 갱신**: GitHub Actions를 활용해 주기적으로 수집 스케줄러를 돌리고 JSON을 커밋/푸시하는 자동 빌드 워크플로우 구축.
- **검색 엔진 등록**: Google Search Console 및 네이버 서치어드바이저에 사이트맵(sitemap.xml) 제출.
