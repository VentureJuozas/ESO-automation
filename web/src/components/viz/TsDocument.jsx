export default function TsDocument({ document: doc, section3, onChange, editable, runId }) {
  if (!doc && !section3) return null;
  const text = section3 || doc?.section3 || "";
  const kw = doc?.kw;
  const phases = doc?.phases;
  const phase = doc?.phase_label || (phases === 3 ? "Trifazis" : phases === 1 ? "Vienfazis" : "—");
  return (
    <div className="section">
      <div className="ts-toolbar">
        <h3>Oficialus TS maketas</h3>
        {runId && (
          <span style={{ display: "flex", gap: 8 }}>
            <a className="go" href={`/api/runs/${runId}/ts.html`} target="_blank" rel="noreferrer">
              A4 / 2 psl.
            </a>
            <a className="go" href={`/api/runs/${runId}/ts.pdf`} target="_blank" rel="noreferrer">
              PDF
            </a>
          </span>
        )}
      </div>
      {editable && (
        <label htmlFor="s3" className="ts-edit-label">§3 tekstas (inžinierius gali taisyti)</label>
      )}
      {editable && (
        <textarea id="s3" className="edit" value={text} onChange={(e) => onChange?.(e.target.value)} />
      )}
      <article className="ts-a4" aria-label="Prijungimo sąlygos">
        {doc?.watermark && <div className="wm">{doc.watermark}</div>}
        <header className="ts-head">
          <div>
            <div className="k">AB Energijos skirstymo operatorius · demonstracija</div>
            <h4>ELEKTROS VARTOTOJO PRIJUNGIMO SĄLYGOS</h4>
          </div>
          <div className="ts-meta">
            Nr. <b>{doc?.ts_number || "PROJEKTAS"}</b><br />
            Parengta: {doc?.issue_date || "—"}<br />
            Galioja iki: {doc?.valid_until || "—"}
          </div>
        </header>
        <h5>Kliento prijungiamo objekto duomenys</h5>
        <table className="ts-fields">
          <tbody>
            <tr><td>Klientas</td><td>{doc?.customer || "Buitinis vartotojas (redaguota)"}</td></tr>
            <tr><td>Identifikatorius</td><td>{doc?.customer_code || "ASMENS KODAS / EIC REDAGUOTAS"}</td></tr>
            <tr><td>Objekto pavadinimas</td><td>{doc?.object_name || "Naujas buitinis objektas"}</td></tr>
            <tr><td>Objekto vieta</td><td>{doc?.address || "Adresas redaguotas · objektas prie TP 12-608"}</td></tr>
            <tr><td>Nauja leistina naudoti galia</td><td>{kw ?? "—"} kW · {phase}</td></tr>
            <tr><td>Transformatorinė</td><td>{doc?.tp || "12-608"}</td></tr>
            <tr><td>Linija / elementas</td><td>{doc?.feeder || "—"} · {doc?.element || "—"}</td></tr>
            <tr><td>Sprendinys / jungiklis</td><td>{doc?.solution || "—"} · {doc?.breaker || "—"}</td></tr>
          </tbody>
        </table>
        <h5>1. Nuosavybės riba</h5>
        <p>{doc?.section1}</p>
        <h5>2. Kliento veiksmai</h5>
        {(doc?.section2 || []).map((p) => <p key={p}>{p}</p>)}
        <h5>3. ESO veiksmai</h5>
        <p className="ts-s3">{text}</p>
        <h5>4. Galiojimas ir parašas</h5>
        <p>Sąlygos galioja vienerius metus nuo parengimo datos.</p>
        <div className="ts-sig">
          <div>{doc?.signature?.prepared || "Parengė demonstracinis agentas"}</div>
          <div>
            {doc?.signature?.approved || "Inžinierius (žmogaus vartai)"}
            <small>{doc?.signature?.title}</small>
          </div>
        </div>
        <p className="ts-disc">{doc?.disclaimer}</p>
      </article>
    </div>
  );
}
