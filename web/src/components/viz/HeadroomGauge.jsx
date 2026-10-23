import { fmtLt } from "../../steps.js";

export default function HeadroomGauge({ gauge }) {
  if (!gauge) return null;
  const max = gauge.limit_80_kw || 320;
  const used = (gauge.after_kw || 0) + (gauge.pending_kw || 0);
  const frac = Math.max(0, Math.min(1, used / max));
  const r = 64, cx = 80, cy = 80;
  const polar = (t) => {
    const a = Math.PI * (1 - t);
    return [cx + r * Math.cos(a), cy - r * Math.sin(a)];
  };
  const [x, y] = polar(frac);
  return (
    <div className="section">
      <h3>Atsarga iki 80 %</h3>
      <svg className="gauge" viewBox="0 0 160 100">
        <path d="M16 80 A64 64 0 0 1 144 80" fill="none" stroke="#eee" strokeWidth="12" strokeLinecap="round" />
        <path d={`M16 80 A64 64 0 0 1 ${x} ${y}`} fill="none" stroke={gauge.headroom_kw >= 0 ? "#1f9d61" : "#e11d48"} strokeWidth="12" strokeLinecap="round" />
        <text x="80" y="72" textAnchor="middle" fontSize="16" fontWeight="700">{fmtLt(gauge.headroom_kw, 1)}</text>
        <text x="80" y="90" textAnchor="middle" fontSize="10" fill="#6f6f78">kW liko</text>
      </svg>
      <div className="kv">
        <div><b>Po prijungimo</b><span>{fmtLt(gauge.after_kw)} kW</span></div>
        <div><b>Rezervuota</b><span>{fmtLt(gauge.pending_kw, 0)} kW</span></div>
      </div>
    </div>
  );
}
