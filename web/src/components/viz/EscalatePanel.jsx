import { fmtLt } from "../../steps.js";
import SourceTags from "../SourceTags.jsx";
import TransformerBar from "./TransformerBar.jsx";

export default function EscalatePanel({ pkg, audit = [] }) {
  if (!pkg) return null;
  const n = pkg.numbers || {};
  return (
    <div className="section escalate-pack">
      <h3>Inžinieriaus perdavimo paketas</h3>
      <p className="hint bad-hint">{pkg.reason || (pkg.reasons || []).join(" ")}</p>
      <div className="num-compare">
        <div className="num bad">
          <b>{fmtLt(n.after_kw)} kW</b>
          <span>po prijungimo</span>
        </div>
        <div className="num-vs">vs</div>
        <div className="num">
          <b>{fmtLt(n.limit_80_kw, 0)} kW</b>
          <span>80 % riba</span>
        </div>
        <div className="num">
          <b>+{fmtLt(n.over_kw)} kW</b>
          <span>viršijimas</span>
        </div>
      </div>
      <div className="kv">
        <div><b>Viršūnė</b><span>{fmtLt(n.peak_kw)} kW</span></div>
        <div><b>Prašoma</b><span>{fmtLt(n.requested_kw, 0)} kW</span></div>
        <div><b>90 % riba</b><span>{fmtLt(n.limit_90_kw, 0)} kW</span></div>
        <div><b>Nepraėjo</b><span>{pkg.failed_at}</span></div>
      </div>
      <p className="hint" style={{ marginTop: 12 }}><b>Kitas žingsnis.</b> {pkg.suggested_next}</p>
      <TransformerBar bar={pkg.attachments?.transformer_bar} pass={false} />
      <p className="map-note">{pkg.safety} <SourceTags tags={pkg.attachments?.source_tags || ["rule", "real"]} /></p>
      {audit.length > 0 && (
        <div className="section">
          <h3>Auditas</h3>
          <ul className="compact-list">
            {audit.map((a, i) => (
              <li key={i}><b>{a.action}</b> — {a.reason}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
