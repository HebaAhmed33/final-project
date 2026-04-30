"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import PageContainer from "../components/PageContainer";

const AccordionItem = ({ title, children, defaultOpen = false }) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  return (
    <div className={`border border-[var(--border-color)] rounded-xl mb-4 overflow-hidden bg-[var(--bg-card)] transition-all duration-300 ${isOpen ? 'shadow-md border-[var(--primary)]' : 'hover:border-gray-300'}`}>
      <button 
        onClick={() => setIsOpen(!isOpen)} 
        className="w-full flex items-center justify-between p-5 text-left bg-transparent hover:bg-[var(--bg-main)] transition-colors focus:outline-none group"
      >
        <span className={`font-semibold text-[16px] transition-colors ${isOpen ? 'text-[var(--primary)]' : 'text-[var(--text-main)] group-hover:text-[var(--primary)]'}`}>{title}</span>
        <div className={`flex items-center justify-center w-8 h-8 rounded-full transition-colors ${isOpen ? 'bg-[var(--primary)] text-[var(--primary)] bg-opacity-10' : 'bg-[var(--icon-bg)] text-[var(--text-muted)] group-hover:bg-[var(--primary)] group-hover:bg-opacity-10 group-hover:text-[var(--primary)]'}`}>
          <svg className={`w-5 h-5 transition-transform duration-300 ${isOpen ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>
      <div 
        className={`transition-all duration-400 ease-in-out ${isOpen ? 'max-h-[500px] opacity-100' : 'max-h-0 opacity-0'} overflow-hidden`}
      >
        <div className="p-5 pt-0 text-[15px] text-[var(--text-muted)] leading-relaxed">
          <div className="pt-4 border-t border-[var(--border-color)]">{children}</div>
        </div>
      </div>
    </div>
  );
};

export default function WorkspacePage() {
  const [companyName, setCompanyName] = useState("");

  useEffect(() => {
    sessionStorage.removeItem('assessment_result');
    sessionStorage.removeItem('config_result');
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

  const getFrameworkIcon = (fw) => {
    switch(fw) {
      case "ISO 27001":
        return <svg className="w-3.5 h-3.5 mr-1.5 inline text-[var(--primary)] group-hover/fw:text-white transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>;
      case "HIPAA":
        return <svg className="w-3.5 h-3.5 mr-1.5 inline text-[var(--primary)] group-hover/fw:text-white transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" /></svg>;
      case "PCI DSS":
        return <svg className="w-3.5 h-3.5 mr-1.5 inline text-[var(--primary)] group-hover/fw:text-white transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" /></svg>;
      case "NIST":
        return <svg className="w-3.5 h-3.5 mr-1.5 inline text-[var(--primary)] group-hover/fw:text-white transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" /></svg>;
      case "CIS Controls":
        return <svg className="w-3.5 h-3.5 mr-1.5 inline text-[var(--primary)] group-hover/fw:text-white transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" /></svg>;
      default:
        return null;
    }
  };

  const WORKSPACE_BLOCKS = [
    {
      title: "Compliance Assessment",
      desc: "Evaluate your organization's overarching governance, policies, and security controls to understand your compliance posture.",
      helperText: "Best for audits, certifications, and high-level governance tracking.",
      btnText: "Start Assessment",
      href: "/assessment",
      frameworks: ["ISO 27001", "HIPAA", "PCI DSS"],
      whyItMatters: "Essential for proving regulatory adherence to auditors and partners, ensuring your organizational processes are robust and secure.",
      icon: (
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
      )
    },
    {
      title: "Technical Configuration Analysis",
      desc: "Upload and analyze specific infrastructure or system configuration files to detect vulnerabilities and misconfigurations.",
      helperText: "Best for engineers, devops, and security operations teams.",
      btnText: "Start Configuration Analysis",
      href: "/configuration",
      frameworks: ["ISO 27001", "NIST", "CIS Controls"],
      whyItMatters: "Directly protects against technical breaches by finding misconfigured ports, weak encryptions, and insecure settings before they are exploited.",
      icon: (
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
        </svg>
      )
    }
  ];

  return (
    <PageContainer>
      <div className="w-full bg-gradient-to-b from-[var(--bg-card)] to-[var(--bg-main)] min-h-[calc(100vh-80px)] p-6 md:p-8 transition-colors duration-300">
        <div className="max-w-[1100px] mx-auto">
          
          {/* Header section */}
          <div className="mb-14">
            <h2 className="text-[18px] font-medium text-[var(--primary)] mb-2 flex items-center gap-2">
              Welcome back, {companyName || "sparck"} 👋
            </h2>
            <h1 className="text-[38px] font-extrabold text-[var(--text-main)] mb-4 tracking-tight">
              Security & Compliance Overview
            </h1>
            <p className="text-[17.5px] text-[var(--text-muted)] font-medium max-w-3xl leading-relaxed">
              Choose how you want to evaluate your organization. You can assess broad organizational compliance or perform deep technical configuration analysis on your infrastructure.
            </p>
          </div>

          {/* Module Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16">
            {WORKSPACE_BLOCKS.map((block, idx) => (
              <div 
                key={idx} 
                className="bg-[var(--bg-card)] rounded-2xl p-8 shadow-[var(--shadow-card)] border border-[var(--border-color)] flex flex-col justify-between group hover:shadow-[0_20px_40px_-15px_rgba(0,0,0,0.1)] hover:-translate-y-1 hover:border-[var(--primary)] transition-all duration-300 relative overflow-hidden"
              >
                {/* Subtle gradient background element for card */}
                <div className="absolute -right-20 -top-20 w-48 h-48 bg-[var(--primary)] rounded-full blur-[80px] opacity-10 group-hover:opacity-20 transition-opacity duration-300 pointer-events-none"></div>

                <div className="relative z-10">
                  <div className="w-14 h-14 bg-[var(--icon-bg)] text-[var(--primary)] rounded-xl flex items-center justify-center mb-6 transition-transform duration-300 group-hover:scale-110 shadow-sm border border-[var(--border-color)]">
                    <div className="w-7 h-7">{block.icon}</div>
                  </div>
                  <h3 className="text-[22px] font-bold text-[var(--text-main)] mb-3">{block.title}</h3>
                  <p className="text-[15px] text-[var(--text-muted)] leading-relaxed mb-6">{block.desc}</p>
                  
                  {/* Frameworks Chips */}
                  <div className="mb-8">
                    <h4 className="text-[11.5px] font-bold text-[var(--text-muted)] uppercase tracking-wider mb-3 flex items-center gap-2">
                      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" /></svg>
                      Supported Frameworks
                    </h4>
                    <div className="flex flex-wrap gap-2.5">
                      {block.frameworks.map(fw => (
                        <span key={fw} className="group/fw flex items-center px-3.5 py-1.5 bg-[var(--icon-bg)] text-[var(--text-main)] text-[13px] font-semibold rounded-full border border-[var(--border-color)] hover:bg-[var(--primary)] hover:text-white transition-all duration-300 cursor-default shadow-sm hover:shadow-md hover:-translate-y-0.5">
                          {getFrameworkIcon(fw)}
                          {fw}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Why it matters Box */}
                  <div className="mb-8 bg-gradient-to-br from-[var(--bg-main)] to-[var(--icon-bg)] p-5 rounded-xl border border-[var(--border-color)] transition-colors group-hover:border-[var(--primary)] group-hover:border-opacity-30">
                    <h4 className="text-[13px] font-bold text-[var(--text-main)] mb-2 flex items-center gap-2">
                      <svg className="w-4.5 h-4.5 text-[var(--primary)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      Why it matters
                    </h4>
                    <p className="text-[13.5px] text-[var(--text-muted)] leading-relaxed">{block.whyItMatters}</p>
                  </div>
                </div>
                
                <div className="mt-auto relative z-10">
                  <p className="text-[13px] text-[var(--text-muted)] font-medium mb-4 flex items-center gap-2">
                    <svg className="w-4 h-4 text-[var(--primary)]" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                    {block.helperText}
                  </p>
                  <Link 
                    href={block.href} 
                    className="bg-[var(--primary)] !text-white hover:bg-[var(--primary-hover)] text-center font-bold py-3.5 px-6 rounded-xl transition-all duration-300 w-full shadow-[0_4px_14px_0_rgba(var(--primary-rgb),0.39)] hover:shadow-[0_6px_20px_rgba(var(--primary-rgb),0.23)] block"
                  >
                    {block.btnText}
                  </Link>
                </div>
              </div>
            ))}
          </div>

          {/* Spacer Line */}
          <div className="w-full h-px bg-gradient-to-r from-transparent via-[var(--border-color)] to-transparent mb-16"></div>

          {/* Comparison Cards Section */}
          <div className="mb-16">
            <h3 className="text-[24px] font-extrabold text-[var(--text-main)] mb-8 flex items-center gap-3 justify-center text-center">
              <svg className="w-7 h-7 text-[var(--primary)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              Module Comparison
            </h3>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Compliance Assessment Comparison Card */}
              <div className="bg-[var(--bg-card)] rounded-2xl p-8 border border-[var(--border-color)] shadow-[var(--shadow-card)] relative overflow-hidden group hover:border-[var(--primary)] transition-colors duration-300">
                <div className="absolute top-0 left-0 w-full h-1.5 bg-gradient-to-r from-[var(--primary)] to-[#3b82f6]"></div>
                <h4 className="text-[20px] font-bold text-[var(--text-main)] mb-6 flex items-center gap-3">
                  <div className="p-2 bg-[var(--icon-bg)] text-[var(--primary)] rounded-lg">
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" /></svg>
                  </div>
                  Compliance Assessment
                </h4>
                <ul className="space-y-6">
                  <li className="flex gap-4">
                    <div className="mt-0.5 w-6 h-6 rounded-full bg-[var(--icon-bg)] flex items-center justify-center flex-shrink-0 text-[var(--primary)]">
                      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                    </div>
                    <div>
                      <span className="block font-bold text-[14.5px] text-[var(--text-main)] mb-1">Primary Focus</span>
                      <span className="text-[14px] text-[var(--text-muted)] leading-relaxed">Organizational policies, governance, employee training, and overall high-level security posture.</span>
                    </div>
                  </li>
                  <li className="flex gap-4">
                    <div className="mt-0.5 w-6 h-6 rounded-full bg-[var(--icon-bg)] flex items-center justify-center flex-shrink-0 text-[var(--primary)]">
                      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" /></svg>
                    </div>
                    <div>
                      <span className="block font-bold text-[14.5px] text-[var(--text-main)] mb-1">Input Method</span>
                      <span className="text-[14px] text-[var(--text-muted)] leading-relaxed">Answers to control questionnaires and uploaded policy/evidence documents.</span>
                    </div>
                  </li>
                  <li className="flex gap-4">
                    <div className="mt-0.5 w-6 h-6 rounded-full bg-[var(--icon-bg)] flex items-center justify-center flex-shrink-0 text-[var(--primary)]">
                      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                    </div>
                    <div>
                      <span className="block font-bold text-[14.5px] text-[var(--text-main)] mb-1">Expected Output</span>
                      <span className="text-[14px] text-[var(--text-muted)] leading-relaxed">Statement of Applicability (SoA), High-level Risk Register, Vendor Checklist, and Training Matrices.</span>
                    </div>
                  </li>
                </ul>
              </div>

              {/* Configuration Analysis Comparison Card */}
              <div className="bg-[var(--bg-card)] rounded-2xl p-8 border border-[var(--border-color)] shadow-[var(--shadow-card)] relative overflow-hidden group hover:border-[var(--primary)] transition-colors duration-300">
                <div className="absolute top-0 left-0 w-full h-1.5 bg-gradient-to-r from-[var(--primary)] to-[#8b5cf6]"></div>
                <h4 className="text-[20px] font-bold text-[var(--text-main)] mb-6 flex items-center gap-3">
                  <div className="p-2 bg-[var(--icon-bg)] text-[var(--primary)] rounded-lg">
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" /></svg>
                  </div>
                  Configuration Analysis
                </h4>
                <ul className="space-y-6">
                  <li className="flex gap-4">
                    <div className="mt-0.5 w-6 h-6 rounded-full bg-[var(--icon-bg)] flex items-center justify-center flex-shrink-0 text-[var(--primary)]">
                      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                    </div>
                    <div>
                      <span className="block font-bold text-[14.5px] text-[var(--text-main)] mb-1">Primary Focus</span>
                      <span className="text-[14px] text-[var(--text-muted)] leading-relaxed">Deep technical settings, system hardening, and granular infrastructure-level vulnerabilities.</span>
                    </div>
                  </li>
                  <li className="flex gap-4">
                    <div className="mt-0.5 w-6 h-6 rounded-full bg-[var(--icon-bg)] flex items-center justify-center flex-shrink-0 text-[var(--primary)]">
                      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
                    </div>
                    <div>
                      <span className="block font-bold text-[14.5px] text-[var(--text-main)] mb-1">Input Method</span>
                      <span className="text-[14px] text-[var(--text-muted)] leading-relaxed">Raw configuration files (e.g., JSON, YAML, .conf, .sh) and technical scripts.</span>
                    </div>
                  </li>
                  <li className="flex gap-4">
                    <div className="mt-0.5 w-6 h-6 rounded-full bg-[var(--icon-bg)] flex items-center justify-center flex-shrink-0 text-[var(--primary)]">
                      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M10 21h7a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v11m0 5l4.879-4.879m0 0a3 3 0 104.243-4.242 3 3 0 00-4.243 4.242z" /></svg>
                    </div>
                    <div>
                      <span className="block font-bold text-[14.5px] text-[var(--text-main)] mb-1">Expected Output</span>
                      <span className="text-[14px] text-[var(--text-muted)] leading-relaxed">Vulnerability reports, exact line-number technical findings, and specific remediation scripts.</span>
                    </div>
                  </li>
                </ul>
              </div>
            </div>
          </div>

          {/* Spacer Line */}
          <div className="w-full h-px bg-gradient-to-r from-transparent via-[var(--border-color)] to-transparent mb-16"></div>

          {/* FAQ Accordions Section */}
          <div className="mb-12">
            <h3 className="text-[24px] font-extrabold text-[var(--text-main)] mb-8 text-center">Frequently Asked Questions</h3>
            <div className="max-w-4xl mx-auto">
              <AccordionItem title="Do I need to complete both modules?" defaultOpen={true}>
                While not strictly required, completing both modules provides a <strong>holistic security overview</strong>. 
                The Compliance Assessment ensures your company has the right rules and policies in place, while the Technical Configuration Analysis proves that your actual servers and networks are enforcing those rules. Auditors often look for both managerial oversight and technical proof.
              </AccordionItem>
              <AccordionItem title="Can I use Configuration Analysis to satisfy Compliance Assessment requirements?">
                Yes. Many technical findings from your Configuration Analysis can act as <strong>supporting evidence</strong> for your Compliance Assessment. For example, proving that a firewall is configured correctly (Configuration Analysis) satisfies the ISO 27001 requirement for network security controls (Compliance Assessment).
              </AccordionItem>
              <AccordionItem title="What happens to the uploaded data?">
                All uploaded questionnaires, policies, and configuration files are analyzed in memory using our robust inference engines. We do not permanently store sensitive infrastructure secrets. For more details on data retention, please refer to our Privacy Policy.
              </AccordionItem>
            </div>
          </div>

        </div>
      </div>
    </PageContainer>
  );
}
