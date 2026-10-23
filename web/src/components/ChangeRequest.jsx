import { useEffect, useMemo, useState } from "react";
import {
  PLUG_STEPS,
  REQUEST_STAGES,
  loadRequests,
  saveRequests,
  stageLabel,
} from "../suggestions.js";

const ACCEPT = ".pdf,.doc,.docx,.xlsx,.xls,.csv,.txt,.md,.json,.png";

function kindFor(name) {
  const ext = name.split(".").pop()?.toLowerCase() || "";
  if (["xlsx", "xls", "csv"].includes(ext)) return "data";
  if (["pdf", "doc", "docx", "md", "txt"].includes(ext)) return "requirements";
  return "document";
}

function formatWhen(iso) {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "";
  return date.toLocaleString("en-GB", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });
}

export default function ChangeRequest() {
  const [requests, setRequests] = useState(loadRequests);
  const [selectedId, setSelectedId] = useState(() => loadRequests()[0]?.id || null);
  const [toolName, setToolName] = useState("");
  const [purpose, setPurpose] = useState("");
  const [plugAfter, setPlugAfter] = useState("check_capacity");
  const [documents, setDocuments] = useState([]);

  useEffect(() => {
    saveRequests(requests);
  }, [requests]);

  const selected = useMemo(
    () => requests.find((item) => item.id === selectedId) || null,
    [requests, selectedId]
  );

  function addFiles(fileList) {
    const added = [...fileList].map((file) => ({ name: file.name, kind: kindFor(file.name) }));
    setDocuments((docs) => {
      const names = new Set(docs.map((doc) => doc.name));
      return [...docs, ...added.filter((doc) => !names.has(doc.name))];
    });
  }

  function submit(event) {
    event.preventDefault();
    const name = toolName.trim();
    const body = purpose.trim();
    if (!name || !body) return;
    const item = {
      id: `${Date.now()}`,
      toolName: name,
      purpose: body,
      plugAfter,
      documents,
      stage: 1,
      at: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    setRequests((items) => [item, ...items]);
    setSelectedId(item.id);
    setToolName("");
    setPurpose("");
    setDocuments([]);
    setPlugAfter("check_capacity");
  }

  const plugLabel = PLUG_STEPS.find((step) => step.id === (selected?.plugAfter || plugAfter))?.label;

  return (
    <div className="change-view" data-testid="change-request">
      <div className="change-wrap">
        <p className="change-kicker">Extend the toolkit</p>
        <h1>Engineers extend ESO helper themselves</h1>
        <div className="change-grid">
          <form className="tool-card" onSubmit={submit}>
            <header>
              <b>New tool request</b>
              <span>engineer form</span>
            </header>
            <label htmlFor="tool-name">Tool name</label>
            <input
              id="tool-name"
              value={toolName}
              onChange={(event) => setToolName(event.target.value)}
              placeholder="Loss calculation (auto-fill)"
              required
            />
            <label htmlFor="tool-purpose">What should it do?</label>
            <textarea
              id="tool-purpose"
              value={purpose}
              onChange={(event) => setPurpose(event.target.value)}
              placeholder="Fill in feeder and transformer losses from the case data, using our documented method."
              required
            />
            <label htmlFor="tool-docs">Data or requirements documents</label>
            <label className="doc-drop" htmlFor="tool-docs">
              <input
                id="tool-docs"
                type="file"
                multiple
                accept={ACCEPT}
                onChange={(event) => {
                  addFiles(event.target.files || []);
                  event.target.value = "";
                }}
              />
              Add documents
            </label>
            {documents.length > 0 && (
              <ul className="doc-list">
                {documents.map((doc) => (
                  <li key={doc.name}>
                    <span className="doc-kind">{doc.kind}</span>
                    <b>{doc.name}</b>
                    <em>uploaded</em>
                    <button type="button" onClick={() => setDocuments((docs) => docs.filter((item) => item.name !== doc.name))} aria-label={`Remove ${doc.name}`}>
                      ×
                    </button>
                  </li>
                ))}
              </ul>
            )}
            <label htmlFor="tool-plug">Which step does it plug into?</label>
            <select id="tool-plug" value={plugAfter} onChange={(event) => setPlugAfter(event.target.value)}>
              {PLUG_STEPS.map((step) => (
                <option key={step.id} value={step.id}>{step.label}</option>
              ))}
            </select>
            <div className="tool-actions">
              <button className="tool-submit" type="submit" disabled={!toolName.trim() || !purpose.trim()}>
                Submit
              </button>
            </div>
          </form>

          <section className="progress-card" aria-label="Submission progress">
            <p className="change-kicker">{selected ? "Submission progress" : "What happens after submit"}</p>
            {selected && (
              <>
                <h2>{selected.toolName}</h2>
                {selected.purpose && <p className="progress-purpose">{selected.purpose}</p>}
              </>
            )}
            <ol>
              {REQUEST_STAGES.map((stage) => {
                const state = !selected
                  ? "path"
                  : stage.id < selected.stage
                    ? "done"
                    : stage.id === selected.stage
                      ? "now"
                      : "wait";
                return (
                  <li key={stage.id} className={`progress-step ${state}`} data-stage={stage.id}>
                    <b>{stage.id}. {stage.title}</b>
                    <p>{stage.detail}</p>
                  </li>
                );
              })}
            </ol>
            {selected && (
              <p className="progress-meta">
                {[
                  plugLabel,
                  selected.documents.length ? selected.documents.map((doc) => doc.name).join(", ") : "",
                  selected.at ? formatWhen(selected.at) : "",
                ].filter(Boolean).join(", ")}
              </p>
            )}
          </section>
        </div>

        <section className="submission-board" data-testid="submissions">
          <h2>My submissions</h2>
          {requests.length === 0 ? (
            <p className="suggest-empty">No submissions yet. Send a tool request to follow its progress.</p>
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
                      <span className="status-pill" data-stage={item.stage}>{stageLabel(item.stage)}</span>
                    </span>
                    <span className="stage-pips" aria-label={`Step ${item.stage} of 4`}>
                      {[1, 2, 3, 4].map((step) => (
                        <i key={step} className={step <= item.stage ? "on" : ""} />
                      ))}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>
        <p className="change-foot">The AI writes the tool. The engineer decides if it goes live.</p>
      </div>
    </div>
  );
}
