export default function HowItWorks({ architecture }) {
  if (!architecture) return <div className="empty">Kraunama architektūra…</div>;
  return (
    <div className="how">
      <div className="how-card">
        <h2 style={{ marginTop: 0 }}>Kaip tai veikia</h2>
        <p>Valdymo skydas yra orkestratoriaus vaizdas. Inžinerinius sprendimus priima deterministinis Python; LLM skaito laisvą tekstą ir formuluoja §3. Sąlygas visada išduoda inžinierius.</p>
        <div className="arch" aria-label="Architektūros sluoksniai">
          {(architecture.layers || []).map((l, i) => (
            <span key={l.id} style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <div className="boxy"><b>{l.title}</b><small>{l.note}</small></div>
              {i < architecture.layers.length - 1 && <span className="arr">→</span>}
            </span>
          ))}
        </div>
        <ul>
          {(architecture.principles || []).map((p) => <li key={p}>{p}</li>)}
        </ul>
        <p style={{ color: "var(--muted)", fontSize: 12 }}>LLM veiksena dabar: <b>{architecture.llm_mode}</b>. {architecture.manual_time_note}</p>
      </div>
      <div className="how-card">
        <h3>Grafo žingsniai</h3>
        <table className="steps-table">
          <thead><tr><th>Įrankis</th><th>Įvestis</th><th>Išvestis</th><th>Taisyklė / duomenys</th></tr></thead>
          <tbody>
            {(architecture.tools || []).map((t) => (
              <tr key={t.id}>
                <td><b>{t.title}</b><br /><span style={{ color: "var(--muted)" }}>{t.title_lt} · {t.kind}</span></td>
                <td>{t.inputs}</td>
                <td>{t.outputs}</td>
                <td>
                  {t.rule_ref ? <a href={t.rule_ref.url} target="_blank" rel="noreferrer">{t.rule_ref.label} ↗</a> : t.rule}
                  <div style={{ color: "var(--muted)" }}>{t.data}</div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {architecture.mermaid && <pre className="json">{architecture.mermaid}</pre>}
      </div>
      <div className="how-card">
        <h3>Kas tikra, kas sintetina</h3>
        <p><span className="tag real">išmatuota</span> TP 12-608 viršūnė 227,7 kW, 400 kW nominalas, 80/90 % ribos, linijų taškų skaičiai, L-KS14330 315 A.</p>
        <p><span className="tag rule">taisyklė</span> jungiklio lentelė, nesutapimo k., 207 V, A/B/C logika.</p>
        <p><span className="tag inferred">išvesta</span> atstumai ir ruožų ilgiai iš koordinačių.</p>
        <p><span className="tag synthetic">sintetinis</span> atramų/spintų koordinatės, kitų linijų saugikliai, laidininkai, rezervacijos 0 kW. Žaliaviniai CSV su PII neįtraukti.</p>
      </div>
      <div className="how-card">
        <h3>Kiti žingsniai</h3>
        <div className="roadmap">
          {(architecture.next_steps || []).map((n) => (
            <article key={n.id}>
              <h4>{n.title}</h4>
              <ul>{(n.items || []).map((i) => <li key={i}>{i}</li>)}</ul>
            </article>
          ))}
        </div>
      </div>
    </div>
  );
}
