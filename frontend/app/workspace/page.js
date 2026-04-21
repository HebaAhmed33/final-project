"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import PageContainer from "../components/PageContainer";

export default function WorkspacePage() {
  const [companyName, setCompanyName] = useState("");

  useEffect(() => {
    const userStr = localStorage.getItem("smartisms_user");
    if (userStr) {
      try {
        const user = JSON.parse(userStr);
        if (user.companyName) {
          setCompanyName(user.companyName);
        }
      } catch (e) {
        console.error("Failed to parse user data");
      }
    }
  }, []);

  const WORKSPACE_BLOCKS = [
    {
      title: "Start Assessment",
      desc: "Run full cross-framework compliance assessments against ISO 27001, NIST, and HIPAA standards.",
      btnText: "New Assessment",
      href: "/upload",
      icon: (
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
        </svg>
      )
    },
    {
      title: "Upload Configuration",
      desc: "Scan infrastructure blueprints and detect deep operational drift actively.",
      btnText: "Analyze Config",
      href: "/config-analysis",
      icon: (
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      )
    },
    {
      title: "Add Assets",
      desc: "Manage and categorize all operational network assets, endpoints, and data.",
      btnText: "Manage Assets",
      href: "/dashboard",
      icon: (
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
      )
    },
    {
      title: "Review Access Requests",
      desc: "Review, approve, and authorize critical governance compliance workflows.",
      btnText: "Approvals",
      href: "/access-requests",
      icon: (
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
        </svg>
      )
    }
  ];

  return (
    <PageContainer>
      <div className="w-full bg-[var(--bg-main)] min-h-[calc(100vh-80px)] p-8 transition-colors duration-300">
        <div className="max-w-[1100px] mx-auto">
          
          <div className="mb-12">
            <h1 className="text-[36px] font-extrabold text-[var(--text-main)] mb-3 tracking-tight">
              Welcome to <span className="bg-[var(--accent)] text-[#1a2340] rounded-[6px] px-3 py-1 inline-block">Aegis.One</span>
            </h1>
            <p className="text-[18px] text-[var(--text-muted)] font-medium">
              Welcome, <span className="text-[var(--text-main)] font-bold">{companyName || "Organization"}</span>. Start your workspace setup to manage compliance, assets, access workflows, and configuration reviews.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {WORKSPACE_BLOCKS.map((block, idx) => (
              <div 
                key={idx} 
                className="bg-[var(--bg-card)] rounded-2xl p-8 shadow-[var(--shadow-card)] border border-[var(--border-color)] flex flex-col justify-between hover:shadow-md transition-shadow duration-300"
              >
                <div>
                  <div className="w-12 h-12 bg-[var(--text-main)]/10 text-[var(--text-main)] rounded-xl flex items-center justify-center mb-6">
                    <div className="w-6 h-6">{block.icon}</div>
                  </div>
                  <h3 className="text-[20px] font-bold text-[var(--text-main)] mb-3">{block.title}</h3>
                  <p className="text-[15px] text-[var(--text-muted)] leading-relaxed mb-8">{block.desc}</p>
                </div>
                
                <Link 
                  href={block.href} 
                  className="bg-[var(--primary)] !text-white hover:bg-[var(--primary-hover)] hover:!text-white visited:!text-white active:!text-white focus:!text-white text-center font-bold py-3 px-6 rounded-xl transition-all duration-300 w-full shadow-sm hover:shadow-md hover:-translate-y-0.5"
                >
                  {block.btnText}
                </Link>
              </div>
            ))}
          </div>

        </div>
      </div>
    </PageContainer>
  );
}
