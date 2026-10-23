function BarRow({ label, value, max, tone }) {
  const pct = max ? Math.min(100, (value / max) * 100) : 0;
  return (
    <div className="an-row">
      <span className="an-lab">{label}</span>
      <div className="an-track"><i className={tone || ""} style={{ width: `${pct}%` }} /></div>
      <span className="an-num">{value}</span>
    </div>
  );
}

export default function Analytics({ data }) {
  if (!data) {
    return <div className="analytics" data-testid="analytics-view"><p className="hint">Kraunama analitika…</p></div>;
  }
  const maxDay = Math.max(1, ...((data.throughput || []).map((d) => d.n)));
  const mix = data.mix || {};
  const mixTotal = Object.values(mix).reduce((s, n) => s + n, 0) || 1;
  const bottleMax = Math.max(1, data.bottleneck?.missing_data_h || 0, data.bottleneck?.engineer_approval_h || 0);
  const risk = data.sla?.cases || [];
  return (
    <div className="analytics" data-testid="analytics-view" data-spot-target="analytics">
      <header className="desk-head">
        <div>
          <div className="kicker">Analitika · vadovo vaizdas</div>
          <h2>Eilės srautas ir kliūtys</h2>
          <p className="hint syn" data-testid="analytics-synthetic">{data.label}</p>
        </div>
        <div className="hud-grid hud-5" style={{ margin: 0, minWidth: 280 }}>
          <div className="hud"><b>{data.throughput_total}</b><span>bylos / {data.days} d.</span></div>
          <div className="hud"><b>{data.hours_saved_h} h</b><span>sutaupyta · prielaida</span></div>
          <div className="hud"><b>{data.sla?.at_risk || 0}</b><span>SLA rizika</span></div>
        </div>
      </header>

      <div className="an-grid">
        <section className="an-card">
          <div className="kicker">Pralaidumas per dieną</div>
          <div className="an-bars" data-testid="analytics-throughput">
            {(data.throughput || []).map((d) => (
              <BarRow key={d.day} label={d.day.slice(5)} value={d.n} max={maxDay} tone="coral" />
            ))}
          </div>
        </section>

        <section className="an-card">
          <div className="kicker">Mediana etape</div>
          <p className="hint">{data.median_stage?.note}</p>
          <div className="hud-grid" style={{ gridTemplateColumns: "1fr 1fr 1fr" }}>
            <div className="hud"><b>{data.median_stage?.agent_s ?? "—"} s</b><span>Agentas (replay)</span></div>
            <div className="hud"><b>{data.median_stage?.engineer_min ?? "—"} min</b><span>Inžinieriaus peržiūra</span></div>
            <div className="hud"><b>{data.median_stage?.wait_data_h ?? "—"} h</b><span>Trūkstami duomenys</span></div>
          </div>
        </section>

        <section className="an-card">
          <div className="kicker">Kliūtys · kur bylos laukia</div>
          <p className="hint">{data.bottleneck?.note}</p>
          <BarRow label="Trūkstami duomenys" value={data.bottleneck?.missing_data_h || 0} max={bottleMax} tone="warn" />
          <BarRow label="Inžinieriaus tvirtinimas" value={data.bottleneck?.engineer_approval_h || 0} max={bottleMax} tone="coral" />
          <div className="an-unit">valandos eilėje per sintetinį mėnesį</div>
        </section>

        <section className="an-card">
          <div className="kicker">Rezultatų mišinys</div>
          <div className="tax-bar" aria-label="Mišinys">
            {["A", "B", "C", "escalate", "waiting"].map((k) => (
              <div key={k} className={`tax-seg mix-${k}`} style={{ width: `${((mix[k] || 0) / mixTotal) * 100}%` }} title={`${k}: ${mix[k] || 0}`} />
            ))}
          </div>
          <ul className="tax-legend">
            <li><i className="mix-A" />A · {mix.A || 0}</li>
            <li><i className="mix-B" />B · {mix.B || 0}</li>
            <li><i className="mix-C" />C · {mix.C || 0}</li>
            <li><i className="mix-escalate" />Eskaluota · {mix.escalate || 0}</li>
            <li><i className="mix-waiting" />Laukia duomenų · {mix.waiting || 0}</li>
          </ul>
        </section>

        <section className="an-card wide">
          <div className="kicker">SLA rizika eilėje</div>
          <p className="hint">{data.sla?.rule} Paryškintos bylos, kurioms gresia 3 d.d. pažeidimas.</p>
          <div className="table-wrap">
            <table className="grid-table" data-testid="analytics-sla">
              <thead><tr><th>Byla</th><th>Diena</th><th>Būsena</th><th>Baigtis</th><th>Šaltinis</th></tr></thead>
              <tbody>
                {risk.length === 0 && <tr><td colSpan={5}>Rizikingų bylų nėra.</td></tr>}
                {risk.map((c) => (
                  <tr key={c.id} className={c.overdue ? "risk" : "warn"}>
                    <td>{c.id}</td>
                    <td>{c.day}</td>
                    <td>{c.status}</td>
                    <td>{c.outcome}</td>
                    <td>{c.source}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="an-card">
          <div className="kicker">Sutaupytos inžinieriaus valandos</div>
          <div className="hud"><b>{data.hours_saved_h} h</b><span>kaupiama per sintetinį mėnesį</span></div>
          <p className="hint assume-tag" data-testid="analytics-assumption">
            Prielaida: {data.hours_saved_per_issued_h} h / išduotą bylą
            ({data.monthly_cases_assumption} bylų / mėn. stalo prielaida). {data.hours_saved_note}
          </p>
          <p className="hint">Gyvos SQLite eigos: {data.live_n}. Sintetinės: {data.synthetic_n}.</p>
        </section>
      </div>
    </div>
  );
}
