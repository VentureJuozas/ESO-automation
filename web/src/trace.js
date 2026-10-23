export const KIND_EN = { llm: "LLM", tool: "Python", human: "Human" };
export const KIND_HINT = {
  llm: "Reads the request or phrases §3.",
  tool: "Deterministic rule.",
  human: "Engineer gate.",
};

export function classify(toolId, event, catalog = []) {
  const meta = catalog.find((t) => t.id === toolId) || {};
  const kind = event?.kind || meta.kind;
  if (kind === "llm" || toolId === "parse_request" || toolId === "draft_ts_section3") return "llm";
  if (kind === "human" || toolId === "engineer_approval" || toolId === "request_missing_data") return "human";
  if (event?.type === "interrupt" && (toolId === "engineer_approval" || toolId === "request_missing_data")) return "human";
  return "tool";
}

function summarise(payload, limit = 180) {
  if (payload == null) return "—";
  if (typeof payload === "string") return payload.length <= limit ? payload : `${payload.slice(0, limit - 1)}…`;
  if (typeof payload !== "object") return String(payload);
  if (Array.isArray(payload)) return `${payload.length} items`;
  const keys = ["kw", "phases", "id", "label", "feeder", "element_id", "ts_number", "pass", "escalate", "section3"];
  const bits = [];
  for (const k of keys) {
    const val = payload[k];
    if (val == null || val === "" || typeof val === "object") continue;
    bits.push(typeof val === "string" && val.length > 40 ? `${k}=${val.slice(0, 36)}…` : `${k}=${val}`);
    if (bits.length >= 4) break;
  }
  return bits.join(", ") || Object.keys(payload).slice(0, 4).join(", ") || "—";
}

export function buildTrace(events = [], catalog = []) {
  const steps = [];
  let n = 0;
  for (const ev of events) {
    if (ev.type !== "tool" && ev.type !== "interrupt") continue;
    if (!ev.tool) continue;
    n += 1;
    const meta = catalog.find((t) => t.id === ev.tool) || {};
    const kind = classify(ev.tool, ev, catalog);
    const ref = ev.rule_ref || meta.rule_ref || {};
    steps.push({
      step: n,
      tool: ev.tool,
      title: ev.title || meta.title || ev.tool,
      kind,
      kind_en: KIND_EN[kind],
      llm_role: ev.tool === "parse_request" ? "parse" : ev.tool === "draft_ts_section3" ? "phrase" : null,
      hint: KIND_HINT[kind],
      inputs: ev.inputs || {},
      outputs: ev.outputs || {},
      input_summary: summarise(ev.inputs),
      output_summary: summarise(ev.outputs),
      elapsed_ms: ev.elapsed_ms || 0,
      rule_ref: { label: ref.label || meta.rule, local: ref.local, url: ref.url },
      ok: ev.ok !== false,
      type: ev.type,
    });
  }
  const llm = steps.filter((s) => s.kind === "llm").length;
  const python = steps.filter((s) => s.kind === "tool").length;
  const human = steps.filter((s) => s.kind === "human").length;
  return {
    steps,
    stats: {
      llm,
      python,
      human,
      line: `${llm} LLM · ${python} Python · ${human} Human`,
    },
  };
}
