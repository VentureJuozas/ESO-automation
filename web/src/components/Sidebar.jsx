import { GROUPS, STEP_LABEL } from "../steps.js";
import { Icon } from "../icons.jsx";

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

export default function Sidebar({
  events = [],
  runningTool,
  selected,
  onSelect,
  open,
  onToggle,
  status,
}) {
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
        {GROUPS.map((g) => (
          <div key={g.id} className={`sec${open[g.id] ? " open" : ""}`} data-testid={`group-${g.id}`}>
            <button
              className={`sec-btn${open[g.id] ? " open" : ""}`}
              type="button"
              onClick={() => onToggle(g.id)}
            >
              {g.title}
              <span className="count">{g.tools.length}</span>
            </button>
            {open[g.id] && g.tools.map((id) => {
              const st = stepState(id, events, runningTool, status);
              return (
                <button
                  key={id}
                  className={`item${selected === id ? " on" : ""}`}
                  type="button"
                  data-testid={`step-${id}`}
                  onClick={() => onSelect(id)}
                >
                  <b>{STEP_LABEL[id] || id}</b>
                  <small className={`st-${st}`}>{st === "run" ? "Running" : st === "done" ? "Done" : st === "stop" ? "Waiting" : "Idle"}</small>
                </button>
              );
            })}
          </div>
        ))}
      </nav>
    </aside>
  );
}
