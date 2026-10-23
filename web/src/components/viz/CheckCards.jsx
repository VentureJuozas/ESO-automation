import { fmtNum } from "../../steps.js";

export function ReliabilityCard({ cutIn, n1, backup }) {
  return (
    <div className="section">
      <div className="viz-cards">
        <article>
          <b>N-1 transformers</b>
          <span>{n1?.transformer_count ?? "—"}</span>
          <small>Reserve {fmtNum(n1?.reserve, 0)} kW</small>
        </article>
        <article>
          <b>Feeder</b>
          <span>{backup?.radial ? "Radial" : "Ring"}</span>
          <small>Backup path unchanged</small>
        </article>
        <article className={cutIn?.applies ? "warn" : "ok"}>
          <b>Cut-in</b>
          <span>{cutIn?.applies ? `${cutIn.affected_customers} points` : "None"}</span>
          <small>{cutIn?.applies ? "Planned outage on this feeder" : "Pole KAS does not isolate neighbours"}</small>
        </article>
      </div>
    </div>
  );
}

export function FutureCard({ gauge, outputs }) {
  const g = gauge || {};
  const ok = (g.headroom_kw ?? outputs?.headroom_kw) >= 0;
  return (
    <div className="section">
      <div className="viz-cards">
        <article className={ok ? "ok" : "bad"}>
          <b>Headroom to 80 %</b>
          <span>{fmtNum(g.headroom_kw ?? outputs?.headroom_kw)} kW</span>
        </article>
        <article>
          <b>After</b>
          <span>{fmtNum(g.after_kw)} kW</span>
        </article>
        <article>
          <b>Reserved</b>
          <span>{fmtNum(g.pending_kw, 0)} kW</span>
        </article>
      </div>
    </div>
  );
}
