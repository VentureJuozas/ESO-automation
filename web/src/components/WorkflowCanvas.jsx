import { useEffect, useMemo, useRef, useState } from "react";
import {
  ADAPTER_EDGES,
  ADAPTER_NODES,
  ADAPTER_STICKIES,
  ARCH_EDGES,
  ARCH_NODES,
  ARCH_STICKIES,
  INSPECTOR_PAD,
  NODE_H,
  NODE_W,
  ANALYSIS_CHILDREN,
  PIPELINE_EDGES,
  PIPELINE_NODES,
  SOLUTION_OPTIONS,
  WORLD_H,
  WORLD_W,
  edgePath,
  nodeById,
  nodePorts,
} from "../workflow.js";
import { Bang, Check, Icon } from "../icons.jsx";
import { classify } from "../trace.js";

function nodeState(id, events, runningTool, failed, skipped = []) {
  if (id === "analysis") {
    const states = ANALYSIS_CHILDREN.map((child) => nodeState(child.id, events, runningTool, failed, skipped));
    if (states.includes("run")) return "run";
    if (states.includes("stop")) return "stop";
    if (states.some((state) => state === "done") && states.every((state) => state === "done" || state === "skip")) return "done";
    if (states.some((state) => state === "done")) return "run";
    return "wait";
  }
  if (skipped.includes(id)) return "skip";
  if (runningTool === id) return "run";
  const ev = [...events].reverse().find((e) => e.tool === id);
  if (!ev) return "wait";
  if (ev.type === "start") return "run";
  if (ev.type === "interrupt") return "stop";
  if (ev.outputs?.escalate) return "stop";
  if (ev.ok === false) return "stop";
  if (id === "escalate" && !failed) return "idle";
  if (id === "issue_ts" && !events.some((e) => e.tool === "issue_ts" && e.type === "tool")) return "wait";
  return "done";
}

function edgeActive(from, to, events, runningTool, failed, skipped = []) {
  const fs = nodeState(from, events, runningTool, failed, skipped);
  const ts = nodeState(to, events, runningTool, failed, skipped);
  if (from === "parse_request" && to === "request_missing_data") {
    return events.some((e) => e.tool === "request_missing_data");
  }
  if (from === "parse_request" && to === "locate_connection_point") {
    if (events.some((e) => e.tool === "request_missing_data") && !events.some((e) => e.tool === "locate_connection_point" && e.type === "tool")) return false;
  }
  if (from === "check_capacity" && to === "escalate") return failed && (fs === "done" || fs === "stop");
  if (from === "check_capacity" && to === "check_voltage_drop") return !skipped.includes("check_voltage_drop") && fs === "done";
  if (from === "check_future" && to === "escalate") return failed && (fs === "done" || fs === "stop") && !skipped.includes("check_future");
  if (from === "analysis" && to === "draft_ts_section3") return !failed && fs === "done";
  if (ts === "skip" || fs === "skip") return false;
  if (ts === "run") return true;
  return fs === "done" && (ts === "done" || ts === "stop" || ts === "run");
}

function SolutionNode({ n, st, selected, onSelect, ports, nk }) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef(null);
  useEffect(() => {
    if (!open) return undefined;
    function onDocClick(event) {
      if (!rootRef.current?.contains(event.target)) setOpen(false);
    }
    function onKey(event) {
      if (event.key === "Escape") setOpen(false);
    }
    const timer = window.setTimeout(() => document.addEventListener("click", onDocClick), 0);
    document.addEventListener("keydown", onKey);
    return () => {
      window.clearTimeout(timer);
      document.removeEventListener("click", onDocClick);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  return (
    <div
      ref={rootRef}
      data-node={n.id}
      data-testid="solution-node"
      className={`n8n-node solution-node ${st}${selected ? " on" : ""}${open ? " open" : ""}${nk ? ` k-${nk}` : ""}`}
      style={{ left: n.x, top: n.y, "--hue": n.hue }}
    >
      {[...ports].map((side) => (
        <span key={side} className={`n8n-port port-${side}${st === "run" ? " live" : ""}`} />
      ))}
      <button
        type="button"
        className="solution-trigger"
        data-testid="solution-menu-button"
        aria-pressed={selected}
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-label={n.label}
        onClick={(event) => {
          event.stopPropagation();
          onSelect(n.id);
          setOpen((value) => !value);
        }}
      >
        <span className="n8n-ico"><Icon name={n.icon} size={20} /></span>
        <span className="n8n-copy"><b>{n.label}</b></span>
        <i className="chev" aria-hidden="true" />
      </button>
      {open && (
        <ul className="solution-menu" role="listbox" aria-label="Solution options" data-testid="solution-menu">
          {SOLUTION_OPTIONS.map((option) => (
            <li key={option.id}>
              <button
                type="button"
                role="option"
                aria-selected={option.active}
                disabled={!option.active}
                data-testid={`solution-option-${option.id}`}
                onClick={() => setOpen(false)}
              >
                {option.label}
              </button>
            </li>
          ))}
        </ul>
      )}
      {st === "done" && (
        <span className="n8n-pip done"><Check /></span>
      )}
      {st === "stop" && <span className="n8n-pip stop"><Bang /></span>}
      {st === "skip" && <span className="n8n-pip skip" title="Skipped">–</span>}
      {st === "run" && <span className="n8n-pip run" />}
    </div>
  );
}

function AnalysisNode({ n, st, selectedId, onSelect, ports, nk, events, runningTool, failed, skipped }) {
  const childIds = ANALYSIS_CHILDREN.map((child) => child.id);
  const active = childIds.includes(selectedId);
  const [open, setOpen] = useState(false);
  const rootRef = useRef(null);
  useEffect(() => {
    if (childIds.includes(runningTool)) setOpen(true);
  }, [runningTool]);
  useEffect(() => {
    if (!open) return undefined;
    function onDocClick(event) {
      if (!rootRef.current?.contains(event.target)) setOpen(false);
    }
    function onKey(event) {
      if (event.key === "Escape") setOpen(false);
    }
    const timer = window.setTimeout(() => document.addEventListener("click", onDocClick), 0);
    document.addEventListener("keydown", onKey);
    return () => {
      window.clearTimeout(timer);
      document.removeEventListener("click", onDocClick);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  return (
    <div
      ref={rootRef}
      data-node={n.id}
      data-testid="analysis-node"
      className={`n8n-node solution-node analysis-node ${st}${active ? " on" : ""}${open ? " open" : ""}${nk ? ` k-${nk}` : ""}`}
      style={{ left: n.x, top: n.y, "--hue": n.hue }}
    >
      {[...ports].map((side) => (
        <span key={side} className={`n8n-port port-${side}${st === "run" ? " live" : ""}`} />
      ))}
      <button
        type="button"
        className="solution-trigger"
        data-testid="analysis-menu-button"
        aria-pressed={active}
        aria-expanded={open}
        aria-label={n.label}
        onClick={(event) => {
          event.stopPropagation();
          setOpen((value) => !value);
        }}
      >
        <span className="n8n-ico"><Icon name={n.icon} size={20} /></span>
        <span className="n8n-copy"><b>{n.label}</b></span>
        <i className="chev" aria-hidden="true" />
      </button>
      {open && (
        <ul className="solution-menu analysis-menu" role="listbox" aria-label="Analysis" data-testid="analysis-menu">
          {ANALYSIS_CHILDREN.map((child) => {
            const childState = nodeState(child.id, events, runningTool, failed, skipped);
            return (
              <li key={child.id}>
                <button
                  type="button"
                  role="option"
                  aria-selected={selectedId === child.id}
                  data-testid={`analysis-${child.id}`}
                  className={`st-${childState}`}
                  onClick={() => onSelect(child.id)}
                >
                  <i className={`nav-dot st-${childState}`} />
                  {child.label}
                </button>
              </li>
            );
          })}
        </ul>
      )}
      {st === "done" && <span className="n8n-pip done"><Check /></span>}
      {st === "stop" && <span className="n8n-pip stop"><Bang /></span>}
      {st === "skip" && <span className="n8n-pip skip" title="Skipped">–</span>}
      {st === "run" && <span className="n8n-pip run" />}
    </div>
  );
}

function lastEvent(id, events) {
  return (
    [...events].reverse().find((e) => e.tool === id && e.type === "tool")
    || [...events].reverse().find((e) => e.tool === id && e.type !== "start")
    || null
  );
}

export default function WorkflowCanvas({
  mode = "pipeline",
  events = [],
  runningTool,
  failed,
  selectedId,
  onSelect,
  architecture,
  stickies,
  inspectorOpen = true,
  followId,
  skipped = [],
  kindOverlay = false,
  onToggleOverlay,
}) {
  const nodes = mode === "adapters" ? ADAPTER_NODES : mode === "arch" ? ARCH_NODES : PIPELINE_NODES;
  const edges = mode === "adapters" ? ADAPTER_EDGES : mode === "arch" ? ARCH_EDGES : PIPELINE_EDGES;
  const notes = stickies || (mode === "adapters" ? ADAPTER_STICKIES : mode === "arch" ? ARCH_STICKIES : []);
  const lookup = (id) => nodeById(id, nodes);
  const wrapRef = useRef(null);
  const camRef = useRef({ x: 24, y: 24, k: 1 });
  const dragRef = useRef(null);
  const [cam, setCam] = useState(camRef.current);
  const [dragging, setDragging] = useState(false);

  function setCamera(next) {
    const value = typeof next === "function" ? next(camRef.current) : next;
    const clipped = {
      k: Math.min(1.6, Math.max(0.55, value.k)),
      x: value.x,
      y: value.y,
    };
    camRef.current = clipped;
    setCam(clipped);
  }

  const padRight = inspectorOpen ? INSPECTOR_PAD : 0;

  function fitView() {
    const el = wrapRef.current;
    if (!el) return;
    const w = Math.max(160, el.clientWidth - padRight - 28);
    const h = Math.max(160, el.clientHeight - 28);
    const k = Math.min(1, w / WORLD_W, h / WORLD_H);
    const x = 14 + Math.max(0, (w - WORLD_W * k) / 2);
    const y = 14 + Math.max(0, (h - WORLD_H * k) / 2);
    setCamera({ x, y, k });
  }

  function panTo(node) {
    const el = wrapRef.current;
    if (!el || !node) return;
    const visW = el.clientWidth - padRight;
    const visH = el.clientHeight;
    const k = camRef.current.k;
    const targetX = visW * 0.34 - (node.x + NODE_W / 2) * k;
    const targetY = visH * 0.42 - (node.y + NODE_H / 2) * k;
    setCamera({ x: targetX, y: targetY, k });
  }

  function obscured(node) {
    const el = wrapRef.current;
    if (!el || !node) return false;
    const { x, y, k } = camRef.current;
    const sx = node.x * k + x;
    const sy = node.y * k + y;
    const visW = el.clientWidth - padRight;
    const visH = el.clientHeight;
    return sx < 10 || sy < 10 || sx + NODE_W * k > visW - 16 || sy + NODE_H * k > visH - 16;
  }

  useEffect(() => {
    fitView();
    const el = wrapRef.current;
    if (!el || typeof ResizeObserver === "undefined") return undefined;
    const ro = new ResizeObserver(() => fitView());
    ro.observe(el);
    return () => ro.disconnect();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mode, inspectorOpen]);

  useEffect(() => {
    const id = followId || runningTool || selectedId;
    const node = lookup(id) || (ANALYSIS_CHILDREN.some((child) => child.id === id) ? lookup("analysis") : null);
    if (node && (followId || runningTool || obscured(node))) panTo(node);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [followId, runningTool, selectedId, inspectorOpen]);

  const portMap = useMemo(() => {
    const m = {};
    for (const n of nodes) m[n.id] = nodePorts(n.id, nodes, edges);
    return m;
  }, [nodes, edges]);

  function onPointerDown(e) {
    if (e.button !== 0) return;
    if (e.target.closest(".n8n-node, .sticky, .wf-toolbar, button, a")) return;
    dragRef.current = { x: e.clientX, y: e.clientY, camX: camRef.current.x, camY: camRef.current.y };
    setDragging(true);
    e.currentTarget.setPointerCapture(e.pointerId);
  }

  function onPointerMove(e) {
    const d = dragRef.current;
    if (!d) return;
    setCamera({
      k: camRef.current.k,
      x: d.camX + (e.clientX - d.x),
      y: d.camY + (e.clientY - d.y),
    });
  }

  function onPointerUp() {
    dragRef.current = null;
    setDragging(false);
  }

  function onWheel(e) {
    e.preventDefault();
    const el = wrapRef.current;
    if (!el) return;
    const factor = e.deltaY > 0 ? 0.92 : 1.08;
    const rect = el.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    const prev = camRef.current;
    const k = Math.min(1.6, Math.max(0.55, prev.k * factor));
    const wx = (mx - prev.x) / prev.k;
    const wy = (my - prev.y) / prev.k;
    setCamera({ k, x: mx - wx * k, y: my - wy * k });
  }

  function zoom(delta) {
    const el = wrapRef.current;
    const cx = el ? (el.clientWidth - padRight) / 2 : 400;
    const cy = el ? el.clientHeight / 2 : 240;
    const prev = camRef.current;
    const k = Math.min(1.6, Math.max(0.55, prev.k + delta));
    const wx = (cx - prev.x) / prev.k;
    const wy = (cy - prev.y) / prev.k;
    setCamera({ k, x: cx - wx * k, y: cy - wy * k });
  }

  return (
    <div
      className={`wf-viewport${dragging ? " dragging" : ""}`}
      ref={wrapRef}
      onPointerDown={onPointerDown}
      onPointerMove={onPointerMove}
      onPointerUp={onPointerUp}
      onPointerCancel={onPointerUp}
      onWheel={onWheel}
      role="application"
      aria-label="Connection workflow"
      data-kinds={kindOverlay ? "on" : "off"}
    >
      <div className="wf-toolbar" onPointerDown={(e) => e.stopPropagation()}>
        <button type="button" className="go" onClick={() => zoom(-0.12)} aria-label="Zoom out">−</button>
        <span className="zoom-readout">{Math.round(cam.k * 100)}%</span>
        <button type="button" className="go" onClick={() => zoom(0.12)} aria-label="Zoom in">+</button>
        <button type="button" className="go" onClick={fitView}>Fit</button>
        {mode === "pipeline" && (
          <button
            type="button"
            className={`go${kindOverlay ? " on" : ""}`}
            data-testid="kind-overlay"
            onClick={() => onToggleOverlay?.(!kindOverlay)}
          >
            LLM / Python / Human
          </button>
        )}
      </div>
      {kindOverlay && mode === "pipeline" && (
        <ul className="kind-legend canvas-legend" data-testid="canvas-kind-legend">
          <li><i className="k-llm" />LLM</li>
          <li><i className="k-tool" />Python</li>
          <li><i className="k-human" />Human</li>
        </ul>
      )}
      <div
        className={`wf-world${dragging ? " dragging" : ""}`}
        style={{
          width: WORLD_W,
          height: WORLD_H,
          transform: `translate(${cam.x}px, ${cam.y}px) scale(${cam.k})`,
        }}
      >
        <svg className="wf-edges" viewBox={`0 0 ${WORLD_W} ${WORLD_H}`} width={WORLD_W} height={WORLD_H}>
          <defs>
            <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#c4c4cc" />
            </marker>
            <marker id="arrow-on" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#1f9d61" />
            </marker>
            <marker id="arrow-run" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#20366c" />
            </marker>
            <marker id="arrow-llm" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#7a9620" />
            </marker>
            <marker id="arrow-tool" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#6d8a22" />
            </marker>
            <marker id="arrow-human" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#20366c" />
            </marker>
          </defs>
          {edges.map(([a, b]) => {
            const na = lookup(a);
            const nb = lookup(b);
            if (!na || !nb) return null;
            const on = mode === "arch" ? true : edgeActive(a, b, events, runningTool, failed, skipped);
            const running = runningTool === b;
            const ek = kindOverlay && mode === "pipeline" ? classify(b, lastEvent(b, events), architecture?.tools) : "";
            const marker = kindOverlay && ek
              ? `url(#arrow-${ek})`
              : running ? "url(#arrow-run)" : on ? "url(#arrow-on)" : "url(#arrow)";
            return (
              <path
                key={`${a}-${b}`}
                d={edgePath(na, nb)}
                className={`edge${on ? " on" : ""}${running ? " flow" : ""}${ek ? ` k-${ek}` : ""}`}
                markerEnd={marker}
              />
            );
          })}
        </svg>
        {notes.map((s) => (
          <aside key={s.id} className="sticky" style={{ left: s.x, top: s.y }} data-sticky={s.id}>
            <b>{s.title}</b>
            <p>{s.body}</p>
          </aside>
        ))}
        {nodes.map((n) => {
          const adapter = (architecture?.adapters || []).find((a) => a.id === n.id);
          const st = mode === "adapters"
            ? (adapter?.mode === "stub" ? "stop" : "done")
            : mode === "arch" ? (selectedId === n.id ? "run" : "wait") : nodeState(n.id, events, runningTool, failed, skipped);
          const hidden = mode === "pipeline" && n.id === "escalate" && !failed && (st === "wait" || st === "idle");
          const ev = lastEvent(n.id, events);
          const ports = portMap[n.id] || new Set(["left", "right"]);
          const nk = kindOverlay && mode === "pipeline" ? classify(n.id, ev, architecture?.tools) : "";
          if (mode === "pipeline" && n.id === "select_solution") {
            return (
              <SolutionNode
                key={n.id}
                n={n}
                st={st}
                selected={selectedId === n.id}
                onSelect={onSelect}
                ports={ports}
                nk={nk}
              />
            );
          }
          if (mode === "pipeline" && n.id === "analysis") {
            return (
              <AnalysisNode
                key={n.id}
                n={n}
                st={st}
                selectedId={selectedId}
                onSelect={onSelect}
                ports={ports}
                nk={nk}
                events={events}
                runningTool={runningTool}
                failed={failed}
                skipped={skipped}
              />
            );
          }
          return (
            <button
              key={n.id}
              type="button"
              data-node={n.id}
              className={`n8n-node ${st}${selectedId === n.id ? " on" : ""}${hidden ? " ghost" : ""}${nk ? ` k-${nk}` : ""}`}
              style={{ left: n.x, top: n.y, "--hue": n.hue }}
              onClick={() => onSelect(n.id)}
              aria-pressed={selectedId === n.id}
              aria-label={n.label}
            >
              {[...ports].map((side) => (
                <span key={side} className={`n8n-port port-${side}${st === "run" ? " live" : ""}`} />
              ))}
              <span className="n8n-ico"><Icon name={n.icon} size={20} /></span>
              <span className="n8n-copy">
                <b>{n.label}</b>
              </span>
              {st === "done" && (
                <span className="n8n-pip done" title={`${ev?.elapsed_ms ?? 0} ms`}>
                  <Check />
                </span>
              )}
              {st === "stop" && <span className="n8n-pip stop"><Bang /></span>}
              {st === "skip" && <span className="n8n-pip skip" title="Skipped">–</span>}
              {st === "run" && <span className="n8n-pip run" />}
            </button>
          );
        })}
      </div>
    </div>
  );
}
