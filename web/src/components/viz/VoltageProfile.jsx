export default function VoltageProfile({ profile = [], limit = 207 }) {
  if (!profile.length) return <p className="empty">No profile.</p>;
  const w = 520, h = 180, p = 28;
  const xs = profile.map((pt) => pt.m);
  const ys = profile.flatMap((pt) => [pt.v_before, pt.v_after]);
  const minX = 0, maxX = Math.max(...xs, 1);
  const minY = Math.min(limit - 5, ...ys) - 2;
  const maxY = Math.max(232, ...ys) + 2;
  const X = (m) => p + ((m - minX) / (maxX - minX)) * (w - 2 * p);
  const Y = (v) => h - p - ((v - minY) / (maxY - minY)) * (h - 2 * p);
  const path = (key) => profile.map((pt, i) => `${i ? "L" : "M"} ${X(pt.m)} ${Y(pt[key])}`).join(" ");
  return (
    <div className="section">
      <svg className="chart" viewBox={`0 0 ${w} ${h}`} role="img" aria-label="Voltage before and after">
        <line x1={p} y1={Y(limit)} x2={w - p} y2={Y(limit)} stroke="#e11d48" strokeDasharray="4 4" />
        <text x={w - p} y={Y(limit) - 4} textAnchor="end" fontSize="10" fill="#e11d48">207 V</text>
        <path d={path("v_before")} fill="none" stroke="#94a3b8" strokeWidth="2" />
        <path d={path("v_after")} fill="none" stroke="#1f9d61" strokeWidth="2.4" />
        {profile.map((pt) => (
          <g key={pt.label}>
            <circle cx={X(pt.m)} cy={Y(pt.v_after)} r={pt.kind === "connection" ? 5 : 3} fill={pt.kind === "connection" ? "#ff6d5a" : "#1f9d61"} />
            <text x={X(pt.m)} y={h - 8} textAnchor="middle" fontSize="9" fill="#6f6f78">{pt.label}</text>
          </g>
        ))}
      </svg>
      <p className="bar-legend"><span>Grey — before</span><span>Green — after</span><span>Coral — connection</span></p>
      <p className="formula">V = 230 × (1 − ΣΔU/100) ≥ 207 V</p>
    </div>
  );
}
