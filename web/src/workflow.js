/** Node graph for the TS pipeline. */

export const NODE_W = 220;
export const NODE_H = 76;
export const WORLD_W = 1120;
export const WORLD_H = 640;
export const INSPECTOR_PAD = 432;

const X = [36, 300, 564, 828];
const Y = [36, 196, 356, 516];

export const PIPELINE_NODES = [
  { id: "parse_request", label: "Read application", caption: "CRM", x: X[0], y: Y[0], hue: "#ff6d5a", icon: "doc" },
  { id: "locate_connection_point", label: "Connection point", caption: "GIS", x: X[1], y: Y[0], hue: "#3b82f6", icon: "pin" },
  { id: "select_solution", label: "Solution", caption: "A / B / C", x: X[2], y: Y[0], hue: "#d97706", icon: "branch" },
  { id: "size_breaker", label: "Breaker", caption: "§15", x: X[3], y: Y[0], hue: "#d97706", icon: "branch" },
  { id: "check_capacity", label: "Capacity", caption: "SCADA", x: X[0], y: Y[1], hue: "#7c5cfc", icon: "grid" },
  { id: "check_voltage_drop", label: "Voltage", caption: "50160", x: X[1], y: Y[1], hue: "#7c5cfc", icon: "grid" },
  { id: "check_reliability", label: "Reliability", caption: "N-1", x: X[2], y: Y[1], hue: "#7c5cfc", icon: "grid" },
  { id: "check_future", label: "Future load", caption: "Headroom", x: X[3], y: Y[1], hue: "#7c5cfc", icon: "grid" },
  { id: "draft_ts_section3", label: "Draft §3", caption: "TS registry", x: X[0], y: Y[2], hue: "#0f766e", icon: "send" },
  { id: "estimate_cost", label: "Cost", caption: "Catalogue", x: X[1], y: Y[2], hue: "#0f766e", icon: "send" },
  { id: "render_map", label: "Map", caption: "GIS annex", x: X[2], y: Y[2], hue: "#0f766e", icon: "pin" },
  { id: "engineer_approval", label: "Engineer", caption: "Gate", x: X[3], y: Y[2], hue: "#ff6d5a", icon: "send" },
  { id: "issue_ts", label: "Issue TS", caption: "Document", x: X[3], y: Y[3], hue: "#0f766e", icon: "send" },
];

export const PIPELINE_EDGES = [
  ["parse_request", "locate_connection_point"],
  ["locate_connection_point", "select_solution"],
  ["select_solution", "size_breaker"],
  ["size_breaker", "check_capacity"],
  ["check_capacity", "check_voltage_drop"],
  ["check_voltage_drop", "check_reliability"],
  ["check_reliability", "check_future"],
  ["check_future", "draft_ts_section3"],
  ["draft_ts_section3", "estimate_cost"],
  ["estimate_cost", "render_map"],
  ["render_map", "engineer_approval"],
  ["engineer_approval", "issue_ts"],
];

export const ARCH_NODES = [
  { id: "ui", label: "Dashboard", caption: "Node graph", x: X[0], y: 80, hue: "#ff6d5a", icon: "grid" },
  { id: "api", label: "FastAPI", caption: "REST + SSE", x: X[1], y: 80, hue: "#3b82f6", icon: "send" },
  { id: "graph", label: "LangGraph", caption: "Orchestrator", x: X[2], y: 80, hue: "#7c5cfc", icon: "branch" },
  { id: "tools", label: "Python tools", caption: "Decisions", x: X[3], y: 80, hue: "#0f766e", icon: "grid" },
  { id: "llm", label: "LLM", caption: "Text only", x: X[2], y: 280, hue: "#d97706", icon: "doc" },
  { id: "human", label: "Engineer", caption: "Approval", x: X[1], y: 280, hue: "#ff6d5a", icon: "send" },
  { id: "data", label: "Data", caption: "12-608 + rules", x: X[3], y: 280, hue: "#1c1c1f", icon: "pin" },
];

export const ARCH_EDGES = [
  ["ui", "api"],
  ["api", "graph"],
  ["graph", "tools"],
  ["graph", "llm"],
  ["graph", "human"],
  ["tools", "data"],
  ["human", "ui"],
];

export const ADAPTER_NODES = [
  { id: "gis", label: "GIS", caption: "Topology", x: X[0], y: 80, hue: "#3b82f6", icon: "pin" },
  { id: "capacity", label: "Power BI", caption: "Capacity", x: X[1], y: 80, hue: "#7c5cfc", icon: "grid" },
  { id: "crm", label: "CRM", caption: "Application", x: X[2], y: 80, hue: "#ff6d5a", icon: "doc" },
  { id: "pricing", label: "Pricing", caption: "Catalogue", x: X[3], y: 80, hue: "#d97706", icon: "send" },
  { id: "registry", label: "TS registry", caption: "Documents", x: X[1], y: 280, hue: "#0f766e", icon: "doc" },
];

export const ADAPTER_EDGES = [
  ["gis", "capacity"],
  ["crm", "gis"],
  ["capacity", "pricing"],
  ["pricing", "registry"],
  ["crm", "registry"],
];

export const ADAPTER_STICKIES = [];

export const ARCH_STICKIES = [];

export function nodeById(id, nodes = PIPELINE_NODES) {
  return nodes.find((n) => n.id === id);
}

function port(n, side) {
  if (side === "right") return { x: n.x + NODE_W, y: n.y + NODE_H / 2 };
  if (side === "left") return { x: n.x, y: n.y + NODE_H / 2 };
  if (side === "bottom") return { x: n.x + NODE_W / 2, y: n.y + NODE_H };
  return { x: n.x + NODE_W / 2, y: n.y };
}

export function edgeRoute(a, b) {
  const dx = b.x - a.x;
  const dy = b.y - a.y;
  if (Math.abs(dx) < 24 && dy > 40) return ["bottom", "top"];
  if (Math.abs(dx) < 24 && dy < -40) return ["top", "bottom"];
  return ["right", "left"];
}

export function edgePath(a, b) {
  const [from, to] = edgeRoute(a, b);
  const p1 = port(a, from);
  const p2 = port(b, to);
  const dx = b.x - a.x;
  if (dx < -40 && from === "right" && to === "left") {
    const midY = (p1.y + p2.y) / 2;
    return `M ${p1.x} ${p1.y} C ${p1.x + 48} ${p1.y}, ${p1.x + 48} ${midY}, ${(p1.x + p2.x) / 2} ${midY} C ${p2.x - 48} ${midY}, ${p2.x - 48} ${p2.y}, ${p2.x} ${p2.y}`;
  }
  const pull = 46;
  const c1 = { x: p1.x, y: p1.y };
  const c2 = { x: p2.x, y: p2.y };
  if (from === "right") c1.x += pull;
  if (from === "left") c1.x -= pull;
  if (from === "bottom") c1.y += pull;
  if (from === "top") c1.y -= pull;
  if (to === "right") c2.x += pull;
  if (to === "left") c2.x -= pull;
  if (to === "bottom") c2.y += pull;
  if (to === "top") c2.y -= pull;
  return `M ${p1.x} ${p1.y} C ${c1.x} ${c1.y}, ${c2.x} ${c2.y}, ${p2.x} ${p2.y}`;
}

export function nodePorts(id, nodes, edges) {
  const n = nodeById(id, nodes);
  const used = new Set();
  if (!n) return used;
  for (const [a, b] of edges) {
    if (a === id) {
      const other = nodeById(b, nodes);
      if (other) used.add(edgeRoute(n, other)[0]);
    }
    if (b === id) {
      const other = nodeById(a, nodes);
      if (other) used.add(edgeRoute(other, n)[1]);
    }
  }
  return used;
}

export function nodeSummary(id, ev) {
  if (!ev) return "";
  const o = ev.outputs || {};
  const p = o.parsed || {};
  switch (id) {
    case "parse_request":
      return p.kw != null ? `${p.kw} kW · ${p.phases}F` : "";
    case "locate_connection_point":
      return o.element_id ? `${o.element_id} · ${o.distance_m} m` : "";
    case "select_solution":
      return o.id ? `Solution ${o.id}` : "";
    case "size_breaker":
      return o.label || (o.amps != null ? `C ${o.amps} A` : "");
    case "check_capacity":
      if (o.pass === false) return "Fail";
      return o.headroom_80_kw != null ? `${o.headroom_80_kw} kW headroom` : "";
    case "check_voltage_drop":
      return o.voltage_after_v != null ? `${o.voltage_after_v} V` : "";
    case "check_reliability":
      return o.cut_in?.applies ? `${o.cut_in.affected_customers} points` : "N-1, no reserve";
    case "check_future":
      return o.headroom_kw != null ? `${o.headroom_kw} kW left` : "";
    case "draft_ts_section3":
      return "§3 draft";
    case "estimate_cost":
      return o.net != null ? `${Math.round(o.net)} € net` : "";
    case "render_map":
      return o.selected?.id || "";
    case "engineer_approval":
      return ev.type === "interrupt" ? "Awaiting engineer" : "";
    case "issue_ts":
      return o.ts_number || "";
    default:
      return ev.title || ev.caption || "";
  }
}

export function scenarioStickies(scenario) {
  if (!scenario) return [];
  return [
    {
      id: "scenario-note",
      x: 36,
      y: 516,
      title: scenario.title,
      body: [scenario.subtitle, scenario.notes].filter(Boolean).join(" · "),
    },
  ];
}
