import { fmtEur } from "../../steps.js";
import SourceTags from "../SourceTags.jsx";

export default function SolutionCards({ comparison = [], chosen }) {
  if (!comparison.length) return null;
  const winner = comparison.find((c) => c.chosen) || chosen;
  return (
    <div className="section">
      <h3>Kodėl laimėjo {winner?.id || "B"}</h3>
      {winner && (
        <p className="hint win">
          <b>Sprendinys {winner.id}</b> — {winner.why || chosen?.reason}
        </p>
      )}
      <div className="cards">
        {comparison.map((c) => {
          const rejected = !c.chosen;
          return (
            <article key={c.id} className={`scard ${c.chosen ? "chosen" : "off"}`}>
              <h4>
                {c.id}
                <small>{c.chosen ? "parinkta" : c.applicable ? "atmesta" : "netinka"}</small>
              </h4>
              <p className="scard-title">{c.title}</p>
              <p>{c.chosen ? c.why : c.why_not}</p>
              <dl>
                <div><dt>Kaina be PVM</dt><dd>{fmtEur(c.cost_net)}</dd></div>
                <div><dt>Su PVM</dt><dd>{fmtEur(c.cost_gross)}</dd></div>
                <div><dt>Darbai</dt><dd>{c.works}</dd></div>
                <div><dt>Apribojimai</dt><dd>{c.constraints}</dd></div>
              </dl>
              {rejected && <p className="why-not">{c.why_not}</p>}
            </article>
          );
        })}
      </div>
      <p className="map-note">SCOPE A/B/C. <SourceTags tags={["rule", "real"]} /></p>
    </div>
  );
}
