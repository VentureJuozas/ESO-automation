import { useMemo, useState } from "react";
import { PLUG_STEPS, REQUEST_STAGES, loadRequests, stageLabel } from "../suggestions.js";

function formatWhen(iso) {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "";
  return date.toLocaleString("en-GB", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });
}

export default function TestEnvironment() {
  const requests = useMemo(() => loadRequests(), []);
  const [selectedId, setSelectedId] = useState(requests[0]?.id || null);
  const selected = requests.find((item) => item.id === selectedId) || null;
  const plugLabel = PLUG_STEPS.find((step) => step.id === selected?.plugAfter)?.label;

  return (
    <div className="change-view" data-testid="test-environment">
      <div className="change-wrap">
        <p className="change-kicker">Back-test cases</p>
        <h1>Test environment</h1>
        <p className="test-lead">Engineer proposals, and the status of each one.</p>
        <div className="change-grid">
          <section className="proposal-list" data-testid="proposals">
            {requests.length === 0 ? (
              <p className="suggest-empty">No proposals yet.</p>
            ) : (
              <ul>
                {requests.map((item) => (
                  <li key={item.id}>
                    <button
                      type="button"
                      className={item.id === selectedId ? "on" : ""}
                      onClick={() => setSelectedId(item.id)}
                    >
                      <span>
                        <b>{item.toolName}</b>
                        <small>{item.purpose}</small>
                      </span>
                      <em className="status-pill" data-stage={item.stage}>{stageLabel(item.stage)}</em>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </section>
          <section className="progress-card" aria-label="Proposal status">
            {selected ? (
              <>
                <p className="change-kicker">Status</p>
                <h2>{selected.toolName}</h2>
                <p className="progress-purpose">{selected.purpose}</p>
                <ol>
                  {REQUEST_STAGES.map((stage) => {
                    const state = stage.id < selected.stage ? "done" : stage.id === selected.stage ? "now" : "wait";
                    return (
                      <li key={stage.id} className={`progress-step ${state}`} data-stage={stage.id}>
                        <b>{stage.id}. {stage.title}</b>
                        <p>{stage.detail}</p>
                      </li>
                    );
                  })}
                </ol>
                <p className="progress-meta">
                  {[
                    plugLabel,
                    selected.documents.length ? selected.documents.map((doc) => doc.name).join(", ") : "",
                    selected.at ? formatWhen(selected.at) : "",
                  ].filter(Boolean).join(", ")}
                </p>
              </>
            ) : (
              <p className="suggest-empty">Select a proposal to see its status.</p>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
