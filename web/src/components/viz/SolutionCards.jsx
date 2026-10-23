import { fmtEur } from "../../steps.js";

export default function SolutionCards({ comparison = [], chosen }) {
  if (!comparison.length) return null;
  const winner = comparison.find((c) => c.chosen) || chosen;
  return (
    <div className="section">
      <div className="cards">
        {comparison.map((c) => (
          <article key={c.id} className={`scard ${c.chosen ? "chosen" : "off"}`}>
            <h4>
              {c.id}
              <small>{c.chosen ? "selected" : c.applicable ? "rejected" : "not applicable"}</small>
            </h4>
            <p className="scard-title">{c.title}</p>
            <p>{c.chosen ? c.why : c.why_not}</p>
            <dl>
              <div><dt>Net</dt><dd>{fmtEur(c.cost_net)}</dd></div>
              <div><dt>Gross</dt><dd>{fmtEur(c.cost_gross)}</dd></div>
              <div><dt>Works</dt><dd>{c.works}</dd></div>
              <div><dt>Constraint</dt><dd>{c.constraints}</dd></div>
            </dl>
          </article>
        ))}
      </div>
      {winner && <p className="formula">Selected {winner.id}: {winner.why || chosen?.reason}</p>}
    </div>
  );
}
