"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import itemsData from "@/data/items.json";

interface OnbidItem {
  id: number;
  pbanc_mng_no: string;
  onbid_cltr_nm: string;
  cltr_adr: string;
  min_bid_prc: number | string;
  sub_category: string;
  ai_score?: number;
  ai_expected_profit?: number;
  ai_margin_percent?: number;
  ai_pickup_method?: string;
  ai_difficulty?: string;
  ai_curator_comment?: string;
  thumb_url?: string;
}

export default function Dashboard() {
  const [viewMode, setViewMode] = useState<"target" | "candidate" | "substandard">("target");
  const [items, setItems] = useState<OnbidItem[]>(itemsData.target as any[]);
  const [categories, setCategories] = useState<string[]>(["전체보기", ...itemsData.categories]);
  const [selectedCategory, setSelectedCategory] = useState<string>("전체보기");

  useEffect(() => {
    let baseItems: OnbidItem[] = [];
    if (viewMode === "target") baseItems = itemsData.target as any[];
    else if (viewMode === "candidate") baseItems = itemsData.candidate as any[];
    else if (viewMode === "substandard") baseItems = itemsData.substandard as any[];

    if (viewMode === "target" && selectedCategory !== "전체보기") {
      setItems(baseItems.filter(item => item.sub_category === selectedCategory));
    } else {
      setItems(baseItems);
    }
  }, [selectedCategory, viewMode]);

  const getScoreColor = (score: number) => {
    if (viewMode === "substandard") return "text-red-400 border-red-500/30 bg-red-500/10";
    if (viewMode === "candidate") return "text-indigo-400 border-indigo-500/30 bg-indigo-500/10";
    if (score >= 80) return "text-emerald-400 border-emerald-500/30 bg-emerald-500/10";
    if (score >= 60) return "text-amber-400 border-amber-500/30 bg-amber-500/10";
    return "text-slate-400 border-slate-500/30 bg-slate-500/10";
  };

  const getDifficultyColor = (diff: string) => {
    if (diff === "Low") return "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
    if (diff === "Medium") return "bg-amber-500/10 text-amber-400 border-amber-500/20";
    return "bg-red-500/10 text-red-400 border-red-500/20";
  };

  return (
    <div className="min-h-screen bg-[#0a0a0c] text-slate-200 font-sans">
      {/* Header */}
      <header className="border-b border-white/5 bg-[#0a0a0c]/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-xl flex items-center justify-center font-black text-white text-xl shadow-lg shadow-indigo-600/20">M</div>
            <h1 className="text-xl font-black tracking-tight text-white">OnBid Arbitrage Master</h1>
          </div>
          <div className="flex items-center gap-2">
            <div className="bg-white/5 rounded-2xl p-1.5 flex gap-1 border border-white/10">
              <button 
                onClick={() => setViewMode("target")}
                className={`px-4 py-1.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${viewMode === "target" ? "bg-white text-black shadow-lg" : "text-slate-500 hover:text-white"}`}
              >
                정예 매물
              </button>
              <button 
                onClick={() => setViewMode("candidate")}
                className={`px-4 py-1.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${viewMode === "candidate" ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/20" : "text-slate-500 hover:text-white"}`}
              >
                후보 매물
              </button>
              <button 
                onClick={() => setViewMode("substandard")}
                className={`px-4 py-1.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${viewMode === "substandard" ? "bg-red-900/50 text-red-400 border border-red-500/30" : "text-slate-500 hover:text-white"}`}
              >
                기준 미달
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-12">
        {/* Hero Section */}
        <div className="mb-16">
          <h2 className="text-5xl font-black text-white mb-4 tracking-tight leading-[1.1]">
            {viewMode === "target" && <>잠자는 자산을 깨워 <br/><span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-indigo-500">실시간 차익</span>을 선점하세요.</>}
            {viewMode === "candidate" && <>Maverick이 엄선한 <br/><span className="text-indigo-400">잠재적 수익 매물</span>들입니다.</>}
            {viewMode === "substandard" && <>AI 분석 기준에 <br/><span className="text-red-400">미달된 매물</span> 리포트</>}
          </h2>
          <p className="text-slate-500 max-w-2xl leading-relaxed font-medium">
            {viewMode === "target" && "Maverick과 Flash 모델이 협업하여 최종 선별한 정예 매물입니다. 실시간 외부 시세 검증이 완료되었습니다."}
            {viewMode === "candidate" && "수천 개의 매물 중 Maverick이 1차 필터링을 통과시킨 매물입니다. 정밀 분석 전 단계입니다."}
            {viewMode === "substandard" && "수익성이 낮거나 리스크가 큰 매물들을 AI가 선별하여 제외했습니다. 탈락 사유를 확인하여 안목을 높이세요."}
          </p>
        </div>

        {/* Category Tabs (Only show if target mode) */}
        {viewMode === "target" && (
          <div className="flex flex-wrap gap-3 mb-12">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-6 py-2.5 rounded-full text-sm font-bold transition-all ${
                  selectedCategory === cat
                    ? "bg-white text-black shadow-xl scale-105"
                    : "bg-white/5 text-slate-400 hover:bg-white/10"
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        )}

        {/* Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {items.map((item) => (
              <Link href={`/items/${item.id}`} key={item.id} className="group h-full">
                <div className="bg-gradient-to-b from-white/[0.05] to-transparent border border-white/5 rounded-[2.5rem] p-1 transition-all duration-500 group-hover:border-indigo-500/50 group-hover:shadow-2xl group-hover:shadow-indigo-500/10 group-hover:-translate-y-2 h-full min-h-[620px] flex flex-col">
                  <div className="bg-[#0f0f12] rounded-[2.3rem] p-7 h-full flex flex-col flex-grow">
                    
                    <div className="flex-grow">
                      {/* Image Area */}
                      <div className="relative aspect-video mb-6 rounded-2xl overflow-hidden bg-white/5">
                        {item.thumb_url ? (
                          <img 
                            src={item.thumb_url} 
                            alt={item.onbid_cltr_nm}
                            className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center bg-white/5 text-slate-700">
                            <svg className="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                          </div>
                        )}
                        <div className="absolute top-4 left-4 flex gap-2">
                          <span className="px-3 py-1 bg-black/60 backdrop-blur-md text-white/70 text-[9px] font-black rounded-lg border border-white/10 uppercase tracking-widest">
                            {item.sub_category}
                          </span>
                          <span className={`px-3 py-1 backdrop-blur-md text-[9px] font-black rounded-lg border uppercase tracking-widest ${getDifficultyColor(item.ai_difficulty)}`}>
                            {item.ai_pickup_method}
                          </span>
                        </div>
                        <div className="absolute top-4 right-4">
                          <div className={`px-3 py-1.5 rounded-lg border font-black text-[10px] backdrop-blur-md ${getScoreColor(item.ai_score)}`}>
                            SCORE <span className="ml-1 text-sm">{item.ai_score}</span>
                          </div>
                        </div>
                      </div>

                        <div className="mb-4">
                          <span className={`text-[10px] font-bold uppercase tracking-widest block mb-1 ${
                            viewMode === "substandard" ? "text-red-500" : 
                            viewMode === "candidate" ? "text-indigo-400" : "text-emerald-500"
                          }`}>
                            {viewMode === "substandard" ? "분석 결과" : 
                             viewMode === "candidate" ? "Maverick 선별" : "예상 수익금"}
                          </span>
                          <div className={`text-3xl font-black group-hover:scale-105 transition-transform origin-left ${
                            viewMode === "substandard" ? "text-slate-400" : 
                            viewMode === "candidate" ? "text-indigo-400" : "text-emerald-400"
                          }`}>
                            {viewMode === "substandard" ? (
                              <span className="text-xl">수익성 부족</span>
                            ) : viewMode === "candidate" ? (
                              <span className="text-xl">정밀 분석 대기</span>
                            ) : (
                              <>
                                +{Number(item.ai_expected_profit).toLocaleString()}
                                <span className="text-sm font-medium ml-1">원</span>
                              </>
                            )}
                          </div>
                        </div>

                        <h3 className="text-lg font-bold text-white mb-4 line-clamp-2 leading-tight group-hover:text-indigo-400 transition-colors">
                          {item.onbid_cltr_nm}
                        </h3>
                        
                        {/* Curator Bubble */}
                        <div className={`rounded-2xl p-4 border mb-6 ${
                          viewMode === "substandard" ? "bg-red-500/5 border-red-500/10" : 
                          viewMode === "candidate" ? "bg-indigo-500/5 border-indigo-500/10" : "bg-white/5 border-white/5"
                        }`}>
                          <p className={`text-xs leading-relaxed italic ${
                            viewMode === "substandard" ? "text-red-400/70" : 
                            viewMode === "candidate" ? "text-indigo-300/70" : "text-slate-400"
                          }`}>
                            "{item.ai_curator_comment || (viewMode === "substandard" ? "분석 기준에 미달하는 매물입니다." : "분석 완료")}"
                          </p>
                        </div>
                    </div>

                    <div className="flex items-center justify-between pt-6 border-t border-white/5 mt-auto">
                      <div>
                        <span className="text-[11px] font-bold text-slate-500 uppercase tracking-widest block mb-1">현재 최저입찰가</span>
                        <div className="text-2xl font-black text-white tracking-tight">
                          {Number(item.min_bid_prc).toLocaleString()}
                          <span className="text-sm font-medium text-slate-500 ml-1">원</span>
                        </div>
                      </div>
                      <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center group-hover:bg-indigo-600 transition-all group-hover:translate-x-1">
                        <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                        </svg>
                      </div>
                    </div>
                  </div>
                </div>
              </Link>
          ))}
        </div>
      </main>
    </div>
  );
}

