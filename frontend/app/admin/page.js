"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function AdminDashboard() {
  const router = useRouter();
  const [adminUser, setAdminUser] = useState(null);

  useEffect(() => {
    const user = localStorage.getItem("admin_user");
    if (!user) {
      router.replace("/admin-login");
    } else {
      setAdminUser(JSON.parse(user));
    }
  }, [router]);

  if (!adminUser) return null;

  return (
    <div className="min-h-screen bg-[#F7F8FC]">
      <nav className="bg-[#151B3A] text-white px-6 py-4 flex justify-between items-center shadow-md">
        <div className="flex items-center gap-3">
          <div className="bg-white/10 p-2 rounded-lg">
            <svg width="20" height="20" fill="none" stroke="#fce69a" strokeWidth="2.5" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <span className="font-bold text-lg tracking-wide">Aegis Admin</span>
        </div>
        <button 
          onClick={() => {
            localStorage.removeItem("admin_user");
            router.push("/");
          }}
          className="text-sm font-semibold bg-white/10 hover:bg-white/20 px-4 py-2 rounded-lg transition-colors"
        >
          Logout
        </button>
      </nav>

      <main className="max-w-6xl mx-auto p-8">
        <header className="mb-8">
          <h1 className="text-3xl font-black text-[#111936]">Dashboard</h1>
          <p className="text-gray-500 mt-2">Welcome back, {adminUser.email}!</p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col">
            <span className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-2">Total Organizations</span>
            <span className="text-4xl font-black text-[#111936]">124</span>
            <span className="text-sm text-green-600 font-semibold mt-4">↑ 12% this month</span>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col">
            <span className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-2">Active Assessments</span>
            <span className="text-4xl font-black text-[#E97A3B]">45</span>
            <span className="text-sm text-gray-500 font-semibold mt-4">In progress</span>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col">
            <span className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-2">System Health</span>
            <div className="flex items-center gap-3 mt-1">
              <span className="relative flex h-5 w-5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-5 w-5 bg-green-500"></span>
              </span>
              <span className="text-2xl font-black text-[#59A26A]">Optimal</span>
            </div>
            <span className="text-sm text-gray-500 font-semibold mt-3">All services running</span>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="px-6 py-5 border-b border-gray-100 flex justify-between items-center bg-slate-50">
            <h2 className="text-lg font-bold text-[#111936]">Recent Activity</h2>
          </div>
          <div className="divide-y divide-gray-100">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="px-6 py-4 flex items-center justify-between hover:bg-slate-50 transition-colors">
                <div>
                  <p className="text-sm font-semibold text-[#111936]">New assessment run completed</p>
                  <p className="text-xs text-gray-500 mt-1">Acme Corp • ISO 27001 Pipeline</p>
                </div>
                <span className="text-xs font-bold text-gray-400">{i * 2} hours ago</span>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
