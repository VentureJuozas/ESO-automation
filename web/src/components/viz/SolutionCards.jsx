export default function SolutionCards({ comparison = [], chosen }) {
  if (!comparison.length) return null;
  return (
    <div className="section">
      <h3>Kodėl A, B ar C</h3>
      <div className="cards">
        {comparison.map((c) => (
          <article key={c.id} className={`scard ${c.chosen ? "chosen" : ""} ${c.applicable ? "" : "off"}`}>
            <h4>Sprendinys {c.id} {c.chosen ? "· parinkta" : c.applicable ? "" : "· netinka"}</h4>
            <p>{c.title}</p>
            <p style={{ marginTop: 8 }}>{c.chosen || c.applicable ? c.why : c.why_not}</p>
            <p style={{ marginTop: 8 }}>{c.ts_hint}</p>
          </article>
        ))}
      </div>
      {chosen?.reason && <p className="hint" style={{ marginTop: 12 }}>{chosen.reason}</p>}
    </div>
  );
}
