import { ARCH_EDGES, ARCH_NODES, NODE_H, NODE_W, PIPELINE_EDGES, PIPELINE_NODES, edgePath, nodeById } from "../workflow.js";
import { Bang, Check, Icon } from "../icons.jsx";

function nodeState(id, events, runningTool, failed) {
  if (runningTool === id) return "run";
  const ev = [...events].reverse().find((e) => e.tool === id);
  if (!ev) return "wait";
  if (ev.type === "interrupt") return "stop";
  if (ev.outputs?.escalate) return "stop";
  if (ev.ok === false) return "stop";
  if (id === "escalate" && !failed) return "idle";
  if (id === "issue_ts" && !events.some((e) => e.tool === "issue_ts" && e.type === "tool")) return "wait";
  return "done";
}

function edgeActive(from, to, events, runningTool, failed) {
  const fs = nodeState(from, events, runningTool, failed);
  const ts = nodeState(to, events, runningTool, failed);
  if (from === "check_future" && to === "escalate") return failed && (fs === "done" || fs === "stop");
  if (from === "check_future" && to === "draft_ts_section3") return !failed && fs === "done";
  if (from === "escalate" && to === "estimate_cost") return failed;
  if (ts === "run") return true;
  return fs === "done" && (ts === "done" || ts === "stop" || ts === "run");
}

export default function WorkflowCanvas({
  mode = "pipeline",
  events = [],
  runningTool,
  failed,
  selectedId,
  onSelect,
  architecture,
}) {
  const nodes = mode === "arch" ? ARCH_NODES : PIPELINE_NODES;
  const edges = mode === "arch" ? ARCH_EDGES : PIPELINE_EDGES;
  const lookup = (id) => nodeById(id, nodes);
  const width = 1280;
  const height = 460;

  return (
    <div className="wf" role="application" aria-label="Prijungimo eigos drobė">
      <svg className="wf-edges" viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="xMinYMin meet">
        <defs>
          <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#c4c4cc" />
          </marker>
          <marker id="arrow-on" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#1f9d61" />
          </marker>
        </defs>
        {edges.map(([a, b]) => {
          const na = lookup(a);
          const nb = lookup(b);
          if (!na || !nb) return null;
          if (mode === "pipeline" && a === "check_future" && b === "escalate" && !failed && !events.some((e) => e.tool === "escalate")) {
            /* still draw, muted */
          }
          const on = mode === "arch" ? true : edgeActive(a, b, events, runningTool, failed);
          const running = runningTool === b;
          return (
            <path
              key={`${a}-${b}`}
              d={edgePath(na, nb)}
              className={`edge${on ? " on" : ""}${running ? " flow" : ""}`}
              markerEnd={on ? "url(#arrow-on)" : "url(#arrow)"}
            />
          );
        })}
      </svg>
      {nodes.map((n) => {
        const st = mode === "arch" ? (selectedId === n.id ? "run" : "wait") : nodeState(n.id, events, runningTool, failed);
        const hidden = mode === "pipeline" && n.id === "escalate" && !failed && st === "wait";
        const arch = architecture?.layers?.find((l) => l.id === n.id);
        return (
          <button
            key={n.id}
            type="button"
            className={`n8n-node ${st}${selectedId === n.id ? " on" : ""}${hidden ? " ghost" : ""}`}
            style={{ left: n.x, top: n.y, "--hue": n.hue }}
            onClick={() => onSelect(n.id)}
            aria-pressed={selectedId === n.id}
          >
            <span className="n8n-ico"><Icon name={n.icon} size={20} /></span>
            <span className="n8n-copy">
              <b>{n.label}</b>
              <small>{mode === "arch" ? (arch?.note || n.caption) : n.caption}</small>
            </span>
            {st === "done" && <span className="n8n-pip done"><Check /></span>}
            {st === "stop" && <span className="n8n-pip stop"><Bang /></span>}
            {st === "run" && <span className="n8n-pip run" />}
          </button>
        );
      })}
    </div>
  );
}
