import { useState } from "react";

const CAT_LT = {
  out_of_scope: "Už SCOPE",
  missing_input: "Trūksta įvesties",
  tool_error: "Įrankio klaida",
  engineer_judgment: "Inžinieriaus sprendimas",
  match: "Sutampa",
};

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
      <td><span className={`cat ${field.category || ""}`}>{CAT_LT[field.category] || field.category || "—"}</span></td>
      <td className="explain">{field.explain}</td>
    </tr>
  );
}

function Taxonomy({ taxonomy }) {
  if (!taxonomy) return null;
  const order = ["out_of_scope", "missing_input", "tool_error", "engineer_judgment", "match"];
  const cases = taxonomy.cases || {};
  const total = order.reduce((s, k) => s + (cases[k] || 0), 0) || 1;
  return (
    <div className="tax">
      <div className="kicker">Neatitikimų taksonomija</div>
      <div className="tax-bar" aria-label="Taksonomija">
        {order.map((k) => (
          <div
            key={k}
            className={`tax-seg ${k}`}
            style={{ width: `${((cases[k] || 0) / total) * 100}%` }}
            title={`${taxonomy.labels?.[k] || k}: ${cases[k] || 0}`}
          />
        ))}
      </div>
      <ul className="tax-legend">
        {order.map((k) => (
          <li key={k}><i className={k} />{taxonomy.labels?.[k] || k} · {cases[k] || 0}</li>
        ))}
      </ul>
    </div>
  );
}

export default function Gallery({ gallery, running, onRun, onWhatIf, onOpenRun }) {
  const last = gallery?.last;
  const cases = last?.results || gallery?.cases || [];
  const [openId, setOpenId] = useState(null);
  const selected = (last?.results || []).find((r) => r.id === openId) || (last?.results || [])[0];
  const before = last?.before || gallery?.before;

  return (
    <div className="gallery">
      <header className="desk-head">
        <div>
          <div className="kicker">Istorinė galerija · 12-608</div>
          <h2>Išduotos TS vs agentas</h2>
          <p className="hint">Sąžiningas back-test. In-scope = 12-608 ir žinomas taškas. Duomenys nebuvo taikomi rezultatui.</p>
        </div>
        <div className="desk-actions">
          <button className="go" type="button" onClick={onWhatIf} disabled={running}>What-if užpildymas</button>
          <button className="exec" type="button" onClick={onRun} disabled={running}>
            {running ? "Skaičiuojama…" : "Paleisti back-test"}
          </button>
        </div>
      </header>
      {last && (
        <div className="hud-grid hud-5">
          <div className="hud"><b>{Math.round((last.in_scope_accuracy || 0) * 100)} %</b><span>In-scope tikslumas</span></div>
          <div className="hud"><b>{Math.round((last.accuracy || 0) * 100)} %</b><span>Visų 16 suminis</span></div>
          <div className="hud"><b>{last.in_scope_count}</b><span>In-scope bylų</span></div>
          <div className="hud"><b>{before ? `${Math.round((before.accuracy || 0) * 100)} %` : "—"}</b><span>Prieš (R3)</span></div>
          <div className="hud"><b>{last.taxonomy?.cases?.tool_error ?? 0}</b><span>Įrankio klaidų</span></div>
        </div>
      )}
      {gallery?.whatif && (
        <p className="assume whatif-note">
          What-if: {gallery.whatif.resolved_matches} / {gallery.whatif.missing_count} trūkstamų bylų tampa atitikimu, kai taškas paimamas iš išduotos TS. Tai ne live balas.
        </p>
      )}
      <Taxonomy taxonomy={last?.taxonomy} />
      <p className="assume">{last?.note || gallery?.note}</p>
      <div className="gallery-split">
        <div className="table-wrap desk-table">
          <table className="grid-table">
            <thead>
              <tr>
                <th>Reg. nr.</th>
                <th>TP</th>
                <th>Kat.</th>
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
                return (
                  <tr key={id} className={openId === id ? "hi" : ""} onClick={() => setOpenId(id)}>
                    <td><b>{id}</b><small> {row.source}</small></td>
                    <td>{row.tp_issued}</td>
                    <td><span className={`cat ${row.category || ""}`}>{CAT_LT[row.category] || (row.out_of_scope ? "Už SCOPE" : "—")}</span></td>
                    <td>{exp || "—"}</td>
                    <td>{got || (row.agent ? "—" : "paleiskite")}</td>
                    <td>{row.score == null ? "—" : `${Math.round(row.score * 100)} %`}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        {selected ? (
          <aside className="gallery-detail">
            <div className="kicker">{selected.id} · {CAT_LT[selected.category] || selected.category}</div>
            <h3>{selected.tp_issued} · agentas {selected.agent?.solution || "—"}</h3>
            <p className="hint">{selected.note}{selected.missing_reason ? ` ${selected.missing_reason}` : ""}</p>
            <table className="grid-table cmp">
              <thead>
                <tr><th>Laukas</th><th>Išduota TS</th><th>Agentas</th><th></th><th>Kat.</th><th>Paaiškinimas</th></tr>
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
