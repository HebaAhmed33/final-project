"use client";

import { useEffect, useState } from "react";

export default function AdminClientsPage() {
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchClients() {
      try {
        const res = await fetch("http://localhost:8000/api/onboarding");
        console.log("Content-Type:", res.headers.get("content-type"));
        if (res.headers.get("content-type")?.includes("text/html")) {
          console.error("API returned HTML instead of JSON for /api/onboarding");
          throw new Error("API returned HTML instead of JSON");
        }
        if (!res.ok) {
          const text = await res.text();
          console.error("API ERROR RESPONSE:", text);
          throw new Error("API request failed");
        }
        const data = await res.json();
        setClients(data);
      } catch (err) {
        console.error(err);
        setError("Could not load client submissions.");
      } finally {
        setLoading(false);
      }
    }
    
    fetchClients();
  }, []);

  return (
    <div className="min-h-screen bg-[#f4f6f9] p-8 md:p-12">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-[32px] font-extrabold text-[#1a2340]">Onboarding Submissions</h1>
          <p className="text-gray-500 mt-2">View and manage clients who completed the onboarding flow.</p>
        </div>

        {error && (
          <div className="bg-red-50 text-red-600 p-4 rounded-lg mb-6 border border-red-100">
            {error}
          </div>
        )}

        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-100 text-[#1a2340] text-[13px] uppercase tracking-wider font-bold">
                  <th className="px-6 py-4">Employee Name</th>
                  <th className="px-6 py-4">Email</th>
                  <th className="px-6 py-4">Company Name</th>
                  <th className="px-6 py-4">Company Type</th>
                  <th className="px-6 py-4">Country</th>
                  <th className="px-6 py-4 max-w-[200px]">Message</th>
                  <th className="px-6 py-4">Created At</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 text-[14px] text-gray-700">
                {loading ? (
                  <tr>
                    <td colSpan="7" className="px-6 py-12 text-center text-gray-400">Loading submissions...</td>
                  </tr>
                ) : clients.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="px-6 py-12 text-center text-gray-400">No onboarding submissions found.</td>
                  </tr>
                ) : (
                  clients.map(client => (
                    <tr key={client.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 font-medium text-[#1a2340]">{client.employeeName}</td>
                      <td className="px-6 py-4">{client.workEmail}</td>
                      <td className="px-6 py-4">{client.companyName}</td>
                      <td className="px-6 py-4">
                        <span className="inline-block px-3 py-1 bg-[#1a2340]/5 text-[#1a2340] rounded-full text-[12px] font-semibold">
                          {client.companyType}
                        </span>
                      </td>
                      <td className="px-6 py-4">{client.country}</td>
                      <td className="px-6 py-4 max-w-[200px] truncate" title={client.message}>
                        {client.message || <span className="text-gray-300 italic">None</span>}
                      </td>
                      <td className="px-6 py-4 text-gray-500 whitespace-nowrap">
                        {new Date(client.createdAt).toLocaleDateString()}{" "}
                        {new Date(client.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
