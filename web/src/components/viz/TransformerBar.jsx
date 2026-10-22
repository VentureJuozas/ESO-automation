import { fmtLt } from "../../steps.js";

export default function TransformerBar({ bar, pass }) {
  if (!bar) return null;
  const max = bar.nominal_kw || 400;
  const pct = (v) => `${Math.min(100, (v / max) * 100)}%`;
  return (
    <div className="section">
      <h3>Transformatoriaus apkrova</h3>
      <div className="bar-wrap">
        <div className="bar" role="img" aria-label="Transformatoriaus apkrova prieš ir po">
          <i style={{ width: pct(bar.before_kw) }} />
          <i className="after" style={{ width: pct(bar.after_kw) }} />
          <span className="mark80" style={{ left: pct(bar.limit_80_kw) }} />
          <span className="mark90" style={{ left: pct(bar.limit_90_kw) }} />
        </div>
        <div className="bar-legend">
          <span>0</span>
          <span>80 % {fmtLt(bar.limit_80_kw, 0)} kW</span>
          <span>90 % {fmtLt(bar.limit_90_kw, 0)}</span>
          <span>{fmtLt(max, 0)} kW</span>
        </div>
      </div>
      <div className="kv">
        <div><b>Prieš</b><span>{fmtLt(bar.before_kw)} kW</span></div>
        <div><b>Po (viršūnė + paraiška)</b><span>{fmtLt(bar.after_kw)} kW {pass ? "· telpa" : "· viršija"}</span></div>
        <div><b>Sutaptinė su nesutapimo k.</b><span>{fmtLt(bar.coincident_kw)} kW</span></div>
        <div><b>Pridėta</b><span>{fmtLt(bar.added_kw)} kW</span></div>
      </div>
    </div>
  );
}
