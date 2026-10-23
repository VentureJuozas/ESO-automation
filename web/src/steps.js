export const GROUPS = [
  { id: "application", title: "Application", hue: "#20366c", icon: "doc", tools: ["parse_request"] },
  { id: "connection", title: "Connection point", hue: "#4d6a9a", icon: "pin", tools: ["locate_connection_point", "render_map"] },
  { id: "checks", title: "Analysis", hue: "#35548a", icon: "grid", tools: ["check_capacity", "check_voltage_drop", "check_reliability", "check_future"] },
  { id: "solution", title: "Solution", hue: "#7a9620", icon: "branch", tools: ["select_solution", "size_breaker", "estimate_cost"] },
  { id: "issue", title: "Issue", hue: "#6d8a22", icon: "send", tools: ["draft_ts_section3", "engineer_approval", "issue_ts"] },
];

export const STEP_LABEL = {
  parse_request: "Read application",
  locate_connection_point: "Locate point",
  render_map: "Map",
  check_capacity: "Capacity",
  check_voltage_drop: "Voltage",
  check_reliability: "Reliability",
  check_future: "Future load",
  select_solution: "Solution",
  size_breaker: "Breaker",
  estimate_cost: "Cost",
  draft_ts_section3: "Draft §3",
  engineer_approval: "Engineer",
  issue_ts: "Issue TS",
};

export function groupOf(tool) {
  return GROUPS.find((g) => g.tools.includes(tool)) || GROUPS[0];
}

export function fmtNum(n, digits = 1) {
  if (n == null || Number.isNaN(n)) return "—";
  return Number(n).toLocaleString("en-GB", { maximumFractionDigits: digits, minimumFractionDigits: digits });
}

export function fmtEur(n) {
  if (n == null) return "—";
  return Number(n).toLocaleString("en-GB", { style: "currency", currency: "EUR" });
}

export const fmtLt = fmtNum;
