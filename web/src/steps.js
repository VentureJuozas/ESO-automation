export const GROUPS = [
  { id: "paraiska", title: "Paraiška", hue: "#ff6d5a", icon: "doc", tools: ["parse_request"] },
  { id: "taskas", title: "Taškas", hue: "#3b82f6", icon: "pin", tools: ["locate_connection_point"] },
  { id: "patikros", title: "Patikros", hue: "#7c5cfc", icon: "grid", tools: ["check_capacity", "check_voltage_drop", "check_reliability", "check_future"] },
  { id: "sprendinys", title: "Sprendinys", hue: "#d97706", icon: "branch", tools: ["select_solution", "size_breaker"] },
  { id: "isdavimas", title: "Išdavimas", hue: "#0f766e", icon: "send", tools: ["draft_ts_section3", "estimate_cost", "render_map", "engineer_approval", "issue_ts", "escalate"] },
];

export function groupOf(tool) {
  return GROUPS.find((g) => g.tools.includes(tool)) || GROUPS[0];
}

export function fmtLt(n, digits = 1) {
  if (n == null || Number.isNaN(n)) return "—";
  return Number(n).toLocaleString("lt-LT", { maximumFractionDigits: digits, minimumFractionDigits: digits });
}

export function fmtEur(n) {
  if (n == null) return "kaina nenurodyta";
  return Number(n).toLocaleString("lt-LT", { style: "currency", currency: "EUR" });
}

export function sourceLabel(tag) {
  return { real: "išmatuota", rule: "taisyklė", inferred: "išvesta", synthetic: "sintetinis" }[tag] || tag;
}
