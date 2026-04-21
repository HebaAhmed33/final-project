"use client";

import Link from "next/link";
import { useState, useEffect } from "react";

export default function AboutPage() {
  const [activeStandard, setActiveStandard] = useState(null);

  useEffect(() => {
    document.documentElement.classList.remove('dark');
    document.documentElement.classList.add('light');
  }, []);

  return (
    <div className="min-h-screen bg-[#f4f6f9] text-[#1a2340] font-sans antialiased relative overflow-x-hidden">
      {/* OVERVIEW SECTION (Breadcrumb style) */}
      <section className="w-full pt-16 pb-12 px-6 relative bg-white border-b border-gray-100">
        <div className="max-w-[800px] mx-auto text-center flex flex-col items-center">
          
          {/* Breadcrumb */}
          <div className="flex items-center gap-2 text-sm font-medium text-gray-500 mb-6 bg-gray-50 px-4 py-1.5 rounded-full border border-gray-100">
            <Link href="/" className="hover:text-[#1a2340] transition-colors">Home</Link>
            <span className="text-gray-300">›</span>
            <span className="text-[#1a2340] font-bold">Overview</span>
          </div>

          <h1 className="text-[42px] md:text-[52px] font-extrabold tracking-tight text-[#1a2340] leading-tight mt-4 mb-6">
            We are <span className="bg-[#fde68a] text-[#1a2340] rounded-[6px] px-3 py-[2px] transition-colors duration-300 inline-block">Aegis</span>, we are ONE
          </h1>
          <p className="text-[18px] md:text-[22px] text-gray-500 font-medium leading-relaxed max-w-[850px] mx-auto">
            Your trusted partner in cybersecurity and compliance, empowering organizations to streamline governance, manage risk effectively, and achieve continuous compliance through intelligent automation and centralized security intelligence.
          </p>
        </div>
      </section>

      {/* MAIN CONTENT WRAPPER */}
      <div className="max-w-7xl mx-auto px-6 py-16 flex flex-col gap-24">
        
        {/* WHO WE ARE */}
        <section className="flex flex-col md:flex-row gap-12 items-center">
          <div className="flex-1 space-y-6">
            <h2 className="text-[32px] font-bold text-[#1a2340]">Who We Are</h2>
            <div className="w-16 h-1 bg-[#f5c842] rounded-full"></div>
            <p className="text-[17px] text-gray-600 leading-relaxed">
              We empower organizations to take absolute control of their cyber landscape. Aegis.One helps you thoroughly understand how compliant you are against key industry standards, manage overwhelming GRC workflows with ease, and continuously identify configuration weaknesses before they become a breach.
            </p>
          </div>
          <div className="flex-1 p-4 lg:p-8 flex items-center justify-center lg:justify-end relative group min-h-[300px]">
            {/* Background glowing effect on hover */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[80%] h-[80%] bg-[#f5c842] opacity-0 group-hover:opacity-15 blur-[70px] rounded-full transition-opacity duration-700 pointer-events-none z-0"></div>
            
            <div className="relative z-10 rounded-2xl bg-white p-3 shadow-[0_8px_30px_-5px_rgba(26,35,64,0.15)] w-full max-w-[500px] transition-all duration-500 group-hover:-translate-y-2 group-hover:shadow-[0_20px_40px_-10px_rgba(26,35,64,0.25)] border border-gray-100">
              <div className="relative rounded-xl overflow-hidden w-full bg-transparent shadow-inner">
                <img 
                  src="/isms-new.jpg" 
                  alt="Information Security Management System"
                  className="w-full h-auto object-cover scale-100 group-hover:scale-105 transition-transform duration-700 ease-out block" 
                />
              </div>
            </div>
          </div>
        </section>

        {/* WHAT THE PLATFORM DOES */}
        <section className="flex flex-col items-center text-center">
          <h2 className="text-[32px] font-bold text-[#1a2340] mb-4">What the Platform Does</h2>
          <div className="w-16 h-1 bg-[#f5c842] rounded-full mb-12"></div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 w-full">
            {[
              {
                title: "Compliance Scoring",
                desc: "Quantify your posture with dynamic scores updating in real-time as controls are met.",
                icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#f5c842" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
              },
              {
                title: "Standards Mapping",
                desc: "Map a single central control to multiple frameworks simultaneously to prevent duplicate work.",
                icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#f5c842" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>
              },
              {
                title: "GRC Workflow",
                desc: "Bring team tasks, audits, evidence gathering, and governance approvals into one unified queue.",
                icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#f5c842" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
              },
              {
                title: "Configuration Assessment",
                desc: "Evaluate technical infrastructures natively against compliance rules to spot misconfigurations.",
                icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#f5c842" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="4 14 10 14 10 20"></polyline><polyline points="20 10 14 10 14 4"></polyline><line x1="14" y1="10" x2="21" y2="3"></line><line x1="3" y1="21" x2="10" y2="14"></line></svg>
              }
            ].map((feature, i) => (
              <div key={i} className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow text-left group">
                <div className="w-12 h-12 bg-[#f4f6f9] rounded-lg flex items-center justify-center mb-6 group-hover:bg-[#1a2340] group-hover:text-white transition-colors">
                  {feature.icon}
                </div>
                <h3 className="text-[19px] font-bold text-[#1a2340] mb-3">{feature.title}</h3>
                <p className="text-gray-500 text-[15px] leading-relaxed">{feature.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* SUPPORTED STANDARDS */}
        <section className="bg-white rounded-2xl p-12 shadow-sm border border-gray-100 flex flex-col items-center">
          <h2 className="text-[28px] font-bold text-[#1a2340] mb-8">Supported Standards</h2>
          <div className="flex flex-wrap justify-center gap-4 w-full max-w-[900px]">
            {['ISO 27001', 'NIST', 'PCI DSS', 'HIPAA', 'CIS Controls', 'SAMA Cybersecurity Framework'].map((std) => (
              <button 
                key={std} 
                onClick={() => setActiveStandard(std)}
                className={`px-6 py-3 rounded-xl font-bold text-[16px] tracking-wide border transition-all duration-300 transform outline-none
                  ${activeStandard === std 
                    ? 'bg-[#1a2340] text-white border-[#1a2340] md:scale-105 shadow-md' 
                    : 'bg-[#f4f6f9] text-[#1a2340] border-gray-200 hover:bg-[#fde68a]/60 hover:border-[#fde68a] hover:-translate-y-1'
                  }`}
              >
                {std}
              </button>
            ))}
          </div>
        </section>

        {/* DETAILS - CONFIG REVIEWS */}
        <div className="flex flex-col w-full">
          {/* Configuration Review */}
          <section className="bg-[#1a2340] text-white rounded-2xl p-10 shadow-md relative overflow-hidden">
            <div className="relative z-10 space-y-6">
              <h2 className="text-[28px] font-bold text-white">Configuration Review</h2>
              <div className="w-12 h-1 bg-[#f5c842] rounded-full"></div>
              <p className="text-[16px] text-gray-300 leading-relaxed">
                Connect compliance directly to your operational reality. Our platform helps you assess technical and security configurations in real-time, deliberately detecting weak settings across cloud, network, and endpoint environments.
              </p>
              <p className="text-[16px] text-gray-300 leading-relaxed">
                Automatically map these weaknesses to compliance impact, allowing engineers to instantly see exactly which framework controls are jeopardized by a single misconfiguration.
              </p>
            </div>
            {/* Background decoration */}
            <svg className="absolute -bottom-10 -right-10 opacity-10" width="200" height="200" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
            </svg>
          </section>
        </div>

        {/* CTA */}
        <section className="w-full bg-[#f4f6f9] border border-gray-200 rounded-3xl p-12 text-center flex flex-col items-center">
          <h2 className="text-[32px] font-bold text-[#1a2340] mb-4">Ready to Transform Your Compliance?</h2>
          <p className="text-gray-500 mb-8 max-w-[500px]">Join us and streamline your GRC operations, identify configuration gaps effortlessly, and maintain a seamless path to audit readiness.</p>
          <Link href="/onboarding" className="inline-block bg-[#1a2340] !text-white visited:!text-white hover:!text-white active:!text-white focus:!text-white px-10 py-4 rounded-full text-[18px] hover:bg-[#253654] transition-all shadow-md hover:shadow-lg hover:-translate-y-0.5">
            <span className="!text-white font-[600]">Get Started Today</span>
          </Link>
        </section>

      </div>
    </div>
  );
}
