import TransformerBar from "./viz/TransformerBar.jsx";
import VoltageProfile from "./viz/VoltageProfile.jsx";
import { ReliabilityCard, FutureCard } from "./viz/CheckCards.jsx";
import SolutionCards from "./viz/SolutionCards.jsx";
import TsDocument from "./viz/TsDocument.jsx";
import CostTable from "./viz/CostTable.jsx";
import MapPanel from "./MapPanel.jsx";
import BreakerTable from "./viz/BreakerTable.jsx";
import ParseExtract from "./viz/ParseExtract.jsx";
import LoadLoss from "./LoadLoss.jsx";
import { BRIEFINGS } from "../briefings.js";
import { STEP_LABEL } from "../steps.js";

function resultOf(ev, running, status) {
  if (running) return { kind: "run", label: "Running" };
  if (!ev) return { kind: "idle", label: "Idle" };
  if (ev.tool === "engineer_approval" && ev.type === "interrupt") return { kind: "wait", label: "Awaiting signature" };
  if (ev.outputs?.escalate || ev.outputs?.pass === false) return { kind: "fail", label: "Fail" };
  if (ev.ok === false) return { kind: "fail", label: "Fail" };
  return { kind: "pass", label: "Pass" };
}

function SourceBlock({ src }) {
  if (!src) return null;
  return (
    <div className="panel-block" data-testid="data-source">
      <h3>Data source</h3>
      <div className="kv">
        <div><b>System</b><span>{src.system}</span></div>
        <div><b>Dataset</b><span>{src.dataset}</span></div>
        <div><b>Fields</b><span>{src.fields}</span></div>
        <div><b>Timestamp</b><span>{src.timestamp}</span></div>
      </div>
    </div>
  );
}

function RuleBlock({ rule }) {
  if (!rule) return null;
  return (
    <div className="panel-block" data-testid="requirements">
      <h3>Requirements and rules</h3>
      <blockquote>{rule.quote}</blockquote>
      <p className="rule-ref">{rule.ref}</p>
    </div>
  );
}

function Calc({ toolId, ev, section3, setSection3, canEdit, runId, document, loadLoss }) {
  const o = ev?.outputs || {};
  return (
    <div className="panel-block" data-testid="calculation">
      <h3>Calculation</h3>
      {toolId === "parse_request" && <ParseExtract outputs={o} />}
      {(toolId === "locate_connection_point" || toolId === "render_map") && <MapPanel map={o.map || o} />}
      {toolId === "select_solution" && (
        <>
          <SolutionCards comparison={o.comparison} chosen={o} />
          <LoadLoss loss={loadLoss} compact />
        </>
      )}
      {toolId === "size_breaker" && <BreakerTable table={o.table} selected={o} requestedKw={o.requested_kw} />}
      {toolId === "check_capacity" && (
        <>
          <TransformerBar bar={o.transformer_bar} pass={o.pass} />
          <LoadLoss loss={o.load_loss || loadLoss} />
        </>
      )}
      {toolId === "check_voltage_drop" && (
        <>
          <VoltageProfile profile={o.profile} limit={o.limit_v} />
          <LoadLoss loss={o.load_loss || loadLoss} />
        </>
      )}
      {toolId === "check_reliability" && <ReliabilityCard cutIn={o.cut_in} n1={o.n1} backup={o.backup} />}
      {toolId === "check_future" && <FutureCard gauge={o.gauge} outputs={o} />}
      {toolId === "estimate_cost" && <CostTable cost={o} />}
      {(toolId === "draft_ts_section3" || toolId === "engineer_approval" || toolId === "issue_ts") && (
        <TsDocument document={o.document || document} section3={section3} onChange={setSection3} editable={canEdit} runId={runId} />
      )}
    </div>
  );
}

export default function StepSheet({
  toolId, event, running, error, section3, setSection3, canEdit,
  onClose, runId, document, status, loadLoss,
}) {
  const brief = BRIEFINGS[toolId] || {};
  const title = STEP_LABEL[toolId] || toolId;
  const result = resultOf(event, running, status);

  if (error) {
    return (
      <section className="sheet" role="region">
        <div className="sheet-body"><div className="error">{error}</div></div>
      </section>
    );
  }

  return (
    <section className="sheet" role="region" aria-label={title} data-testid="step-panel">
      <header className="sheet-head">
        <div>
          <div className="sheet-kicker">{toolId}</div>
          <h2>{title}</h2>
        </div>
        <div className="badges">
          <span className={`badge result ${result.kind}`} data-testid="step-result">{result.label}</span>
          {event?.elapsed_ms != null && <span className="badge">{event.elapsed_ms} ms</span>}
          {onClose && <button type="button" className="insp-x" onClick={onClose} aria-label="Close">×</button>}
        </div>
      </header>
      <div className="sheet-body">
        {running && !event && <div className="skel"><div className="skel-bar" /><div className="skel-bar" /></div>}
        <SourceBlock src={brief.source} />
        <RuleBlock rule={brief.rule} />
        <Calc
          toolId={toolId}
          ev={event}
          section3={section3}
          setSection3={setSection3}
          canEdit={canEdit}
          runId={runId}
          document={document}
          loadLoss={loadLoss}
        />
        <div className="panel-block result-block" data-testid="result-block">
          <h3>Result</h3>
          <p className={`result-pill ${result.kind}`}>{result.label}</p>
        </div>
      </div>
    </section>
  );
}
