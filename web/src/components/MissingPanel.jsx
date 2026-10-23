export default function MissingPanel({ missing, onSupply, busy }) {
  const gaps = missing?.gaps || [];
  const letter = missing?.letter || {};
  const prov = missing?.provisional || {};
  if (!gaps.length && !letter.body) return null;
  return (
    <div className="missing-box">
      <div className="kicker">request_missing_data</div>
      <h3>Laukia duomenų</h3>
      <ul className="gap-list">
        {gaps.map((g) => (
          <li key={g.id || g.field}>
            <b>{g.field}</b> · {g.party_lt || g.party}
            <div className="hint">{g.note} Priklauso: {g.why}.</div>
          </li>
        ))}
      </ul>
      <div className="kicker">Laiško peržiūra · neišsiųsta</div>
      <pre className="letter">{letter.body}</pre>
      <div className="kicker">Laikinas sprendinys</div>
      <p><b>{prov.solution}</b> — {prov.reason}</p>
      <ul className="gap-list">
        {(prov.sensitivity || []).map((s) => (
          <li key={s.if}><b>Jei {s.if}</b> → {s.then}. {s.note}</li>
        ))}
      </ul>
      {onSupply && (
        <button className="exec" type="button" disabled={busy} onClick={onSupply}>Pateikti duomenis ir tęsti</button>
      )}
    </div>
  );
}
