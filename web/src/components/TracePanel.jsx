import { useState } from "react";
import { KIND_HINT } from "../trace.js";

function KindChip({ kind, label }) {
  return <span className={`kind-chip k-${kind}`}>{label}</span>;
}

export default function TracePanel({ trace, selectedId, onSelect }) {
  const [openJson, setOpenJson] = useState(null);
  const steps = trace?.steps || [];
  const stats = trace?.stats || { llm: 0, python: 0, human: 0, line: "—" };
  return (
    <section className="trace-panel" data-testid="trace-panel" data-spot-target="trace">
      <header className="sheet-head">
        <div>
          <div className="sheet-kicker">Agento sekimas</div>
          <h2>Matomi įrankių kvietimai</h2>
        </div>
      </header>
      <div className="trace-stats" data-testid="trace-stats">
        <b>{stats.llm}</b> LLM kvietimai · <b>{stats.python}</b> deterministiniai įrankiai · <b>{stats.human}</b> žmogaus vartai
      </div>
      <p className="hint">LLM tik skaito paraišką ir formuluoja §3. Python priima kiekvieną inžinerinį sprendimą. Sąlygas pasirašo žmogus.</p>
      <ul className="kind-legend" data-testid="trace-legend">
        <li><i className="k-llm" />LLM · skaitymas / formulavimas</li>
        <li><i className="k-tool" />Python · deterministinė taisyklė</li>
        <li><i className="k-human" />Žmogus · patvirtinimas</li>
      </ul>
      <ol className="trace-list">
        {steps.length === 0 && <li className="hint">Paleiskite eigą — čia atsiras kiekvienas mazgas.</li>}
        {steps.map((s) => (
          <li key={`${s.step}-${s.tool}`}>
            <button
              type="button"
              className={`trace-step k-${s.kind}${selectedId === s.tool ? " on" : ""}`}
              data-testid={`trace-step-${s.tool}`}
              onClick={() => onSelect?.(s.tool)}
            >
              <span className="trace-n">{s.step}</span>
              <span className="trace-body">
                <span className="trace-top">
                  <b>{s.tool}</b>
                  <KindChip kind={s.kind} label={s.kind === "llm" && s.llm_role ? `LLM · ${s.llm_role}` : s.kind_lt} />
                  <small>{s.elapsed_ms} ms</small>
                </span>
                <span className="trace-title">{s.title}</span>
                <span className="trace-io">Įvestis: {s.input_summary}</span>
                <span className="trace-io">Išvestis: {s.output_summary}</span>
                <span className="trace-meta">
                  {(s.source_tags || []).map((t) => <em key={t}>{t}</em>)}
                  {s.rule_ref?.label && <em className="rule">{s.rule_ref.local || s.rule_ref.label}</em>}
                </span>
              </span>
            </button>
            <button
              type="button"
              className="json-toggle"
              onClick={() => setOpenJson(openJson === s.step ? null : s.step)}
            >
              {openJson === s.step ? "Slėpti JSON" : "JSON"}
            </button>
            {openJson === s.step && (
              <pre className="json">{JSON.stringify({ inputs: s.inputs, outputs: s.outputs }, null, 2)}</pre>
            )}
          </li>
        ))}
      </ol>
      <p className="hint">{KIND_HINT.llm}</p>
    </section>
  );
}
