import { fmtNum } from "../steps.js";

function Gauge({ value, max = 100, label, pass }) {
  const pct = Math.max(0, Math.min(100, (Number(value) / max) * 100));
  return (
    <div className={`ll-gauge${pass === false ? " bad" : ""}`} data-testid="load-gauge">
      <div className="ll-gauge-bar"><i style={{ width: `${pct}%` }} /></div>
      <div className="ll-gauge-meta">
        <b>{fmtNum(value, 1)}%</b>
        <span>{label}</span>
      </div>
    </div>
  );
}

export default function LoadLoss({ loss, compact = false }) {
  if (!loss) return null;
  const line = loss.line || {};
  const feed = loss.feeder_loss || {};
  const tr = loss.transformer_loss || {};
  const path = compact ? (loss.to_customer || []) : (loss.segments || []);
  return (
    <div className={`load-loss${compact ? " compact" : ""}`} data-testid="load-loss">
      <h3>{compact ? "Load and loss" : "Load and loss estimator"}</h3>
      <div className="ll-grid">
        <article>
          <b>Feeder current</b>
          <span>{fmtNum(line.before?.isk_a, 1)} A → {fmtNum(line.after?.isk_a, 1)} A</span>
          <small>Isk = Psk / 0.624 · {loss.conductor}</small>
        </article>
        <article>
          <b>Line loading</b>
          <Gauge value={line.after?.load_pct} label={`of ${loss.ampacity_a} A`} pass={(line.after?.load_pct || 0) <= 100} />
        </article>
        <article>
          <b>Feeder loss</b>
          <span>{fmtNum(feed.before_kw, 3)} → {fmtNum(feed.after_kw, 3)} kW</span>
          <small>{fmtNum(feed.after_kwh_year, 0)} kWh/year</small>
        </article>
        <article>
          <b>Transformer loss</b>
          <span>{fmtNum(tr.before?.total_kw, 3)} → {fmtNum(tr.after?.total_kw, 3)} kW</span>
          <small>{fmtNum(tr.after_kwh_year, 0)} kWh/year · P0 + Pk·(S/Sn)²</small>
        </article>
      </div>
      {!compact && (
        <table className="grid-table" data-testid="loss-segments">
          <thead>
            <tr>
              <th>Segment</th>
              <th>m</th>
              <th>I before</th>
              <th>I after</th>
              <th>Load</th>
              <th>ΔU after</th>
              <th>V after</th>
              <th>Loss after</th>
            </tr>
          </thead>
          <tbody>
            {path.map((s) => (
              <tr key={`${s.id}-${s.m}`} className={s.kind === "connection" ? "hi" : ""}>
                <td>{s.id}</td>
                <td>{fmtNum(s.length_m, 0)}</td>
                <td>{fmtNum(s.i_before_a, 1)} A</td>
                <td>{fmtNum(s.i_after_a, 1)} A</td>
                <td>{fmtNum(s.load_after_pct, 1)}%</td>
                <td>{fmtNum(s.du_after_pct, 3)}%</td>
                <td>{fmtNum(s.v_after, 1)} V</td>
                <td>{fmtNum(s.loss_after_kw, 3)} kW</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
