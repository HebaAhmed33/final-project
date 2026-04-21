"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function OnboardingPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    employeeName: "",
    workEmail: "",
    companyName: "",
    companyType: "",
    country: "",
    message: "",
    agreesToTerms: false,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e) => {
    const value = e.target.type === "checkbox" ? e.target.checked : e.target.value;
    setFormData({ ...formData, [e.target.name]: value });
  };

  const countries = [
    "United States", "United Kingdom", "Canada", "Australia", 
    "Saudi Arabia", "United Arab Emirates", "Germany", "France", 
    "India", "Japan", "Brazil", "Other"
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!formData.agreesToTerms) {
      setError("You must agree to the Terms & Conditions.");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch("/api/onboarding", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (!res.ok) {
        throw new Error("Failed to submit onboarding form");
      }
      
      // Simulate typical SaaS behavior setting some user context
      localStorage.setItem("smartisms_user", JSON.stringify({ 
        onboarded: true, 
        email: formData.workEmail, 
        name: formData.employeeName,
        companyName: formData.companyName
      }));
      
      router.push("/workspace");
    } catch (err) {
      console.error(err);
      setError("An error occurred during submission. Please try again.");
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-80px)] flex flex-col justify-center items-center py-16 px-6 bg-[#f4f6f9]">
      <div className="w-full max-w-[600px] bg-white rounded-2xl shadow-[0_10px_40px_-10px_rgba(26,35,64,0.1)] p-8 md:p-12 border border-gray-100">
        <div className="mb-8 text-center">
          <h1 className="text-[32px] font-extrabold text-[#1a2340] mb-2 tracking-tight">Get Started with Aegis.One</h1>
          <p className="text-[16px] text-gray-500">Provide a few details to customize your GRC experience.</p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-100 text-red-600 rounded-lg text-sm text-center">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="flex flex-col space-y-2">
              <label className="text-[14px] font-[600] text-[#1a2340]">Employee Name *</label>
              <input 
                type="text" 
                name="employeeName" 
                required 
                value={formData.employeeName} 
                onChange={handleChange}
                placeholder="John Doe"
                className="w-full px-4 py-3 rounded-lg border border-gray-200 outline-none focus:border-[#f5c842] focus:ring-1 focus:ring-[#f5c842] transition-colors text-[15px]" 
              />
            </div>
            <div className="flex flex-col space-y-2">
              <label className="text-[14px] font-[600] text-[#1a2340]">Work Email *</label>
              <input 
                type="email" 
                name="workEmail" 
                required 
                value={formData.workEmail} 
                onChange={handleChange}
                placeholder="john@company.com"
                className="w-full px-4 py-3 rounded-lg border border-gray-200 outline-none focus:border-[#f5c842] focus:ring-1 focus:ring-[#f5c842] transition-colors text-[15px]" 
              />
            </div>
          </div>

          <div className="flex flex-col space-y-2">
            <label className="text-[14px] font-[600] text-[#1a2340]">Company Name *</label>
            <input 
              type="text" 
              name="companyName" 
              required 
              value={formData.companyName} 
              onChange={handleChange}
              placeholder="Acme Corp"
              className="w-full px-4 py-3 rounded-lg border border-gray-200 outline-none focus:border-[#f5c842] focus:ring-1 focus:ring-[#f5c842] transition-colors text-[15px]" 
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="flex flex-col space-y-2">
              <label className="text-[14px] font-[600] text-[#1a2340]">Company Type *</label>
              <select 
                name="companyType" 
                required 
                value={formData.companyType} 
                onChange={handleChange}
                className="w-full px-4 py-3 rounded-lg border border-gray-200 outline-none focus:border-[#f5c842] focus:ring-1 focus:ring-[#f5c842] transition-colors bg-white text-[15px]"
              >
                <option value="" disabled>Select Type</option>
                <option value="Startup">Startup</option>
                <option value="Small Business">Small Business</option>
                <option value="Enterprise">Enterprise</option>
                <option value="Government">Government</option>
                <option value="Financial Services">Financial Services</option>
                <option value="Healthcare">Healthcare</option>
                <option value="Technology">Technology</option>
                <option value="Other">Other</option>
              </select>
            </div>
            <div className="flex flex-col space-y-2">
              <label className="text-[14px] font-[600] text-[#1a2340]">Country *</label>
              <select 
                name="country" 
                required 
                value={formData.country} 
                onChange={handleChange}
                className="w-full px-4 py-3 rounded-lg border border-gray-200 outline-none focus:border-[#f5c842] focus:ring-1 focus:ring-[#f5c842] transition-colors bg-white text-[15px]"
              >
                <option value="" disabled>Select Country</option>
                {countries.map(c => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex flex-col space-y-2">
            <label className="text-[14px] font-[600] text-[#1a2340]">Message / Requirements <span className="text-gray-400 font-normal">(Optional)</span></label>
            <textarea 
              name="message" 
              rows="3" 
              value={formData.message} 
              onChange={handleChange}
              placeholder="Tell us about your specific GRC needs..."
              className="w-full px-4 py-3 rounded-lg border border-gray-200 outline-none focus:border-[#f5c842] focus:ring-1 focus:ring-[#f5c842] transition-colors text-[15px] resize-none" 
            />
          </div>

          <div className="flex items-start gap-3 mt-4">
            <input 
              type="checkbox" 
              id="agreesToTerms" 
              name="agreesToTerms" 
              required
              checked={formData.agreesToTerms} 
              onChange={handleChange}
              className="mt-1 w-4 h-4 text-[#1a2340] border-gray-300 rounded focus:ring-[#1a2340]" 
            />
            <label htmlFor="agreesToTerms" className="text-[14px] text-gray-600 leading-relaxed cursor-pointer select-none">
              I agree to the <span className="text-[#1a2340] font-semibold hover:underline">Terms & Conditions</span> and <span className="text-[#1a2340] font-semibold hover:underline">Privacy Policy</span>.
            </label>
          </div>

          <button 
            type="submit" 
            disabled={loading}
            className={`w-full py-4 px-6 rounded-xl font-bold text-white text-[16px] transition-all shadow-md  
              ${loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-[#1a2340] hover:bg-[#253654] hover:shadow-lg hover:-translate-y-0.5'}`}
          >
            {loading ? "Processing..." : "Next"}
          </button>
        </form>
      </div>
    </div>
  );
}
