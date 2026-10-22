/** n8n-style node graph for the TS pipeline and the architecture view. */

export const PIPELINE_NODES = [
  { id: "parse_request", label: "parse_request", caption: "Paraiška", x: 48, y: 36, hue: "#ff6d5a", icon: "doc" },
  { id: "locate_connection_point", label: "locate_point", caption: "Taškas", x: 292, y: 36, hue: "#3b82f6", icon: "pin" },
  { id: "select_solution", label: "select_solution", caption: "Sprendinys", x: 536, y: 36, hue: "#d97706", icon: "branch" },
  { id: "size_breaker", label: "size_breaker", caption: "Jungiklis", x: 780, y: 36, hue: "#d97706", icon: "branch" },
  { id: "check_capacity", label: "check_capacity", caption: "Pajėgumas", x: 48, y: 188, hue: "#7c5cfc", icon: "grid" },
  { id: "check_voltage_drop", label: "check_voltage", caption: "Kokybė", x: 292, y: 188, hue: "#7c5cfc", icon: "grid" },
  { id: "check_reliability", label: "check_reliability", caption: "Patikimumas", x: 536, y: 188, hue: "#7c5cfc", icon: "grid" },
  { id: "check_future", label: "check_future", caption: "Ateitis", x: 780, y: 188, hue: "#7c5cfc", icon: "grid" },
  { id: "draft_ts_section3", label: "draft_ts", caption: "Juodraštis", x: 48, y: 340, hue: "#0f766e", icon: "send" },
  { id: "estimate_cost", label: "estimate_cost", caption: "Sąmata", x: 292, y: 340, hue: "#0f766e", icon: "send" },
  { id: "render_map", label: "render_map", caption: "Žemėlapis", x: 536, y: 340, hue: "#0f766e", icon: "pin" },
  { id: "engineer_approval", label: "approval", caption: "Inžinierius", x: 780, y: 340, hue: "#ff6d5a", icon: "send" },
  { id: "issue_ts", label: "issue_ts", caption: "Išdavimas", x: 1024, y: 340, hue: "#0f766e", icon: "send" },
  { id: "escalate", label: "escalate", caption: "Eskalacija", x: 1024, y: 188, hue: "#e11d48", icon: "grid" },
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
  ["check_future", "escalate"],
  ["draft_ts_section3", "estimate_cost"],
  ["escalate", "estimate_cost"],
  ["estimate_cost", "render_map"],
  ["render_map", "engineer_approval"],
  ["engineer_approval", "issue_ts"],
];

export const ARCH_NODES = [
  { id: "ui", label: "Dashboard", caption: "n8n drobė", x: 40, y: 80, hue: "#ff6d5a", icon: "grid" },
  { id: "api", label: "FastAPI", caption: "REST + SSE", x: 280, y: 80, hue: "#3b82f6", icon: "send" },
  { id: "graph", label: "LangGraph", caption: "Orkestratorius", x: 520, y: 80, hue: "#7c5cfc", icon: "branch" },
  { id: "llm", label: "LLM", caption: "Tekstas tik", x: 520, y: 240, hue: "#d97706", icon: "doc" },
  { id: "tools", label: "Python įrankiai", caption: "Sprendimai", x: 760, y: 80, hue: "#0f766e", icon: "grid" },
  { id: "data", label: "Duomenys", caption: "12-608 + taisyklės", x: 1000, y: 80, hue: "#1c1c1f", icon: "pin" },
  { id: "human", label: "Inžinierius", caption: "Patvirtinimas", x: 760, y: 240, hue: "#ff6d5a", icon: "send" },
];

export const ARCH_EDGES = [
  ["ui", "api"],
  ["api", "graph"],
  ["graph", "llm"],
  ["graph", "tools"],
  ["tools", "data"],
  ["graph", "human"],
  ["human", "ui"],
];

export const NODE_W = 200;
export const NODE_H = 64;

export function nodeById(id, nodes = PIPELINE_NODES) {
  return nodes.find((n) => n.id === id);
}

export function edgePath(a, b) {
  const x1 = a.x + NODE_W;
  const y1 = a.y + NODE_H / 2;
  const x2 = b.x;
  const y2 = b.y + NODE_H / 2;
  const dx = Math.max(40, (x2 - x1) / 2);
  if (x2 >= x1 - 8) {
    return `M ${x1} ${y1} C ${x1 + dx} ${y1}, ${x2 - dx} ${y2}, ${x2} ${y2}`;
  }
  const midY = (y1 + y2) / 2;
  return `M ${x1} ${y1} C ${x1 + 36} ${y1}, ${x1 + 36} ${midY}, ${(x1 + x2) / 2} ${midY} C ${x2 - 36} ${midY}, ${x2 - 36} ${y2}, ${x2} ${y2}`;
}
