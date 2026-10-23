import { fmtNum } from "../../steps.js";

export default function TransformerBar({ bar, pass }) {
  if (!bar) return null;
  const max = bar.nominal_kw || 400;
  const pct = (v) => `${Math.min(100, (v / max) * 100)}%`;
  return (
    <div className="section">
      <div className="bar-wrap">
        <div className="bar" role="img" aria-label="Transformer load">
          <i style={{ width: pct(bar.before_kw) }} />
          <i className="after" style={{ width: pct(bar.after_kw) }} />
          <span className="mark80" style={{ left: pct(bar.limit_80_kw) }} />
          <span className="mark90" style={{ left: pct(bar.limit_90_kw) }} />
        </div>
        <div className="bar-legend">
          <span>0</span>
          <span>80 % {fmtNum(bar.limit_80_kw, 0)} kW</span>
          <span>90 % {fmtNum(bar.limit_90_kw, 0)}</span>
          <span>{fmtNum(max, 0)} kW</span>
        </div>
      </div>
      <div className="kv">
        <div><b>Before</b><span>{fmtNum(bar.before_kw)} kW</span></div>
        <div><b>After</b><span>{fmtNum(bar.after_kw)} kW {pass ? "· pass" : "· fail"}</span></div>
        <div><b>Coincident</b><span>{fmtNum(bar.coincident_kw, 2)} kW</span></div>
        <div><b>Added</b><span>{fmtNum(bar.added_kw)} kW</span></div>
      </div>
      <p className="formula">P_after = P_peak + P_request = {fmtNum(bar.before_kw)} + {fmtNum(bar.added_kw)} = {fmtNum(bar.after_kw)} kW ≤ 0.8 × 400 kVA (conservative 80 % gate)</p>
      <p className="formula">P_coincident = P_peak + P_request × k(n) = {fmtNum(bar.coincident_kw)} kW (diversified, not the gate)</p>
    </div>
  );
}
