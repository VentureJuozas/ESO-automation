import { fmtLt } from "../../steps.js";
import SourceTags from "../SourceTags.jsx";

export function ReliabilityCard({ cutIn, n1, backup }) {
  return (
    <div className="section">
      <h3>Patikimumas</h3>
      <div className="viz-cards">
        <article>
          <b>N-1 transformatoriai</b>
          <span>{n1?.transformer_count ?? "—"} vnt.</span>
          <small>Rezervas {fmtLt(n1?.reserve, 0)} kW</small>
        </article>
        <article>
          <b>Linija</b>
          <span>{backup?.radial ? "Radialė" : "Žiedas"}</span>
          <small>Atsarginis kelias neprarandamas</small>
        </article>
        <article className={cutIn?.applies ? "warn" : "ok"}>
          <b>Įsipjovimas</b>
          <span>{cutIn?.applies ? `${cutIn.affected_customers} taškai` : "Neatjungia"}</span>
          <small>{cutIn?.applies ? "Be adresų, tik skaitikliai linijoje" : "Sprendinys A/B kaimynų neatjungia"}</small>
        </article>
      </div>
      {cutIn?.applies && (
        <table className="cost">
          <tbody>
            {(cutIn.groups || []).map((g) => (
              <tr key={g.id}><td>{g.kind === "pole" ? "Atrama" : "Spinta"} {g.id}</td><td>{g.points}</td></tr>
            ))}
          </tbody>
        </table>
      )}
      <p className="map-note"><SourceTags tags={["real", "rule"]} /></p>
    </div>
  );
}

export function FutureCard({ gauge, outputs }) {
  const g = gauge || {};
  const ok = (g.headroom_kw ?? outputs?.headroom_kw) >= 0;
  return (
    <div className="section">
      <h3>Ateitis · atsarga iki 80 %</h3>
      <div className="viz-cards">
        <article className={ok ? "ok" : "bad"}>
          <b>Likutis</b>
          <span>{fmtLt(g.headroom_kw ?? outputs?.headroom_kw)} kW</span>
          <small>{ok ? "Telpa su rezervuotomis" : "Nepraeina — rezervas neigiamas"}</small>
        </article>
        <article>
          <b>Po prijungimo</b>
          <span>{fmtLt(g.after_kw)} kW</span>
          <small>Viršūnė + paraiška</small>
        </article>
        <article>
          <b>Rezervuota</b>
          <span>{fmtLt(g.pending_kw, 0)} kW</span>
          <small>Demo: 0 kW (sintetinis)</small>
        </article>
      </div>
      <p className="map-note"><SourceTags tags={["real", "synthetic", "rule"]} /></p>
    </div>
  );
}
