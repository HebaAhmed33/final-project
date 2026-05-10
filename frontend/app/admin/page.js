"use client";
import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";

import API_BASE_URL from "../lib/api";

const S = {
  page: { minHeight:"100vh", background:"var(--bg-main)", color:"var(--text-main)", fontFamily:"'Inter','Segoe UI',sans-serif", transition: "background 0.3s, color 0.3s" },
  nav: { background:"var(--bg-card)", borderBottom:"1px solid var(--border-color)", padding:"0 2rem", height:"60px", display:"flex", alignItems:"center", justifyContent:"space-between", position:"sticky", top:0, zIndex:50, transition: "background 0.3s, border-color 0.3s" },
  navBrand: { display:"flex", alignItems:"center", gap:"0.6rem", fontWeight:700, fontSize:"1.1rem", color:"var(--text-main)" },
  main: { maxWidth:"1400px", margin:"0 auto", padding:"1.5rem 2rem 3rem" },
  grid6: { display:"grid", gridTemplateColumns:"repeat(auto-fit,minmax(190px,1fr))", gap:"0.75rem", marginBottom:"1.5rem" },
  card: { background:"var(--bg-card)", border:"1px solid var(--border-color)", borderRadius:"0.75rem", padding:"1.25rem", boxShadow:"var(--shadow-card)", transition: "background 0.3s, border-color 0.3s, box-shadow 0.3s" },
  statVal: { fontSize:"2rem", fontWeight:800, lineHeight:1.1 },
  statLabel: { fontSize:"0.75rem", fontWeight:600, textTransform:"uppercase", letterSpacing:"0.05em", color:"var(--text-muted)", marginBottom:"0.5rem" },
  sTitle: { fontSize:"1.15rem", fontWeight:700, color:"var(--text-main)", marginBottom:"1rem", display:"flex", alignItems:"center", gap:"0.5rem" },
  tbl: { width:"100%", borderCollapse:"collapse", fontSize:"0.82rem" },
  th: { padding:"0.6rem 0.75rem", textAlign:"left", color:"var(--text-muted)", fontWeight:600, fontSize:"0.7rem", textTransform:"uppercase", letterSpacing:"0.06em", borderBottom:"1px solid var(--border-color)" },
  td: { padding:"0.6rem 0.75rem", borderBottom:"1px solid var(--border-color)", color:"var(--text-secondary)" },
  badge: (c) => ({ display:"inline-block", padding:"0.15rem 0.5rem", borderRadius:"999px", fontSize:"0.7rem", fontWeight:600, background:`${c}18`, color:c, border:`1px solid ${c}30` }),
  searchInput: { width:"100%", padding:"0.6rem 0.85rem", borderRadius:"0.5rem", border:"1px solid var(--border-color)", background:"var(--input-bg)", color:"var(--input-text)", fontSize:"0.85rem", outline:"none", marginBottom:"0.75rem", transition: "background 0.3s, border-color 0.3s, color 0.3s" },
  tabBtn: (a) => ({ padding:"0.45rem 1rem", borderRadius:"0.5rem", border:"1px solid transparent", cursor:"pointer", fontSize:"0.8rem", fontWeight:600, background:a?"var(--primary)":"transparent", color:a?"white":"var(--text-muted)", transition:"all 0.2s" }),
  actBtn: (c,bg) => ({ padding:"0.35rem 0.65rem", borderRadius:"0.35rem", border:`1px solid ${c}40`, background:bg||`${c}12`, color:c, fontSize:"0.7rem", fontWeight:600, cursor:"pointer", marginRight:"0.25rem", transition:"all 0.2s" }),
  modal: { position:"fixed", inset:0, zIndex:100, display:"flex", alignItems:"center", justifyContent:"center", background:"rgba(0,0,0,0.5)", backdropFilter:"blur(2px)" },
  modalBox: { background:"var(--bg-card)", border:"1px solid var(--border-color)", borderRadius:"0.75rem", padding:"1.5rem", maxWidth:"550px", width:"90%", maxHeight:"80vh", overflow:"auto", boxShadow:"var(--shadow-card)" },
};

const TABS = ["Overview","Companies","Assessments","Config Reviews","Activity Log"];
const TC = { onboarding:"#22c55e", assessment:"#3b82f6", config_upload:"#f59e0b", live_scan:"#8b5cf6", report:"#ec4899", login:"#06b6d4", login_failed:"#ef4444", admin_action:"#f97316", live_scan_failed:"#ef4444", system:"#64748b" };
const TL = { onboarding:"Onboarding", assessment:"Assessment", config_upload:"Config Review", live_scan:"Live Scan", report:"Report", login:"Login", login_failed:"Login Failed", admin_action:"Admin Action", live_scan_failed:"Scan Failed", system:"System" };

function fmt(ts) { if(!ts) return "—"; try { const d=new Date(ts); return d.toLocaleDateString("en-US",{month:"short",day:"numeric",year:"numeric"})+" "+d.toLocaleTimeString("en-US",{hour:"2-digit",minute:"2-digit"}); } catch{ return ts; } }
function scoreBadge(s) { if(s==null) return <span style={S.badge("#64748b")}>N/A</span>; const c=s>=80?"#22c55e":s>=60?"#f59e0b":"#ef4444"; return <span style={S.badge(c)}>{s}%</span>; }
function riskBadge(r) { const c={High:"#ef4444",Medium:"#f59e0b",Low:"#22c55e"}[r]||"#64748b"; return <span style={S.badge(c)}>{r||"N/A"}</span>; }

export default function AdminDashboard() {
  const router = useRouter();
  const [adminUser, setAdminUser] = useState(null);
  const [tab, setTab] = useState("Overview");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [modal, setModal] = useState(null); // {type, data}
  const [actionMsg, setActionMsg] = useState(null);
  const [theme, setTheme] = useState("light");

  const loadData = useCallback(() => {
    fetch(`${API_BASE_URL}/admin/dashboard`).then(r=>r.json()).then(d=>{setData(d);setLoading(false);}).catch(()=>setLoading(false));
  }, []);

  useEffect(() => {
    const u = localStorage.getItem("admin_user");
    if(!u){router.replace("/admin-login");return;}
    setAdminUser(JSON.parse(u));
    loadData();
    
    // Initialize Theme
    const savedTheme = localStorage.getItem("theme") || "light";
    setTheme(savedTheme);
    document.documentElement.setAttribute("data-theme", savedTheme);
  }, [router, loadData]);

  const toggleTheme = () => {
    const next = theme === "light" ? "dark" : "light";
    setTheme(next);
    localStorage.setItem("theme", next);
    document.documentElement.setAttribute("data-theme", next);
  };

  const doAction = async (url, method="POST") => {
    try {
      const r = await fetch(`${API_BASE_URL}${url}`, {method});
      const d = await r.json();
      if(r.ok) { setActionMsg({ok:true,text:d.message||"Done"}); loadData(); setTimeout(()=>setActionMsg(null),2500); }
      else { setActionMsg({ok:false,text:d.detail||"Failed"}); setTimeout(()=>setActionMsg(null),3000); }
    } catch(e) { setActionMsg({ok:false,text:"Network error"}); setTimeout(()=>setActionMsg(null),3000); }
    setModal(null);
  };

  if(!adminUser) return null;
  const s = data?.stats || {};
  const q = search.toLowerCase();

  const Stat = ({label,value,color="#3b82f6"}) => (
    <div style={S.card}><div style={S.statLabel}>{label}</div><div style={{...S.statVal,color}}>{loading?"…":value}</div></div>
  );

  // Detail modal
  const DetailModal = () => {
    if(!modal) return null;
    const {type,data:md} = modal;
    return (
      <div style={S.modal} onClick={()=>setModal(null)}>
        <div style={S.modalBox} onClick={e=>e.stopPropagation()}>
          <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:"1rem"}}>
            <h3 style={{fontSize:"1.1rem",fontWeight:700,color:"var(--text-main)",margin:0}}>
              {type==="client"?"Client Details":type==="assessment"?"Assessment Details":type==="config"?"Config Review Details":"Details"}
            </h3>
            <button onClick={()=>setModal(null)} style={{background:"none",border:"none",color:"var(--text-muted)",cursor:"pointer",fontSize:"1.2rem"}}>✕</button>
          </div>
          <div style={{display:"flex",flexDirection:"column",gap:"0.5rem",fontSize:"0.85rem"}}>
            {Object.entries(md||{}).filter(([k])=>!["parsed_config","config_analysis","config_compliance","severity_summary","top_missing_high_risk"].includes(k)).map(([k,v])=>(
              <div key={k} style={{display:"flex",gap:"0.5rem",padding:"0.35rem 0",borderBottom:"1px solid var(--border-color)"}}>
                <span style={{color:"var(--text-muted)",minWidth:"140px",fontWeight:600,fontSize:"0.78rem",textTransform:"uppercase"}}>{k.replace(/_/g," ")}</span>
                <span style={{color:"var(--text-main)",wordBreak:"break-all"}}>{typeof v==="object"?JSON.stringify(v):String(v??"—")}</span>
              </div>
            ))}
          </div>
          {/* Action buttons inside modal */}
          <div style={{display:"flex",gap:"0.5rem",marginTop:"1.25rem",paddingTop:"1rem",borderTop:"1px solid var(--border-color)"}}>
            {type==="client" && md.status!=="banned" && <button onClick={()=>doAction(`/admin/clients/${md.id}/ban`)} style={S.actBtn("#f59e0b")}>Ban User</button>}
            {type==="client" && md.status==="banned" && <button onClick={()=>doAction(`/admin/clients/${md.id}/unban`)} style={S.actBtn("#22c55e")}>Unban User</button>}
            {type==="client" && <button onClick={()=>{if(confirm("Permanently delete this client?"))doAction(`/admin/clients/${md.id}`,"DELETE")}} style={S.actBtn("#ef4444")}>Delete</button>}
            {type==="assessment" && <button onClick={()=>{if(confirm("Delete this assessment?"))doAction(`/admin/assessments/${md.id}`,"DELETE")}} style={S.actBtn("#ef4444")}>Delete</button>}
            {type==="config" && <button onClick={()=>{if(confirm("Delete this config review?"))doAction(`/admin/configs/${md.id}`,"DELETE")}} style={S.actBtn("#ef4444")}>Delete</button>}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div style={S.page}>
      <DetailModal />

      {/* Toast */}
      {actionMsg && (
        <div style={{position:"fixed",top:"1rem",right:"1rem",zIndex:200,padding:"0.75rem 1.25rem",borderRadius:"0.5rem",background:actionMsg.ok?"rgba(34,197,94,0.15)":"rgba(239,68,68,0.15)",border:`1px solid ${actionMsg.ok?"#22c55e":"#ef4444"}`,color:actionMsg.ok?"#22c55e":"#ef4444",fontSize:"0.85rem",fontWeight:600}}>
          {actionMsg.text}
        </div>
      )}

      {/* NAV */}
      <nav style={S.nav}>
        <div style={S.navBrand}>
          <div style={{width:32,height:32,borderRadius:"0.5rem",background:"linear-gradient(135deg,#3b82f6,#8b5cf6)",display:"flex",alignItems:"center",justifyContent:"center"}}>
            <svg width="16" height="16" fill="none" stroke="#fff" strokeWidth="2.5" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
          </div>
          SmartISMS Admin
        </div>
        <div style={{display:"flex",alignItems:"center",gap:"1.5rem"}}>
          <button onClick={toggleTheme} style={{background:"none",border:"none",color:"var(--text-secondary)",cursor:"pointer",display:"flex",alignItems:"center",justifyContent:"center"}}>
            {theme === "light" ? (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
            ) : (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
            )}
          </button>
          <span style={{fontSize:"0.8rem",color:"var(--text-muted)"}}>{adminUser.email}</span>
          <button onClick={()=>{localStorage.removeItem("admin_user");router.push("/");}} style={{fontSize:"0.8rem",fontWeight:600,background:"rgba(239,68,68,0.1)",color:"#ef4444",border:"1px solid rgba(239,68,68,0.2)",padding:"0.4rem 1rem",borderRadius:"0.5rem",cursor:"pointer"}}>Logout</button>
        </div>
      </nav>

      <main style={S.main}>
        <div style={{display:"flex",gap:"0.35rem",marginBottom:"1.5rem",flexWrap:"wrap"}}>
          {TABS.map(t=><button key={t} onClick={()=>{setTab(t);setSearch("");}} style={S.tabBtn(tab===t)}>{t}</button>)}
        </div>

        {/* ═══ OVERVIEW ═══ */}
        {tab==="Overview" && <>
          <div style={S.grid6}>
            <Stat label="Companies" value={s.total_companies} color="#3b82f6"/>
            <Stat label="Assessments" value={s.total_assessments} color="#8b5cf6"/>
            <Stat label="Config Reviews" value={s.total_config_reviews} color="#f59e0b"/>
            <Stat label="Live Scans" value={s.total_live_scans} color="#06b6d4"/>
          </div>
          <div style={S.card}>
            <h3 style={S.sTitle}>Recent Activity</h3>
            <table style={S.tbl}><thead><tr>{["Time","Type","Detail","Framework","Score","Actions"].map(h=><th key={h} style={S.th}>{h}</th>)}</tr></thead>
            <tbody>{(data?.activity||[]).slice(0,15).map((a,i)=>(
              <tr key={i}>
                <td style={{...S.td,whiteSpace:"nowrap",fontSize:"0.75rem"}}>{fmt(a.timestamp)}</td>
                <td style={S.td}><span style={S.badge(TC[a.type]||"#64748b")}>{TL[a.type]||a.type}</span></td>
                <td style={{...S.td,maxWidth:280,overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>{a.detail}</td>
                <td style={S.td}>{a.framework||"—"}</td>
                <td style={S.td}>{scoreBadge(a.score)}</td>
                <td style={S.td}><button style={S.actBtn("var(--primary)", "transparent")} onClick={()=>setModal({type:"activity",data:a})}>View</button></td>
              </tr>
            ))}</tbody></table>
          </div>
        </>}

        {/* ═══ COMPANIES ═══ */}
        {tab==="Companies" && <div style={S.card}>
          <h3 style={S.sTitle}>Companies & Users</h3>
          <input style={S.searchInput} placeholder="Search…" value={search} onChange={e=>setSearch(e.target.value)}/>
          <table style={S.tbl}><thead><tr>{["Company","Contact","Email","Type","Status","Date","Actions"].map(h=><th key={h} style={S.th}>{h}</th>)}</tr></thead>
          <tbody>{(data?.clients||[])
            .filter(c=>!q||c.companyName?.toLowerCase().includes(q)||c.workEmail?.toLowerCase().includes(q)||c.employeeName?.toLowerCase().includes(q))
            .sort((a,b)=>new Date(b.createdAt)-new Date(a.createdAt))
            .map((c,i)=>(
              <tr key={i}>
                <td style={{...S.td,fontWeight:600,color:"var(--text-main)"}}>{c.companyName}</td>
                <td style={S.td}>{c.employeeName}</td>
                <td style={S.td}>{c.workEmail}</td>
                <td style={S.td}><span style={S.badge("#3b82f6")}>{c.companyType}</span></td>
                <td style={S.td}>{c.status==="banned"?<span style={S.badge("#ef4444")}>Banned</span>:<span style={S.badge("#22c55e")}>Active</span>}</td>
                <td style={{...S.td,fontSize:"0.75rem",whiteSpace:"nowrap"}}>{fmt(c.createdAt)}</td>
                <td style={S.td}>
                  <button style={S.actBtn("var(--primary)", "transparent")} onClick={()=>setModal({type:"client",data:c})}>View</button>
                  {c.status==="banned"
                    ? <button style={S.actBtn("#22c55e", "transparent")} onClick={()=>doAction(`/admin/clients/${c.id}/unban`)}>Unban</button>
                    : <button style={S.actBtn("#f59e0b", "transparent")} onClick={()=>doAction(`/admin/clients/${c.id}/ban`)}>Ban</button>
                  }
                  <button style={S.actBtn("#ef4444", "transparent")} onClick={()=>{if(confirm(`Delete ${c.employeeName}?`))doAction(`/admin/clients/${c.id}`,"DELETE")}}>Delete</button>
                </td>
              </tr>
            ))}</tbody></table>
        </div>}

        {/* ═══ ASSESSMENTS ═══ */}
        {tab==="Assessments" && <div style={S.card}>
          <h3 style={S.sTitle}>Assessment History</h3>
          <input style={S.searchInput} placeholder="Search…" value={search} onChange={e=>setSearch(e.target.value)}/>
          <table style={S.tbl}><thead><tr>{["Name","Framework","Score","Priority","Controls","Evidence","Date","Actions"].map(h=><th key={h} style={S.th}>{h}</th>)}</tr></thead>
          <tbody>{(data?.assessments||[])
            .filter(a=>!q||a.name?.toLowerCase().includes(q)||a.framework?.toLowerCase().includes(q))
            .sort((a,b)=>(b.created_at||"").localeCompare(a.created_at||""))
            .map((a,i)=>(
              <tr key={i}>
                <td style={{...S.td,fontWeight:600,color:"var(--text-main)"}}>{a.name||"Unnamed"}</td>
                <td style={S.td}><span style={S.badge("#8b5cf6")}>{a.framework}</span></td>
                <td style={S.td}>{scoreBadge(a.score)}</td>
                <td style={S.td}>{riskBadge(a.priority)}</td>
                <td style={S.td}><span style={{fontSize:"0.75rem"}}>{a.compliant}/{a.total_controls}</span></td>
                <td style={S.td}>{a.evidence_used?<span style={S.badge("#22c55e")}>Yes</span>:<span style={S.badge("#64748b")}>No</span>}</td>
                <td style={{...S.td,fontSize:"0.75rem",whiteSpace:"nowrap"}}>{fmt(a.created_at)}</td>
                <td style={S.td}>
                  <button style={S.actBtn("var(--primary)", "transparent")} onClick={()=>setModal({type:"assessment",data:a})}>View</button>
                  <button style={S.actBtn("#ef4444", "transparent")} onClick={()=>{if(confirm(`Delete "${a.name}"?`))doAction(`/admin/assessments/${a.id}`,"DELETE")}}>Delete</button>
                </td>
              </tr>
            ))}</tbody></table>
        </div>}

        {/* ═══ CONFIG REVIEWS ═══ */}
        {tab==="Config Reviews" && <div style={S.card}>
          <h3 style={S.sTitle}>Configuration Reviews & Uploads</h3>
          <input style={S.searchInput} placeholder="Search…" value={search} onChange={e=>setSearch(e.target.value)}/>
          <table style={S.tbl}><thead><tr>{["File","Type","Framework","Risk","Findings","Score","Date","Actions"].map(h=><th key={h} style={S.th}>{h}</th>)}</tr></thead>
          <tbody>{(data?.config_uploads||[])
            .filter(c=>!q||c.file_name?.toLowerCase().includes(q)||c.framework?.toLowerCase().includes(q))
            .sort((a,b)=>(b.created_at||"").localeCompare(a.created_at||""))
            .map((c,i)=>(
              <tr key={i}>
                <td style={{...S.td,fontWeight:600,color:"var(--text-main)",maxWidth:200,overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>{c.file_name}</td>
                <td style={S.td}><span style={S.badge("#06b6d4")}>{c.file_type}</span></td>
                <td style={S.td}>{c.framework||"—"}</td>
                <td style={S.td}>{riskBadge(c.risk)}</td>
                <td style={S.td}>{c.findings}</td>
                <td style={S.td}>{scoreBadge(c.score)}</td>
                <td style={{...S.td,fontSize:"0.75rem",whiteSpace:"nowrap"}}>{fmt(c.created_at)}</td>
                <td style={S.td}>
                  <button style={S.actBtn("var(--primary)", "transparent")} onClick={()=>setModal({type:"config",data:c})}>View</button>
                  <button style={S.actBtn("#ef4444", "transparent")} onClick={()=>{if(confirm(`Delete "${c.file_name}"?`))doAction(`/admin/configs/${c.id}`,"DELETE")}}>Delete</button>
                </td>
              </tr>
            ))}</tbody></table>
        </div>}

        {/* ═══ ACTIVITY LOG ═══ */}
        {tab==="Activity Log" && <div style={S.card}>
          <h3 style={S.sTitle}>Full Activity Log</h3>
          <input style={S.searchInput} placeholder="Search…" value={search} onChange={e=>setSearch(e.target.value)}/>
          <table style={S.tbl}><thead><tr>{["Timestamp","Type","Detail","User/Email","Company","Framework","Score","Actions"].map(h=><th key={h} style={S.th}>{h}</th>)}</tr></thead>
          <tbody>{(data?.activity||[])
            .filter(a => {
              if(!q) return true;
              const detailMatch = (a.detail || "").toLowerCase().includes(q);
              const emailMatch = (a.email || a.user || "").toLowerCase().includes(q);
              const companyMatch = (a.company || "").toLowerCase().includes(q);
              const typeMatch = (TL[a.type] || a.type || "").toLowerCase().includes(q);
              return detailMatch || emailMatch || companyMatch || typeMatch;
            })
            .map((a,i)=>(
              <tr key={i}>
                <td style={{...S.td,whiteSpace:"nowrap",fontSize:"0.75rem"}}>{fmt(a.timestamp)}</td>
                <td style={S.td}><span style={S.badge(TC[a.type]||"#64748b")}>{TL[a.type]||a.type}</span></td>
                <td style={{...S.td,maxWidth:250,overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>{a.detail}</td>
                <td style={S.td}>{a.email||a.user||"—"}</td>
                <td style={S.td}>{a.company||"—"}</td>
                <td style={S.td}>{a.framework||"—"}</td>
                <td style={S.td}>{scoreBadge(a.score)}</td>
                <td style={S.td}><button style={S.actBtn("var(--primary)", "transparent")} onClick={()=>setModal({type:"activity",data:a})}>View</button></td>
              </tr>
            ))}</tbody></table>
        </div>}
      </main>
    </div>
  );
}
