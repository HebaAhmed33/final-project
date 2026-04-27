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
      title: "Compliance Assessment",
      desc: "Evaluate your organization against industry standards such as ISO 27001, NIST, and HIPAA to understand your compliance posture.",
      helperText: "Best for audits, certifications, and governance tracking.",
      btnText: "Start Assessment",
      href: "/upload",
      icon: (
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
        </svg>
      )
    },
    {
      title: "Technical Configuration Analysis",
      desc: "Upload infrastructure or system configurations to detect vulnerabilities, misconfigurations, and operational risks.",
      helperText: "Best for engineers and security teams.",
      btnText: "Upload & Analyze",
      href: "/upload",
      icon: (
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      )
    }
  ];

  return (
    <PageContainer>
      <div className="w-full bg-[var(--bg-main)] min-h-[calc(100vh-80px)] p-8 transition-colors duration-300">
        <div className="max-w-[1100px] mx-auto">
          
          <div className="mb-12">
            <h2 className="text-[18px] font-medium text-[var(--text-muted)] mb-1">
              Welcome back, {companyName || "sparck"} 👋
            </h2>
            <h1 className="text-[36px] font-extrabold text-[var(--text-main)] mb-4 tracking-tight">
              Your Security Workspace
            </h1>
            <p className="text-[18px] text-[var(--text-muted)] font-medium">
              Start by choosing how you want to assess your organization — compliance-based or technical analysis.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {WORKSPACE_BLOCKS.map((block, idx) => (
              <div 
                key={idx} 
                className="bg-[var(--bg-card)] rounded-2xl p-8 shadow-[var(--shadow-card)] border border-[var(--border-color)] flex flex-col justify-between hover:shadow-md transition-shadow duration-300"
              >
                <div>
                  <div className="w-12 h-12 bg-[var(--icon-bg)] text-[var(--primary)] rounded-xl flex items-center justify-center mb-6">
                    <div className="w-6 h-6">{block.icon}</div>
                  </div>
                  <h3 className="text-[20px] font-bold text-[var(--text-main)] mb-3">{block.title}</h3>
                  <p className="text-[15px] text-[var(--text-muted)] leading-relaxed mb-4">{block.desc}</p>
                  <p className="text-[13px] text-[var(--text-muted)] italic mb-8">{block.helperText}</p>
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
