import { fmtLt } from "../../steps.js";
import SourceTags from "../SourceTags.jsx";

function fmtAgent(ms) {
  if (ms == null) return "—";
  if (ms < 1000) return `${ms} ms`;
  return `${(ms / 1000).toFixed(1)} s`;
}

export default function TimeSaved({ comparison, compact = false }) {
  if (!comparison) {
    return (
      <div className="value">
        <div className="v"><b>—</b><span>agento eiga</span></div>
        <div className="v"><b>2–4 val.</b><span>rankinis (prielaida)</span></div>
      </div>
    );
  }
  const maxMin = Math.max(...(comparison.rows || []).map((r) => r.manual_min), 1);
  return (
    <aside className={`time-saved${compact ? " compact" : ""}`}>
      <header>
        <div>
          <div className="kicker">Rankinis vs Agentas</div>
          <h3>Sutaupyta {fmtLt(comparison.saved_min, 0)} min. šiai bylai</h3>
        </div>
        <SourceTags tags={["inferred"]} />
      </header>
      <div className="time-kpis">
        <div className="v"><b>{fmtAgent(comparison.agent_ms)}</b><span>agento įrankiai</span></div>
        <div className="v"><b>{fmtLt(comparison.manual_min, 0)} min.</b><span>rankinis (prielaida)</span></div>
        <div className="v"><b>{fmtLt(comparison.monthly_hours, 1)} val.</b><span>× {comparison.monthly_cases} bylų / mėn.</span></div>
      </div>
      <div className="time-bars">
        {(comparison.rows || []).map((r) => (
          <div key={r.tool} className="time-row">
            <span className="time-lab" title={r.tool}>{r.title}</span>
            <span className="time-track">
              <i className="manual" style={{ width: `${(r.manual_min / maxMin) * 100}%` }} />
              <i className="agent" style={{ width: `${Math.max(2, (r.agent_ms / 60000 / maxMin) * 100)}%` }} />
            </span>
            <span className="time-num">{r.manual_min} min · {fmtAgent(r.agent_ms)}</span>
          </div>
        ))}
      </div>
      <p className="assume">{comparison.note}</p>
    </aside>
  );
}
