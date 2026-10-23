import { useState } from "react";

function KindChip({ kind, label }) {
  return <span className={`kind-chip k-${kind}`}>{label}</span>;
}

export default function TracePanel({ trace, selectedId, onSelect }) {
  const [openJson, setOpenJson] = useState(null);
  const steps = trace?.steps || [];
  const stats = trace?.stats || { llm: 0, python: 0, human: 0, line: "—" };
  return (
    <section className="trace-panel" data-testid="trace-panel">
      <header className="sheet-head">
        <div>
          <div className="sheet-kicker">Trace</div>
          <h2>Tool calls</h2>
        </div>
      </header>
      <div className="trace-stats" data-testid="trace-stats">
        {stats.line}
      </div>
      <ul className="kind-legend" data-testid="trace-legend">
        <li><i className="k-llm" />LLM</li>
        <li><i className="k-tool" />Python</li>
        <li><i className="k-human" />Human</li>
      </ul>
      <ol className="trace-list">
        {steps.length === 0 && <li className="hint">Run the case to see each call.</li>}
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
                  <KindChip kind={s.kind} label={s.kind === "llm" && s.llm_role ? `LLM (${s.llm_role})` : s.kind_en} />
                  <small>{s.elapsed_ms} ms</small>
                </span>
                <span className="trace-io">In: {s.input_summary}</span>
                <span className="trace-io">Out: {s.output_summary}</span>
              </span>
            </button>
            <button type="button" className="json-toggle" onClick={() => setOpenJson(openJson === s.step ? null : s.step)}>
              {openJson === s.step ? "Hide JSON" : "JSON"}
            </button>
            {openJson === s.step && (
              <pre className="json">{JSON.stringify({ inputs: s.inputs, outputs: s.outputs }, null, 2)}</pre>
            )}
          </li>
        ))}
      </ol>
    </section>
  );
}
