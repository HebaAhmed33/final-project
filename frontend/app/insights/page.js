"use client";

import Link from "next/link";
import { useEffect } from "react";

export default function InsightsPage() {
  useEffect(() => {
    document.documentElement.classList.remove('dark');
    document.documentElement.classList.add('light');
  }, []);

  const articles = [
    {
      title: "How Aegis.One measures compliance across security standards",
      category: "Methodology",
      date: "Apr 18, 2026",
      read: "5 min read"
    },
    {
      title: "Why configuration assessment matters in ISMS programs",
      category: "Security",
      date: "Apr 15, 2026",
      read: "4 min read"
    },
    {
      title: "Common GRC gaps organizations overlook",
      category: "Compliance",
      date: "Apr 10, 2026",
      read: "7 min read"
    },
    {
      title: "How to prepare for audit readiness with centralized controls",
      category: "Audits",
      date: "Apr 02, 2026",
      read: "6 min read"
    },
    {
      title: "New compliance scoring dashboard released",
      category: "Product Update",
      date: "Mar 28, 2026",
      read: "3 min read"
    }
  ];

  return (
    <div className="min-h-screen bg-[#f4f6f9] text-[#1a2340] font-sans antialiased relative overflow-x-hidden">
      {/* NAVBAR */}
      <nav className="sticky top-0 z-50 bg-[#f4f6f9]/90 backdrop-blur-md shadow-sm border-b border-transparent">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2C12 2 4 5 4 12C4 18 12 22 12 22C12 22 20 18 20 12C20 5 12 2 12 2Z" fill="#1a2340" />
              <path d="M9 12L11 14L15 9" stroke="#f5c842" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            <span className="text-2xl font-bold tracking-tight text-[#1a2340]">Aegis.One</span>
          </Link>

          <div className="hidden md:flex items-center gap-8 text-sm font-medium text-gray-600">
            {[
              { name: 'About', path: '/about' },
              { name: 'Services', path: '/services' },
              { name: 'Solutions', path: '/solutions' },
              { name: 'Platform', path: '/platform' },
              { name: 'Partners', path: '/partners' },
              { name: 'Insights', path: '/insights' }
            ].map((item) => (
              <Link key={item.name} href={item.path} className={`cursor-pointer hover:text-[#1a2340] flex items-center gap-1 transition-colors duration-300 ${item.name === 'Insights' ? 'text-[#1a2340] font-bold' : ''}`}>
                {item.name}
              </Link>
            ))}
          </div>

          <div className="flex items-center gap-4">
            <Link href="/login" className="bg-[#1a2340] !text-white visited:!text-white hover:!text-white active:!text-white focus:!text-white px-6 py-2.5 rounded-lg hover:bg-[#253654] transition-all shadow-sm hover:shadow-md">
              <span className="!text-white font-[600]">Get Started</span>
            </Link>
          </div>
        </div>
      </nav>

      {/* HERO SECTION */}
      <section className="w-full pt-20 pb-16 px-6 relative bg-white border-b border-gray-100">
        <div className="max-w-[800px] mx-auto text-center flex flex-col items-center">
          <h1 className="text-[46px] font-extrabold tracking-tight text-[#1a2340] leading-tight mb-6">
            Insights &amp; <span className="text-[#f5c842]">Updates</span>
          </h1>
          <p className="text-[20px] text-gray-600 leading-relaxed max-w-[700px]">
            Stay updated with the latest in GRC operations, compliance strategies, configuration management, and platform announcements.
          </p>
        </div>
      </section>

      {/* ARTICLES GRID */}
      <div className="max-w-7xl mx-auto px-6 py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {articles.map((article, idx) => (
            <div key={idx} className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-all group flex flex-col cursor-pointer">
              <div className="flex justify-between items-center mb-6">
                <span className="text-[12px] font-bold tracking-widest uppercase text-[#f5c842]">{article.category}</span>
                <span className="text-[13px] text-gray-400 font-medium">{article.read}</span>
              </div>
              <h3 className="text-[22px] font-bold text-[#1a2340] mb-4 leading-snug group-hover:text-[#253654] transition-colors line-clamp-3">
                {article.title}
              </h3>
              <div className="mt-auto pt-6 border-t border-gray-50 flex items-center justify-between text-gray-400 text-[14px]">
                <span>{article.date}</span>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="opacity-0 group-hover:opacity-100 transform translate-x-[-10px] group-hover:translate-x-0 transition-all text-[#1a2340]">
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                  <polyline points="12 5 19 12 12 19"></polyline>
                </svg>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* CTA */}
      <section className="max-w-7xl mx-auto px-6 pb-24">
        <div className="w-full bg-[#1a2340] border border-[#253654] rounded-3xl p-12 text-center flex flex-col items-center shadow-lg relative overflow-hidden">
          <h2 className="text-[32px] font-bold text-white mb-4 relative z-10">Subscribe for GRC Excellence</h2>
          <p className="text-gray-300 mb-8 max-w-[500px] relative z-10">Don't miss the latest updates on compliance frameworks, standards mapping, and Aegis.One platform capabilities.</p>
          <div className="flex w-full max-w-md gap-2 relative z-10">
            <input type="email" placeholder="Enter your email" className="focus:outline-none flex-1 px-4 py-3 rounded-lg border border-transparent focus:border-[#f5c842] text-gray-800" />
            <button className="bg-[#f5c842] text-[#1a2340] px-6 py-3 rounded-lg font-bold hover:brightness-110 transition-all shadow-sm">
              Subscribe
            </button>
          </div>
        </div>
      </section>

    </div>
  );
}
