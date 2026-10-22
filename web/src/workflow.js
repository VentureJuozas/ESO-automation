/** n8n-style node graph for the TS pipeline and the architecture view. */

export const NODE_W = 220;
export const NODE_H = 76;
export const WORLD_W = 1120;
export const WORLD_H = 640;
export const INSPECTOR_PAD = 432;

const X = [36, 300, 564, 828];
const Y = [36, 196, 356, 516];

export const PIPELINE_NODES = [
  { id: "parse_request", label: "parse_request", caption: "Paraiška", x: X[0], y: Y[0], hue: "#ff6d5a", icon: "doc" },
  { id: "request_missing_data", label: "request_data", caption: "Duomenys", x: X[0], y: Y[3], hue: "#d97706", icon: "doc" },
  { id: "locate_connection_point", label: "locate_point", caption: "Taškas", x: X[1], y: Y[0], hue: "#3b82f6", icon: "pin" },
  { id: "select_solution", label: "select_solution", caption: "Sprendinys", x: X[2], y: Y[0], hue: "#d97706", icon: "branch" },
  { id: "size_breaker", label: "size_breaker", caption: "Jungiklis", x: X[3], y: Y[0], hue: "#d97706", icon: "branch" },
  { id: "check_capacity", label: "check_capacity", caption: "Pajėgumas", x: X[0], y: Y[1], hue: "#7c5cfc", icon: "grid" },
  { id: "check_voltage_drop", label: "check_voltage", caption: "Kokybė", x: X[1], y: Y[1], hue: "#7c5cfc", icon: "grid" },
  { id: "check_reliability", label: "check_reliability", caption: "Patikimumas", x: X[2], y: Y[1], hue: "#7c5cfc", icon: "grid" },
  { id: "check_future", label: "check_future", caption: "Ateitis", x: X[3], y: Y[1], hue: "#7c5cfc", icon: "grid" },
  { id: "draft_ts_section3", label: "draft_ts", caption: "Juodraštis", x: X[0], y: Y[2], hue: "#0f766e", icon: "send" },
  { id: "estimate_cost", label: "estimate_cost", caption: "Sąmata", x: X[1], y: Y[2], hue: "#0f766e", icon: "send" },
  { id: "render_map", label: "render_map", caption: "Žemėlapis", x: X[2], y: Y[2], hue: "#0f766e", icon: "pin" },
  { id: "engineer_approval", label: "approval", caption: "Inžinierius", x: X[3], y: Y[2], hue: "#ff6d5a", icon: "send" },
  { id: "issue_ts", label: "issue_ts", caption: "Išdavimas", x: X[3], y: Y[3], hue: "#0f766e", icon: "send" },
  { id: "escalate", label: "escalate", caption: "Eskalacija", x: X[2], y: Y[3], hue: "#e11d48", icon: "grid" },
];

export const PIPELINE_EDGES = [
  ["parse_request", "locate_connection_point"],
  ["parse_request", "request_missing_data"],
  ["locate_connection_point", "select_solution"],
  ["select_solution", "size_breaker"],
  ["size_breaker", "check_capacity"],
  ["check_capacity", "check_voltage_drop"],
  ["check_capacity", "escalate"],
  ["check_voltage_drop", "check_reliability"],
  ["check_reliability", "check_future"],
  ["check_future", "draft_ts_section3"],
  ["check_future", "escalate"],
  ["draft_ts_section3", "estimate_cost"],
  ["estimate_cost", "render_map"],
  ["render_map", "engineer_approval"],
  ["engineer_approval", "issue_ts"],
];

export const ARCH_NODES = [
  { id: "ui", label: "Dashboard", caption: "n8n drobė", x: X[0], y: 80, hue: "#ff6d5a", icon: "grid" },
  { id: "api", label: "FastAPI", caption: "REST + SSE", x: X[1], y: 80, hue: "#3b82f6", icon: "send" },
  { id: "graph", label: "LangGraph", caption: "Orkestratorius", x: X[2], y: 80, hue: "#7c5cfc", icon: "branch" },
  { id: "tools", label: "Python įrankiai", caption: "Sprendimai", x: X[3], y: 80, hue: "#0f766e", icon: "grid" },
  { id: "llm", label: "LLM", caption: "Tik tekstas", x: X[2], y: 280, hue: "#d97706", icon: "doc" },
  { id: "human", label: "Inžinierius", caption: "Patvirtinimas", x: X[1], y: 280, hue: "#ff6d5a", icon: "send" },
  { id: "data", label: "Duomenys", caption: "12-608 + taisyklės", x: X[3], y: 280, hue: "#1c1c1f", icon: "pin" },
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

export const ARCH_STICKIES = [
  {
    id: "arch-note",
    x: 36,
    y: 280,
    title: "Kaip tai veikia",
    body: "Python priima inžinerinius sprendimus. LLM skaito tekstą ir formuluoja §3. Sąlygas visada išduoda inžinierius.",
  },
];

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
      return o.id ? `Sprendinys ${o.id}` : "";
    case "size_breaker":
      return o.label || (o.amps != null ? `C ${o.amps} A` : "");
    case "check_capacity":
      if (o.pass === false) return "Nepraeina";
      return o.headroom_80_kw != null ? `atsarga ${o.headroom_80_kw} kW` : "";
    case "check_voltage_drop":
      return o.voltage_after_v != null ? `${o.voltage_after_v} V` : "";
    case "check_reliability":
      return o.cut_in?.applies ? `${o.cut_in.affected_customers} taškai` : "N-1 be rezervo";
    case "check_future":
      return o.headroom_kw != null ? `${o.headroom_kw} kW likutis` : "";
    case "draft_ts_section3":
      return "§3 juodraštis";
    case "estimate_cost":
      return o.net != null ? `${Math.round(o.net)} € be PVM` : "";
    case "render_map":
      return o.selected?.id || "";
    case "engineer_approval":
      return ev.type === "interrupt" ? "Laukia inžinieriaus" : "";
    case "issue_ts":
      return o.ts_number || "";
    case "escalate":
      return o.numbers?.after_kw != null ? `${o.numbers.after_kw} / ${o.numbers.limit_80_kw} kW` : (o.reason ? "Perduota" : "");
    default:
      return ev.title_lt || ev.caption || "";
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
