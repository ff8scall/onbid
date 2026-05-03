import itemsData from "@/data/items.json";
import Link from "next/link";
import { notFound } from "next/navigation";

interface OnbidItem {
  id: number;
  pbanc_mng_no: string;
  cltr_mng_no: string;
  onbid_cltr_nm: string;
  cltr_adr: string;
  min_bid_prc: number | string;
  sub_category: string;
  thumb_url?: string;
  created_at: string;
  raw_data: any;
  ai_score?: number;
  ai_expected_profit?: number;
  ai_margin_percent?: number;
  ai_pickup_method?: string;
  ai_difficulty?: string;
  ai_curator_comment?: string;
  ai_resale_value?: number;
  ai_risk_factor?: string;
  is_ai_processed?: number;
}

// 모든 매물 ID에 대한 정적 경로 생성
export async function generateStaticParams() {
  const allItems = [
    ...itemsData.target,
    ...itemsData.candidate,
    ...itemsData.substandard
  ];
  return allItems.map((item) => ({
    id: item.id.toString(),
  }));
}

// 동적 메타데이터 생성 (SEO 핵심)
export async function generateMetadata({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const allItems = [
    ...itemsData.target,
    ...itemsData.candidate,
    ...itemsData.substandard
  ];
  const item = allItems.find((i) => i.id.toString() === id);

  if (!item) return { title: "매물을 찾을 수 없습니다" };

  return {
    title: `${item.onbid_cltr_nm} | AI 수익분석 리포트`,
    description: item.ai_curator_comment || `${item.onbid_cltr_nm}의 공매 차익 분석 결과입니다.`,
    openGraph: {
      title: item.onbid_cltr_nm,
      description: item.ai_curator_comment,
      images: [item.thumb_url || ""],
    },
  };
}

export default async function ItemDetail({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const allItems = [
    ...itemsData.target,
    ...itemsData.candidate,
    ...itemsData.substandard
  ] as any[];
  
  const item = allItems.find((i) => i.id.toString() === id) as OnbidItem;

  if (!item) notFound();

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-emerald-400";
    if (score >= 60) return "text-amber-400";
    return "text-slate-400";
  };

  const getDifficultyColor = (diff: string) => {
    if (diff === "Low") return "text-emerald-400";
    if (diff === "Medium") return "text-amber-400";
    return "text-red-400";
  };

  // 온비드 URL 생성
  const raw = item.raw_data;
  const baseUrl = "https://www.onbid.co.kr/op/cltrpbancinf/cltrdtl/CltrDtlController/mvmnCltrDtl.do";
  const onbidUrl = `${baseUrl}?cltrScrnGrpCd=0003&cltrPrptDivCd=${raw.prptDivCd || "0007"}&onbidCltrno=${raw.onbidCltrno}&onbidPbancNo=${raw.onbidPbancNo}&pbctNo=${raw.pbctNo}&pbctCdtnNo=${raw.pbctCdtnNo}`;

  return (
    <div className="min-h-screen bg-[#0a0a0c] text-slate-200 font-sans pb-20">
      {/* Top Bar */}
      <div className="border-b border-white/5 bg-[#0a0a0c]/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-5xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            <span className="text-sm font-bold">리스트로 돌아가기</span>
          </Link>
          <div className="text-[10px] font-mono text-slate-600 tracking-widest uppercase">
            ID: {item.cltr_mng_no}
          </div>
        </div>
      </div>

      <main className="max-w-5xl mx-auto px-6 mt-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
          {/* Left: Main Info */}
          <div className="lg:col-span-2">
            
            {/* Image Banner */}
            <div className="relative w-full aspect-video rounded-[3rem] overflow-hidden mb-12 border border-white/5 bg-white/5 shadow-2xl group">
              {item.thumb_url ? (
                <img 
                  src={item.thumb_url} 
                  alt={item.onbid_cltr_nm}
                  className="w-full h-full object-contain"
                />
              ) : (
                <div className="w-full h-full flex flex-col items-center justify-center text-slate-700">
                  <svg className="w-20 h-20 mb-4 opacity-20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <p className="text-sm font-bold opacity-20 uppercase tracking-widest">No Original Photo Provided</p>
                </div>
              )}
            </div>

            <div className="mb-8">
              <div className="flex items-center gap-3 mb-6">
                <span className="px-4 py-1.5 bg-indigo-500/10 text-indigo-400 text-xs font-black rounded-xl border border-indigo-500/20 uppercase tracking-widest">
                  {item.sub_category}
                </span>
                <span className="px-4 py-1.5 bg-emerald-500/10 text-emerald-400 text-xs font-black rounded-xl border border-emerald-500/20 uppercase tracking-widest">
                  {item.ai_pickup_method ?? "정보 없음"}
                </span>
              </div>
              <h1 className="text-4xl font-black text-white leading-tight mb-6 tracking-tight">
                {item.onbid_cltr_nm}
              </h1>
              <div className="flex items-center gap-4 text-slate-400 text-sm">
                <div className="flex items-center gap-1.5">
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  </svg>
                  {item.cltr_adr}
                </div>
              </div>
            </div>

            {/* AI Arbitrage Analysis Card */}
            {item.ai_curator_comment ? (
              <div className="bg-gradient-to-br from-white/[0.05] to-white/[0.01] border border-white/10 rounded-[2.5rem] p-10 mb-12 shadow-2xl relative overflow-hidden">
                <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-500/5 blur-[100px] -z-10"></div>
                
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-8 mb-12">
                  <div>
                    <h2 className="text-emerald-400 text-sm font-black uppercase tracking-widest mb-2">Expert Arbitrage Report</h2>
                    <p className="text-2xl font-bold text-white leading-tight">
                      "{item.ai_curator_comment}"
                    </p>
                  </div>
                  <div className="text-center bg-white/5 rounded-3xl p-6 border border-white/5 min-w-[140px]">
                    <div className={`text-5xl font-black mb-1 ${getScoreColor(item.ai_score ?? 0)}`}>
                      {item.ai_score ?? 0}
                    </div>
                    <div className="text-[10px] font-black text-slate-500 uppercase tracking-widest">투자 매력도</div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-10 mb-10">
                  <div className="space-y-8">
                    <div>
                      <h3 className="text-white font-bold mb-4 flex items-center gap-2">
                        <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full"></span>
                        수익성 분석 (Financials)
                      </h3>
                      <div className="bg-black/20 rounded-2xl p-6 border border-white/5 space-y-4">
                        <div className="flex justify-between items-center">
                          <span className="text-slate-500 text-xs">추정 시장가</span>
                          <span className="text-white font-bold">{item.ai_resale_value?.toLocaleString() ?? "0"}원</span>
                        </div>
                        <div className="flex justify-between items-center text-red-400">
                          <span className="text-slate-500 text-xs">입찰가(비용)</span>
                          <span className="font-bold">-{Number(item.min_bid_prc).toLocaleString()}원</span>
                        </div>
                        <div className="pt-4 border-t border-white/5 flex justify-between items-center">
                          <span className="text-emerald-400 font-black">예상 순수익</span>
                          <span className="text-emerald-400 text-2xl font-black">+{item.ai_expected_profit?.toLocaleString() ?? "0"}원</span>
                        </div>
                        <div className="text-right text-[10px] text-emerald-500/60 font-bold uppercase tracking-widest">
                          ROI: {item.ai_margin_percent?.toFixed(1) ?? "0.0"}%
                        </div>
                      </div>
                    </div>
                    <div>
                      <h3 className="text-white font-bold mb-4 flex items-center gap-2">
                        <span className="w-1.5 h-1.5 bg-amber-500 rounded-full"></span>
                        인수 난이도 (Friction)
                      </h3>
                      <div className="bg-amber-500/5 rounded-2xl p-6 border border-amber-500/10">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-slate-400 text-xs font-bold uppercase">수령 방식</span>
                          <span className="text-white font-bold">{item.ai_pickup_method ?? "정보 없음"}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-slate-400 text-xs font-bold uppercase">난이도 등급</span>
                          <span className={`font-black ${getDifficultyColor(item.ai_difficulty ?? "Medium")}`}>{item.ai_difficulty ?? "Medium"}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="space-y-8">
                    <div>
                      <h3 className="text-white font-bold mb-4 flex items-center gap-2">
                        <span className="w-1.5 h-1.5 bg-red-500 rounded-full"></span>
                        주의사항 (Risk Factor)
                      </h3>
                      <div className="bg-red-500/5 rounded-2xl p-6 text-red-200/80 text-sm leading-relaxed border border-red-500/10 h-[100px] overflow-y-auto">
                        {item.ai_risk_factor || "특이사항 없음"}
                      </div>
                    </div>
                    <div>
                      <h3 className="text-white font-bold mb-4 flex items-center gap-2">
                        <span className="w-1.5 h-1.5 bg-indigo-500 rounded-full"></span>
                        데이터 파싱 기반 사양
                      </h3>
                      <div className="bg-black/20 rounded-2xl p-6 text-slate-400 text-xs leading-relaxed border border-white/5 h-[150px] overflow-y-auto font-mono">
                        {item.raw_data.cltrDtlCont || "원본 데이터에 상세 설명이 없습니다."}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-white/5 border border-white/5 rounded-[2.5rem] p-10 mb-12 text-center">
                <p className="text-slate-500 italic">상세 분석 리포트가 없는 매물입니다.</p>
              </div>
            )}

            {/* Raw Data Section */}
            <div className="bg-white/[0.02] border border-white/5 rounded-[2.5rem] p-10">
              <h3 className="text-xl font-bold text-white mb-8">온비드 원본 정보</h3>
              <div className="space-y-6">
                {Object.entries(item.raw_data).map(([key, value]) => (
                  <div key={key} className="flex flex-col md:flex-row md:items-center py-4 border-b border-white/5 last:border-0 gap-2 md:gap-0">
                    <div className="md:w-1/3 text-slate-500 text-sm font-bold uppercase tracking-wider">{key}</div>
                    <div className="md:w-2/3 text-slate-300 text-sm break-all font-mono">{String(value)}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right: Price & CTA */}
          <div className="lg:col-span-1">
            <div className="bg-white/[0.03] border border-white/10 rounded-[2.5rem] p-8 sticky top-28 shadow-2xl">
              <div className="mb-8">
                <span className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-3 block">현재 최저입찰가</span>
                <div className="text-4xl font-black text-white">
                  {Number(item.min_bid_prc).toLocaleString()}
                  <span className="text-lg font-normal text-slate-400 ml-1">원</span>
                </div>
              </div>

              <div className="space-y-4 mb-8">
                <div className="flex items-center justify-between py-3 border-b border-white/5">
                  <span className="text-slate-500 text-xs font-bold uppercase">물건 상태</span>
                  <span className="text-white text-sm font-bold">중고/불용</span>
                </div>
                <div className="flex items-center justify-between py-3 border-b border-white/5">
                  <span className="text-slate-500 text-xs font-bold uppercase">입찰 방식</span>
                  <span className="text-white text-sm font-bold">최고가방식</span>
                </div>
                <div className="flex items-center justify-between py-3">
                  <span className="text-slate-500 text-xs font-bold uppercase">집행 기관</span>
                  <span className="text-white text-sm font-bold truncate ml-4">{item.raw_data.orgNm || "정보없음"}</span>
                </div>
              </div>

              <a 
                href={onbidUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="w-full py-5 bg-gradient-to-r from-emerald-500 to-indigo-600 text-white rounded-[1.5rem] font-black text-lg hover:brightness-110 transition-all shadow-xl shadow-emerald-500/20 active:scale-[0.98] mb-4 flex items-center justify-center"
              >
                온비드 입찰하러 가기
              </a>
              
              <p className="mt-6 text-[10px] text-slate-500 text-center leading-relaxed font-medium">
                * 본 분석 리포트는 AI의 추정치이며, 입찰 전 반드시 <br/>현장을 방문하여 실물 상태를 확인하시기 바랍니다.
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
