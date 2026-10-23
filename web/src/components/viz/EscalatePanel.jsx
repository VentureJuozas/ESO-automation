import { fmtLt } from "../../steps.js";
import SourceTags from "../SourceTags.jsx";
import TransformerBar from "./TransformerBar.jsx";

export default function EscalatePanel({ pkg, audit = [], runId }) {
  if (!pkg) return null;
  const n = pkg.numbers || {};
  const brief = pkg.brief || {};
  const options = brief.options || [];
  const impact = brief.pending_impact || {};
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
      {options.length > 0 && (
        <div className="brief-block">
          <div className="ts-toolbar">
            <h3>Stiprinimo paketas, 5 pakopa</h3>
            {runId && (
              <a className="go" href={`/api/runs/${runId}/brief.html`} target="_blank" rel="noreferrer">A4 / PDF</a>
            )}
          </div>
          {options.map((o) => (
            <article key={o.id} className={`brief-opt${o.recommended ? " rec" : ""}`}>
              <header>
                <b>{o.title}</b>
                {o.recommended && <span className="badge ok">Rekomenduojama</span>}
                <span className="badge">{o.tag}</span>
              </header>
              <p>{o.why}</p>
              <div className="kv">
                <div><b>Kaina</b><span>{o.cost_lo}–{o.cost_hi} {o.currency} (inferred)</span></div>
                <div><b>Savininkas</b><span>{o.owner}</span></div>
              </div>
              <p className="hint"><b>Kitas žingsnis.</b> {o.next_step}</p>
            </article>
          ))}
          <p className="hint">{impact.note}</p>
          <p className="map-note">{brief.disclaimer}</p>
        </div>
      )}
      {!options.length && <p className="hint" style={{ marginTop: 12 }}><b>Kitas žingsnis.</b> {pkg.suggested_next}</p>}
      <TransformerBar bar={pkg.attachments?.transformer_bar} pass={false} />
      <p className="map-note">{pkg.safety || brief.safety} <SourceTags tags={pkg.attachments?.source_tags || ["rule", "real", "inferred"]} /></p>
      {runId && (
        <p className="inbox-actions">
          <a className="go" href={`/api/runs/${runId}/audit.html`} target="_blank" rel="noreferrer">Audito HTML</a>
          <a className="go" href={`/api/runs/${runId}/audit.json`} target="_blank" rel="noreferrer">Audito JSON</a>
        </p>
      )}
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
