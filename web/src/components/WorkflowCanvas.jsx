import { useEffect, useMemo, useRef, useState } from "react";
import {
  ARCH_EDGES,
  ARCH_NODES,
  ARCH_STICKIES,
  INSPECTOR_PAD,
  NODE_H,
  NODE_W,
  PIPELINE_EDGES,
  PIPELINE_NODES,
  WORLD_H,
  WORLD_W,
  edgePath,
  nodeById,
  nodePorts,
  nodeSummary,
} from "../workflow.js";
import { Bang, Check, Icon } from "../icons.jsx";

function nodeState(id, events, runningTool, failed) {
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

function edgeActive(from, to, events, runningTool, failed) {
  const fs = nodeState(from, events, runningTool, failed);
  const ts = nodeState(to, events, runningTool, failed);
  if (from === "check_future" && to === "escalate") return failed && (fs === "done" || fs === "stop");
  if (from === "check_future" && to === "draft_ts_section3") return !failed && fs === "done";
  if (from === "escalate" && to === "estimate_cost") return failed;
  if (ts === "run") return true;
  return fs === "done" && (ts === "done" || ts === "stop" || ts === "run");
}

function lastEvent(id, events) {
  return [...events].reverse().find((e) => e.tool === id && e.type !== "start") || null;
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
}) {
  const nodes = mode === "arch" ? ARCH_NODES : PIPELINE_NODES;
  const edges = mode === "arch" ? ARCH_EDGES : PIPELINE_EDGES;
  const notes = stickies || (mode === "arch" ? ARCH_STICKIES : []);
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
    const node = lookup(id);
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
      aria-label="Prijungimo eigos drobė"
    >
      <div className="wf-toolbar" onPointerDown={(e) => e.stopPropagation()}>
        <button type="button" className="go" onClick={() => zoom(-0.12)} aria-label="Sumažinti">−</button>
        <span className="zoom-readout">{Math.round(cam.k * 100)}%</span>
        <button type="button" className="go" onClick={() => zoom(0.12)} aria-label="Padidinti">+</button>
        <button type="button" className="go" onClick={fitView}>Talpinti</button>
      </div>
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
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#ff6d5a" />
            </marker>
          </defs>
          {edges.map(([a, b]) => {
            const na = lookup(a);
            const nb = lookup(b);
            if (!na || !nb) return null;
            const on = mode === "arch" ? true : edgeActive(a, b, events, runningTool, failed);
            const running = runningTool === b;
            return (
              <path
                key={`${a}-${b}`}
                d={edgePath(na, nb)}
                className={`edge${on ? " on" : ""}${running ? " flow" : ""}`}
                markerEnd={running ? "url(#arrow-run)" : on ? "url(#arrow-on)" : "url(#arrow)"}
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
          const st = mode === "arch" ? (selectedId === n.id ? "run" : "wait") : nodeState(n.id, events, runningTool, failed);
          const hidden = mode === "pipeline" && n.id === "escalate" && !failed && st === "wait";
          const arch = architecture?.layers?.find((l) => l.id === n.id);
          const ev = lastEvent(n.id, events);
          const summary = mode === "arch" ? (arch?.note || n.caption) : (nodeSummary(n.id, ev) || n.caption);
          const ports = portMap[n.id] || new Set(["left", "right"]);
          return (
            <button
              key={n.id}
              type="button"
              data-node={n.id}
              className={`n8n-node ${st}${selectedId === n.id ? " on" : ""}${hidden ? " ghost" : ""}`}
              style={{ left: n.x, top: n.y, "--hue": n.hue }}
              onClick={() => onSelect(n.id)}
              aria-pressed={selectedId === n.id}
              aria-label={n.label}
            >
              {[...ports].map((side) => (
                <span key={side} className={`n8n-port ${side}${st === "run" ? " live" : ""}`} />
              ))}
              <span className="n8n-ico"><Icon name={n.icon} size={20} /></span>
              <span className="n8n-copy">
                <b>{n.label}</b>
                <small>{summary}</small>
              </span>
              {st === "done" && (
                <span className="n8n-pip done" title={`${ev?.elapsed_ms ?? 0} ms`}>
                  <Check />
                </span>
              )}
              {st === "stop" && <span className="n8n-pip stop"><Bang /></span>}
              {st === "run" && <span className="n8n-pip run" />}
              {st === "done" && ev?.elapsed_ms != null && (
                <span className="n8n-ms">{ev.elapsed_ms} ms</span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
