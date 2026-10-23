export default function AffectedList({ cutIn, n1, backup }) {
  return (
    <div className="section">
      <h3>Patikimumas</h3>
      <div className="kv">
        <div><b>Transformatoriai</b><span>{n1?.transformer_count} · N-1 rezervas {n1?.reserve} kW</span></div>
        <div><b>Linija</b><span>{backup?.radial ? "Radiali, atsarginis kelias neprarandamas" : "—"}</span></div>
      </div>
      <h3 style={{ marginTop: 14 }}>Atjungiami apskaitos taškai</h3>
      {!cutIn?.applies ? (
        <p>Šis sprendinys kaimynų neatjungia.</p>
      ) : (
        <>
          <p><b>{cutIn.affected_customers}</b> taškai linijoje (be adresų).</p>
          <table className="cost">
            <tbody>
              {(cutIn.groups || []).map((g) => (
                <tr key={g.id}><td>{g.kind === "pole" ? "Atrama" : "Spinta"} {g.id}</td><td>{g.points}</td></tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}
