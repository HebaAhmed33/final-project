import React, { useEffect, useState } from 'react';

const ComplianceScoreGauge = ({
  score = 0,
  totalControls = 0,
  compliantControls = 0,
  partialControls = 0,
  missingControls = 0,
  frameworkName = ""
}) => {
  const [animatedScore, setAnimatedScore] = useState(0);

  useEffect(() => {
    const duration = 1000;
    const steps = 60;
    const stepTime = duration / steps;
    let currentStep = 0;
    const targetScore = Math.min(100, Math.max(0, score || 0));

    const timer = setInterval(() => {
      currentStep++;
      const progress = currentStep / steps;
      const easeOut = 1 - Math.pow(1 - progress, 3);
      setAnimatedScore(easeOut * targetScore);
      if (currentStep >= steps) {
        clearInterval(timer);
        setAnimatedScore(targetScore);
      }
    }, stepTime);

    return () => clearInterval(timer);
  }, [score]);

  // Polar to Cartesian coordinate conversion for SVG arcs
  const polarToCartesian = (cx, cy, r, angle) => {
    const rad = (angle - 180) * (Math.PI / 180);
    return {
      x: cx + r * Math.cos(rad),
      y: cy + r * Math.sin(rad)
    };
  };

  const drawArc = (cx, cy, r, startAngle, endAngle) => {
    const start = polarToCartesian(cx, cy, r, startAngle);
    const end = polarToCartesian(cx, cy, r, endAngle);
    // Adjust large arc flag just in case, though segments < 180
    const largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1"; 
    // Sweep flag is 1 for clockwise drawing from start to end mathematically
    return `M ${start.x} ${start.y} A ${r} ${r} 0 ${largeArcFlag} 1 ${end.x} ${end.y}`;
  };

  // Segments definition matches the required percentages of the 180 degree arc
  // 0-49 (50%) -> 180 * 0.50 = 90 deg -> start 0 to 88 (with gap)
  // 50-69 (20%) -> 180 * 0.20 = 36 deg -> start 90 to 124
  // 70-89 (20%) -> 180 * 0.20 = 36 deg -> start 126 to 160
  // 90-99 (9%) -> 180 * 0.09 = 16.2 deg -> start 162 to 176
  // 100 (1%) -> 180 * 0.01 = 1.8 deg -> start 178 to 180
  const segments = [
    { color: '#e53e3e', start: 0, end: 88, label: 'Poor', key: 'poor' },
    { color: '#ed8936', start: 90, end: 124, label: 'Average', key: 'avg' },
    { color: '#ecc94b', start: 126, end: 160, label: 'Good', key: 'good' },
    { color: '#3182ce', start: 162, end: 176, label: 'Very Good', key: 'vgood' },
    { color: '#38a169', start: 178, end: 180, label: 'Excellent', key: 'exc' }
  ];

  const ticks = [
    { val: 0, angle: 0 },
    { val: 50, angle: 90 },
    { val: 70, angle: 126 },
    { val: 90, angle: 162 },
    { val: 99, angle: 177 },
    { val: 100, angle: 180 }
  ];

  const cx = 200;
  const cy = 160;
  const r = 120;

  // Determine Badge/Rating logic
  let rating = "POOR";
  let badgeColor = "#e53e3e";
  if (score >= 100) { rating = "EXCELLENT"; badgeColor = "#38a169"; }
  else if (score >= 90) { rating = "VERY GOOD"; badgeColor = "#3182ce"; }
  else if (score >= 70) { rating = "GOOD"; badgeColor = "#ecc94b"; }
  else if (score >= 50) { rating = "AVERAGE"; badgeColor = "#ed8936"; }

  // Needle smoothly revolves from -90deg to +90deg
  const needleAngle = (animatedScore / 100) * 180 - 90;

  // Progress calculations
  const percComp = totalControls ? ((compliantControls / totalControls) * 100).toFixed(0) : 0;
  const percPart = totalControls ? ((partialControls / totalControls) * 100).toFixed(0) : 0;
  const percMiss = totalControls ? ((missingControls / totalControls) * 100).toFixed(0) : 0;

  return (
    <div style={{ padding: "1.5rem 2rem", background: "var(--bg-card, #1E1E1E)", borderRadius: "12px", border: "1px solid var(--border-color, #333)", color: "var(--text-main, #fff)", width: "100%", boxShadow: "0 10px 25px rgba(0,0,0,0.2)" }}>
      
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" }}>
        <div>
          <div style={{ fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.1em", color: "var(--text-muted, #9CA3AF)", marginBottom: "0.2rem" }}>Overall System Health</div>
          <h2 style={{ margin: 0, fontSize: "1.6rem", fontWeight: "800", color: "var(--text-main, #F9FAFB)" }}>Compliance Score</h2>
          {frameworkName && <div style={{ fontSize: "0.85rem", color: "var(--text-muted, #9CA3AF)", marginTop: "0.2rem" }}>{frameworkName} Assessment</div>}
        </div>
        <div style={{ padding: "0.4rem 1rem", borderRadius: "16px", border: `1px solid ${badgeColor}`, color: badgeColor, fontSize: "0.85rem", fontWeight: "700", letterSpacing: "0.05em", background: `${badgeColor}11`, textTransform: "uppercase" }}>
          {rating}
        </div>
      </div>

      {/* Gauge Visualization */}
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", position: "relative" }}>
        <svg viewBox="0 0 400 180" style={{ width: "100%", maxWidth: "500px", overflow: "visible" }}>
          
          {/* Segments */}
          {segments.map(seg => (
            <path key={seg.key} d={drawArc(cx, cy, r, seg.start, seg.end)} fill="none" stroke={seg.color} strokeWidth="24" />
          ))}
          
          {/* Ticks */}
          {ticks.map(t => {
            const pos = polarToCartesian(cx, cy, r + 24, t.angle);
            return (
              <text key={t.val} x={pos.x} y={pos.y} fill="var(--text-muted, #9CA3AF)" fontSize="11" fontWeight="600" textAnchor="middle" dominantBaseline="middle">
                {t.val}
              </text>
            );
          })}

          {/* Center Display */}
          <text x={cx} y={cy - 20} fill="var(--text-main, #F9FAFB)" fontSize="54" fontWeight="800" textAnchor="middle" letterSpacing="-0.03em">
            {Math.round(animatedScore)}%
          </text>
          <text x={cx} y={cy + 4} fill="var(--text-muted, #9CA3AF)" fontSize="13" fontWeight="700" textAnchor="middle" letterSpacing="0.05em">
            {rating}
          </text>

          {/* Needle Base Pivot */}
          <circle cx={cx} cy={cy} r="8" fill="var(--bg-card, #1E1E1E)" stroke="var(--text-muted, #9CA3AF)" strokeWidth="3" />
          
          {/* Animated Needle */}
          <g transform={`rotate(${needleAngle}, ${cx}, ${cy})`}>
            {/* Draws a needle pointing straight up when angle is 0 (which translates to center top). 
                Tip at cy - r + 15, base extends left/right 5px around cy */}
            <path d={`M ${cx - 6} ${cy} L ${cx + 6} ${cy} L ${cx} ${cy - r + 10} Z`} fill="var(--text-muted, #9CA3AF)" style={{ transition: "all 0.1s linear" }} />
          </g>
        </svg>

        {/* Legend */}
        <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", gap: "1.25rem", marginTop: "1rem", fontSize: "0.85rem", color: "var(--text-muted, #9CA3AF)", fontWeight: 500 }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}><span style={{ width: 10, height: 10, borderRadius: "50%", background: "#e53e3e" }}></span>Poor (&lt;50)</div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}><span style={{ width: 10, height: 10, borderRadius: "50%", background: "#ed8936" }}></span>Average (50-69)</div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}><span style={{ width: 10, height: 10, borderRadius: "50%", background: "#ecc94b" }}></span>Good (70-89)</div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}><span style={{ width: 10, height: 10, borderRadius: "50%", background: "#3182ce" }}></span>Very Good (90-99)</div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}><span style={{ width: 10, height: 10, borderRadius: "50%", background: "#38a169" }}></span>Excellent (100)</div>
        </div>
      </div>

      <hr style={{ border: "none", borderTop: "1px solid var(--border-color, #333)", margin: "1.75rem 0" }} />

      {/* Metrics Row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(130px, 1fr))", gap: "1.25rem", marginBottom: "2rem" }}>
        <div style={{ border: "1px solid var(--border-color, #333)", borderRadius: "8px", padding: "1.25rem", background: "var(--bg-main, #111)" }}>
          <div style={{ fontSize: "0.75rem", color: "var(--text-muted, #9CA3AF)", letterSpacing: "0.05em", textTransform: "uppercase", fontWeight: 700, marginBottom: "0.4rem" }}>Total</div>
          <div style={{ fontSize: "2rem", color: "#60A5FA", fontWeight: "800", lineHeight: "1" }}>{totalControls}</div>
        </div>
        <div style={{ border: "1px solid var(--border-color, #333)", borderRadius: "8px", padding: "1.25rem", background: "var(--bg-main, #111)" }}>
          <div style={{ fontSize: "0.75rem", color: "var(--text-muted, #9CA3AF)", letterSpacing: "0.05em", textTransform: "uppercase", fontWeight: 700, marginBottom: "0.4rem" }}>Compliant</div>
          <div style={{ fontSize: "2rem", color: "#34D399", fontWeight: "800", lineHeight: "1" }}>{compliantControls}</div>
        </div>
        <div style={{ border: "1px solid var(--border-color, #333)", borderRadius: "8px", padding: "1.25rem", background: "var(--bg-main, #111)" }}>
          <div style={{ fontSize: "0.75rem", color: "var(--text-muted, #9CA3AF)", letterSpacing: "0.05em", textTransform: "uppercase", fontWeight: 700, marginBottom: "0.4rem" }}>Missing</div>
          <div style={{ fontSize: "2rem", color: "#F87171", fontWeight: "800", lineHeight: "1" }}>{missingControls}</div>
        </div>
      </div>

      {/* Progress Bars */}
      <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
        
        <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.9rem", color: "var(--text-main, #F9FAFB)", fontWeight: 500 }}>
            <span>Compliant</span>
            <span style={{ fontWeight: 700 }}>{percComp}%</span>
          </div>
          <div style={{ width: "100%", height: "6px", background: "var(--border-color, #333)", borderRadius: "3px", overflow: "hidden" }}>
            <div style={{ width: `${percComp}%`, height: "100%", background: "#48bb78", transition: "width 1s cubic-bezier(0.4, 0, 0.2, 1)" }}></div>
          </div>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.9rem", color: "var(--text-main, #F9FAFB)", fontWeight: 500 }}>
            <span>Partial</span>
            <span style={{ fontWeight: 700 }}>{percPart}%</span>
          </div>
          <div style={{ width: "100%", height: "6px", background: "var(--border-color, #333)", borderRadius: "3px", overflow: "hidden" }}>
            <div style={{ width: `${percPart}%`, height: "100%", background: "#ecc94b", transition: "width 1s cubic-bezier(0.4, 0, 0.2, 1)" }}></div>
          </div>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.9rem", color: "var(--text-main, #F9FAFB)", fontWeight: 500 }}>
            <span>Missing</span>
            <span style={{ fontWeight: 700 }}>{percMiss}%</span>
          </div>
          <div style={{ width: "100%", height: "6px", background: "var(--border-color, #333)", borderRadius: "3px", overflow: "hidden" }}>
            <div style={{ width: `${percMiss}%`, height: "100%", background: "#f56565", transition: "width 1s cubic-bezier(0.4, 0, 0.2, 1)" }}></div>
          </div>
        </div>

      </div>

    </div>
  );
};

export default ComplianceScoreGauge;
