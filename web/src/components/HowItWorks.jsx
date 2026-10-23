export default function HowItWorks({ architecture, layerId }) {
  if (!architecture) return <div className="empty">Kraunama architektūra…</div>;
  const layer = (architecture.layers || []).find((l) => l.id === layerId);
  const tools = architecture.tools || [];
  const next = architecture.next_steps || [];

  if (layerId === "tools") {
    return (
      <div>
        <p className="hint">Deterministiniai Python įrankiai. Skaičiai ne iš LLM.</p>
        <ul className="compact-list">
          {tools.filter((t) => t.kind === "tool").map((t) => (
            <li key={t.id}><b>{t.title}</b> — {t.title_lt}</li>
          ))}
        </ul>
      </div>
    );
  }
  if (layerId === "llm") {
    return (
      <div>
        <p className="hint">LLM tik skaito laisvą tekstą ir formuluoja §3. Be rakto — replay šablonai.</p>
        <p style={{ color: "var(--muted)", fontSize: 12 }}>Veiksena dabar: <b>{architecture.llm_mode}</b></p>
        <ul className="compact-list">
          {tools.filter((t) => t.kind === "llm").map((t) => (
            <li key={t.id}><b>{t.title}</b> — {t.outputs}</li>
          ))}
        </ul>
      </div>
    );
  }
  if (layerId === "human") {
    return (
      <div>
        <p className="hint">Sąlygas visada išduoda inžinierius. Eskalacija reikalauja override su priežastimi — vieno mygtuko „išduoti vis tiek“ nėra.</p>
      </div>
    );
  }
  if (layerId === "data") {
    return (
      <div>
        <div className="section">
          <h3>Kas tikra, kas sintetina</h3>
          <p><span className="tag real">išmatuota</span> TP 12-608 viršūnė 227,7 kW, 400 kW nominalas, 80/90 % ribos, linijų taškų skaičiai, L-KS14330 315 A.</p>
          <p><span className="tag rule">taisyklė</span> jungiklio lentelė, nesutapimo k., 207 V, A/B/C logika.</p>
          <p><span className="tag inferred">išvesta</span> atstumai ir ruožų ilgiai iš koordinačių.</p>
          <p><span className="tag synthetic">sintetinis</span> atramų/spintų koordinatės, kitų linijų saugikliai, laidininkai, rezervacijos 0 kW.</p>
        </div>
        <div className="section">
          <h3>Kiti žingsniai</h3>
          <div className="roadmap">
            {next.map((n) => (
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
  if (layerId === "graph") {
    return (
      <div>
        <p className="hint">LangGraph eina fiksuota seka ir sustoja prie inžinieriaus vartų. Šaka: patikros OK → juodraštis; nepraeina → eskalacija.</p>
        {architecture.mermaid && <pre className="json">{architecture.mermaid}</pre>}
      </div>
    );
  }
  if (layerId === "api") {
    return (
      <div>
        <p className="hint">FastAPI transliuoja kiekvieną įrankio start/result SSE srautu. Paleisti, atnaujinti, perskaičiuoti — REST.</p>
      </div>
    );
  }
  return (
    <div>
      <p className="hint">{layer?.note || "Valdymo skydas yra orkestratoriaus vaizdas n8n drobėje."}</p>
      <ul className="compact-list">
        {(architecture.principles || []).map((p) => <li key={p}>{p}</li>)}
      </ul>
      <p style={{ color: "var(--muted)", fontSize: 12 }}>{architecture.manual_time_note}</p>
    </div>
  );
}
