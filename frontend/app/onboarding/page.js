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
    agreesToTerms: false,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e) => {
    const value = e.target.type === "checkbox" ? e.target.checked : e.target.value;
    setFormData({ ...formData, [e.target.name]: value });
  };

  const countries = [
    "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda", "Argentina", "Armenia", "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Congo", "Costa Rica", "Croatia", "Cuba", "Cyprus", "Czech Republic", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania", "Luxembourg", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Monaco", "Mongolia", "Montenegro", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Korea", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Palestine", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Qatar", "Romania", "Russia", "Rwanda", "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", "Samoa", "San Marino", "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Korea", "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "Taiwan", "Tajikistan", "Tanzania", "Thailand", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan", "Tuvalu", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Vatican City", "Venezuela", "Vietnam", "Yemen", "Zambia", "Zimbabwe"
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
      const res = await fetch("http://localhost:8000/request-access", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          company_name: formData.companyName,
          email: formData.workEmail,
          organization_type: formData.companyType,
          sector: formData.country,
          notes: formData.employeeName
        }),
      });

      console.log("Content-Type:", res.headers.get("content-type"));
      if (res.headers.get("content-type")?.includes("text/html")) {
        console.error("API returned HTML instead of JSON for /request-access");
        throw new Error("API returned HTML instead of JSON");
      }
      if (!res.ok) {
        const text = await res.text();
        console.error("API ERROR RESPONSE:", text);
        throw new Error("API request failed");
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
                className="w-full px-4 py-3 rounded-lg border border-[#D1D5DB] bg-[#FFFFFF] text-[#111827] placeholder-[#9CA3AF] outline-none focus:border-[#111936] focus:ring-1 focus:ring-[#111936] transition-colors text-[15px]" 
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
                className="w-full px-4 py-3 rounded-lg border border-[#D1D5DB] bg-[#FFFFFF] text-[#111827] placeholder-[#9CA3AF] outline-none focus:border-[#111936] focus:ring-1 focus:ring-[#111936] transition-colors text-[15px]" 
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
              className="w-full px-4 py-3 rounded-lg border border-[#D1D5DB] bg-[#FFFFFF] text-[#111827] placeholder-[#9CA3AF] outline-none focus:border-[#111936] focus:ring-1 focus:ring-[#111936] transition-colors text-[15px]" 
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
                className="w-full px-4 py-3 rounded-lg border border-[#D1D5DB] bg-[#FFFFFF] text-[#111827] outline-none focus:border-[#111936] focus:ring-1 focus:ring-[#111936] transition-colors text-[15px]"
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
                className="w-full px-4 py-3 rounded-lg border border-[#D1D5DB] bg-[#FFFFFF] text-[#111827] outline-none focus:border-[#111936] focus:ring-1 focus:ring-[#111936] transition-colors text-[15px]"
              >
                <option value="" disabled>Select Country</option>
                {countries.map(c => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Message field removed per user request */}

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
