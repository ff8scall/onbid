"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface OnbidItem {
  id: number;
  pbanc_mng_no: string;
  onbid_cltr_nm: string;
  cltr_adr: string;
  min_bid_prc: number;
  sub_category: string;
  ai_score: number;
  ai_catchphrase: string;
  ai_recommendation: string;
  thumb_url: string;
}

export default function Dashboard() {
  const [items, setItems] = useState<OnbidItem[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>("전체보기");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCategories();
    fetchItems();
  }, [selectedCategory]);

  const fetchCategories = async () => {
    const res = await fetch("http://localhost:8000/categories");
    const data = await res.json();
    setCategories(["전체보기", ...data]);
  };

  const fetchItems = async () => {
    setLoading(true);
    let url = "http://localhost:8000/items";
    if (selectedCategory !== "전체보기") {
      url += `?category=${selectedCategory}`;
    }
    const res = await fetch(url);
    const data = await res.json();
    setItems(data);
    setLoading(false);
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-emerald-400 border-emerald-500/30 bg-emerald-500/10";
    if (score >= 60) return "text-amber-400 border-amber-500/30 bg-amber-500/10";
    return "text-slate-400 border-slate-500/30 bg-slate-500/10";
  };

  return (
    <div className="min-h-screen bg-[#0a0a0c] text-slate-200 font-sans">
      {/* Header */}
      <header className="border-b border-white/5 bg-[#0a0a0c]/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center font-black text-white text-xl shadow-lg shadow-indigo-600/20">P</div>
            <h1 className="text-xl font-black tracking-tight text-white">Pbid Hunter</h1>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
            <span className="text-[10px] font-bold text-emerald-500 uppercase tracking-widest">Live Scan Active</span>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-12">
        {/* Hero Section */}
        <div className="mb-16">
          <h2 className="text-5xl font-black text-white mb-4 tracking-tight">온비드의 숨은 보석을 찾아서.</h2>
          <p className="text-slate-500 max-w-2xl leading-relaxed font-medium">
            집행기관의 신뢰도, 매물 수량, 사양 및 유찰 이력을 AI가 정밀 분석하여 최고의 가성비 IT 기기만을 큐레이션합니다.
          </p>
        </div>

        {/* Category Tabs */}
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

        {/* Grid */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-80 bg-white/5 rounded-[2.5rem] animate-pulse"></div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {items.map((item) => (
              <Link href={`/items/${item.id}`} key={item.id} className="group">
                <div className="bg-gradient-to-b from-white/[0.05] to-transparent border border-white/5 rounded-[2.5rem] p-1 overflow-hidden transition-all duration-500 group-hover:border-indigo-500/50 group-hover:shadow-2xl group-hover:shadow-indigo-500/10 group-hover:-translate-y-2">
                  <div className="bg-[#0f0f12] rounded-[2.3rem] p-7 h-full flex flex-col">
                    
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
                      <div className="absolute top-4 left-4">
                        <span className="px-3 py-1 bg-black/60 backdrop-blur-md text-white/70 text-[9px] font-black rounded-lg border border-white/10 uppercase tracking-widest">
                          {item.sub_category}
                        </span>
                      </div>
                      <div className="absolute top-4 right-4">
                        <div className={`px-3 py-1.5 rounded-lg border font-black text-[10px] backdrop-blur-md ${getScoreColor(item.ai_score)}`}>
                          AI SCORE <span className="ml-1 text-sm">{item.ai_score}</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex-1">
                      <p className="text-indigo-400 text-[10px] font-black mb-3 line-clamp-1 uppercase tracking-widest">
                        "{item.ai_catchphrase || "분석 완료"}"
                      </p>
                      <h3 className="text-xl font-bold text-white mb-4 line-clamp-2 leading-tight group-hover:text-indigo-400 transition-colors">
                        {item.onbid_cltr_nm}
                      </h3>
                      <div className="flex items-center gap-2 text-slate-500 text-xs mb-8">
                        <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        </svg>
                        {item.cltr_adr.split(" ").slice(0, 2).join(" ")}
                      </div>
                    </div>

                    <div className="flex items-center justify-between pt-6 border-t border-white/5">
                      <div>
                        <span className="text-[10px] font-bold text-slate-600 uppercase tracking-widest block mb-1">최저입찰가격</span>
                        <div className="text-xl font-black text-white">
                          {Number(item.min_bid_prc).toLocaleString()}
                          <span className="text-xs font-medium text-slate-500 ml-1">원</span>
                        </div>
                      </div>
                      <div className="w-12 h-12 rounded-2xl bg-white/5 flex items-center justify-center group-hover:bg-indigo-600 transition-colors">
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
        )}
      </main>
    </div>
  );
}
