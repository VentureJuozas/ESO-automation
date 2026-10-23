import { useEffect, useState } from "react";
import { GROUPS, STEP_LABEL } from "../steps.js";
import { Icon } from "../icons.jsx";

const STORE = "eso-suggestions";

function stepState(id, events, runningTool, status) {
  if (runningTool === id) return "run";
  const ev = [...events].reverse().find((e) => e.tool === id);
  if (!ev) return "wait";
  if (ev.type === "interrupt") return "stop";
  if (ev.outputs?.pass === false || ev.outputs?.escalate) return "stop";
  if (id === "issue_ts" && status !== "issued") return "wait";
  if (id === "engineer_approval" && status === "awaiting_approval") return "stop";
  return "done";
}

function loadSuggestions() {
  try {
    const parsed = JSON.parse(localStorage.getItem(STORE) || "[]");
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function formatWhen(iso) {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "";
  return date.toLocaleString("en-GB", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });
}

export default function Sidebar({
  events = [],
  runningTool,
  selected,
  onSelect,
  open,
  onToggle,
  status,
}) {
  const [flowOpen, setFlowOpen] = useState(false);
  const [suggestOpen, setSuggestOpen] = useState(false);
  const [suggestions, setSuggestions] = useState(loadSuggestions);
  const [expanded, setExpanded] = useState(() => new Set());
  const [functionality, setFunctionality] = useState("");
  const [detail, setDetail] = useState("");
  const [engineer, setEngineer] = useState("");

  useEffect(() => {
    localStorage.setItem(STORE, JSON.stringify(suggestions));
  }, [suggestions]);

  function submitSuggestion(event) {
    event.preventDefault();
    const title = functionality.trim();
    const body = detail.trim();
    if (!title || !body) return;
    const item = {
      id: `${Date.now()}`,
      title,
      detail: body,
      engineer: engineer.trim(),
      at: new Date().toISOString(),
    };
    setSuggestions((items) => [item, ...items]);
    setExpanded((ids) => new Set(ids).add(item.id));
    setFunctionality("");
    setDetail("");
    setEngineer("");
  }

  function toggleSuggestion(id) {
    setExpanded((ids) => {
      const next = new Set(ids);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  const canSubmit = functionality.trim() && detail.trim();

  return (
    <aside className="side" data-testid="sidebar">
      <div className="brand">
        <span className="mark"><Icon name="branch" size={16} /></span>
        <div>
          <b>ESO helper</b>
          <small>0.4 kV · TP 12-608</small>
        </div>
      </div>
      <nav className="nav">
        <p className="nav-label">Main</p>
        <button
          className={`nav-item${flowOpen ? " on" : ""}`}
          type="button"
          data-testid="nav-flow"
          aria-expanded={flowOpen}
          onClick={() => setFlowOpen((value) => !value)}
        >
          <Icon name="branch" size={16} />
          Flow
          <i className={`nav-chev${flowOpen ? " open" : ""}`} aria-hidden="true" />
        </button>
        {flowOpen && (
          <div className="flow-body">
            {GROUPS.map((g) => (
              <div key={g.id} data-testid={`group-${g.id}`}>
                <button
                  className={`nav-sub${open[g.id] ? " on" : ""}`}
                  type="button"
                  aria-expanded={Boolean(open[g.id])}
                  onClick={() => onToggle(g.id)}
                >
                  <Icon name={g.icon} size={15} />
                  {g.title}
                  <i className={`nav-chev${open[g.id] ? " open" : ""}`} aria-hidden="true" />
                </button>
                {open[g.id] && g.tools.map((id) => {
                  const st = stepState(id, events, runningTool, status);
                  return (
                    <button
                      key={id}
                      className={`nav-step${selected === id ? " on" : ""}`}
                      type="button"
                      data-testid={`step-${id}`}
                      onClick={() => onSelect(id)}
                    >
                      <i className={`nav-dot st-${st}`} />
                      {STEP_LABEL[id] || id}
                    </button>
                  );
                })}
              </div>
            ))}
          </div>
        )}
        <button className="nav-item" type="button" disabled data-testid="nav-test-env">
          <Icon name="flask" size={16} />
          Test environment
        </button>

        <p className="nav-label">Suggestions</p>
        <button
          className={`nav-item${suggestOpen ? " on" : ""}`}
          type="button"
          data-testid="nav-propose"
          aria-expanded={suggestOpen}
          onClick={() => setSuggestOpen((value) => !value)}
        >
          <Icon name="plus" size={16} />
          Propose a change
          <i className={`nav-chev${suggestOpen ? " open" : ""}`} aria-hidden="true" />
        </button>
        {suggestOpen && (
          <div className="suggest-panel" data-testid="suggest-panel">
            <form onSubmit={submitSuggestion}>
              <label htmlFor="suggest-who">Engineer</label>
              <input
                id="suggest-who"
                value={engineer}
                onChange={(event) => setEngineer(event.target.value)}
                placeholder="Name"
                autoComplete="name"
              />
              <label htmlFor="suggest-title">Functionality</label>
              <input
                id="suggest-title"
                value={functionality}
                onChange={(event) => setFunctionality(event.target.value)}
                placeholder="What to add"
                required
              />
              <label htmlFor="suggest-detail">What to implement</label>
              <textarea
                id="suggest-detail"
                value={detail}
                onChange={(event) => setDetail(event.target.value)}
                placeholder="Describe the change for the manager"
                required
              />
              <button className="suggest-submit" type="submit" disabled={!canSubmit}>
                Submit suggestion
              </button>
            </form>
            {suggestions.length === 0 ? (
              <p className="suggest-empty">No suggestions yet.</p>
            ) : (
              <ul className="suggest-list">
                {suggestions.map((item) => {
                  const isOpen = expanded.has(item.id);
                  return (
                    <li key={item.id}>
                      <button
                        type="button"
                        className={`suggest-row${isOpen ? " open" : ""}`}
                        aria-expanded={isOpen}
                        onClick={() => toggleSuggestion(item.id)}
                      >
                        <i className={`nav-chev${isOpen ? " open" : ""}`} aria-hidden="true" />
                        <b>{item.title}</b>
                      </button>
                      {isOpen && (
                        <p className="suggest-detail">
                          <small>
                            {[item.engineer || "Engineer", formatWhen(item.at)].filter(Boolean).join(" · ")}
                          </small>
                          {item.detail}
                        </p>
                      )}
                    </li>
                  );
                })}
              </ul>
            )}
          </div>
        )}
      </nav>
    </aside>
  );
}
