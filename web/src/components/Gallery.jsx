import { useState } from "react";

function Badge({ match }) {
  if (match === true) return <span className="badge ok">Sutampa</span>;
  if (match === false) return <span className="badge bad">Nesutampa</span>;
  return <span className="badge">Nelyginama</span>;
}

function FieldRow({ field }) {
  return (
    <tr className={field.match === false ? "miss" : field.match ? "hit" : ""}>
      <td>{field.field}</td>
      <td><pre>{field.expected == null ? "—" : String(field.expected)}</pre></td>
      <td><pre>{field.got == null ? "—" : String(field.got)}</pre></td>
      <td><Badge match={field.match} /></td>
      <td className="explain">{field.explain}</td>
    </tr>
  );
}

export default function Gallery({ gallery, running, onRun, onOpenRun }) {
  const last = gallery?.last;
  const cases = last?.results || gallery?.cases || [];
  const [openId, setOpenId] = useState(null);
  const selected = (last?.results || []).find((r) => r.id === openId) || (last?.results || [])[0];

  return (
    <div className="gallery">
      <header className="desk-head">
        <div>
          <div className="kicker">Istorinė galerija · 12-608</div>
          <h2>Išduotos TS vs agentas</h2>
          <p className="hint">Tik redaguoti duomenys. Neatitikimai rodomi sąmoningai — kita TP, sintetinė lokacija, kitoks darbų rinkinys.</p>
        </div>
        <button className="exec" type="button" onClick={onRun} disabled={running}>
          {running ? "Skaičiuojama…" : "Paleisti back-test"}
        </button>
      </header>
      {last && (
        <div className="hud-grid">
          <div className="hud"><b>{Math.round((last.accuracy || 0) * 100)} %</b><span>Suminis tikslumas</span></div>
          <div className="hud"><b>{last.count}</b><span>Bylų palyginta</span></div>
          <div className="hud"><b>{(last.results || []).filter((r) => r.fields.some((f) => f.match === false)).length}</b><span>Su neatitikimu</span></div>
        </div>
      )}
      <p className="assume">{last?.note || gallery?.note}</p>
      <div className="gallery-split">
        <div className="table-wrap desk-table">
          <table className="grid-table">
            <thead>
              <tr>
                <th>Reg. nr.</th>
                <th>Išduota TP</th>
                <th>Tikėtasi</th>
                <th>Agentas</th>
                <th>Balas</th>
              </tr>
            </thead>
            <tbody>
              {(last?.results || gallery?.cases || []).map((row) => {
                const id = row.id;
                const exp = row.expected?.solution || row.expected_solution;
                const got = row.agent?.solution;
                const score = row.score;
                return (
                  <tr key={id} className={openId === id ? "hi" : ""} onClick={() => setOpenId(id)}>
                    <td><b>{id}</b><small> {row.source}</small></td>
                    <td>{row.tp_issued}</td>
                    <td>{exp || "—"}</td>
                    <td>{got || (row.agent ? "—" : "paleiskite")}</td>
                    <td>{score == null ? "—" : `${Math.round(score * 100)} %`}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        {selected ? (
          <aside className="gallery-detail">
            <div className="kicker">{selected.id}</div>
            <h3>{selected.tp_issued} · agentas {selected.agent?.solution || "—"}</h3>
            <p className="hint">{selected.note}</p>
            <table className="grid-table cmp">
              <thead>
                <tr><th>Laukas</th><th>Išduota TS</th><th>Agentas</th><th></th><th>Paaiškinimas</th></tr>
              </thead>
              <tbody>
                {(selected.fields || []).map((f) => <FieldRow key={f.field} field={f} />)}
              </tbody>
            </table>
            {selected.agent?.run_id && (
              <div className="inbox-actions">
                <button className="go" type="button" onClick={() => onOpenRun(selected.agent.run_id)}>Atidaryti drobę</button>
                <a className="go" href={`/api/runs/${selected.agent.run_id}/audit.html`} target="_blank" rel="noreferrer">Auditas</a>
              </div>
            )}
          </aside>
        ) : (
          <aside className="gallery-detail">
            <p className="empty">{cases.length ? "Pasirinkite bylą arba paleiskite back-test." : "Istorinių bylų nėra."}</p>
          </aside>
        )}
      </div>
    </div>
  );
}
