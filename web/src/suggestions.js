import { ANALYSIS_CHILDREN, PIPELINE_NODES } from "./workflow.js";

export const STORE_KEY = "eso-suggestions";

export const REQUEST_STAGES = [
  {
    id: 1,
    title: "Engineer submits",
    detail: "Tool request plus the data or requirements documents.",
  },
  {
    id: 2,
    title: "AI builds the tool",
    detail: "Reads the documents and builds an auto-fillable tool. Inputs map to the case. Rules stay deterministic Python.",
  },
  {
    id: 3,
    title: "Tests on the back-test cases",
    detail: "Runs the new tool on the back-test cases and compares it with the source result.",
  },
  {
    id: 4,
    title: "Proposes an updated chain",
    detail: "Inserts the new node into the chain and sends it to review.",
  },
];

export const PLUG_STEPS = [
  ...PIPELINE_NODES.map((node) => ({
    id: node.id,
    label: `After ${node.label}`,
  })),
  ...ANALYSIS_CHILDREN.map((node) => ({
    id: node.id,
    label: `After ${node.label}`,
  })),
];

export const SAMPLE_REQUESTS = [
  {
    id: "sample-loss",
    sample: true,
    toolName: "Loss calculation (auto-fill)",
    purpose: "Fill feeder and transformer losses from the case data, using the documented method.",
    plugAfter: "check_capacity",
    documents: [{ name: "loss_method.xlsx", kind: "data" }],
    stage: 4,
    at: "2026-10-20T09:10:00",
    updatedAt: "2026-10-21T11:40:00",
  },
  {
    id: "sample-voltage",
    sample: true,
    toolName: "Voltage margin note",
    purpose: "Flag a feeder when the voltage after the new load falls under 207 V.",
    plugAfter: "check_voltage_drop",
    documents: [{ name: "en50160.pdf", kind: "requirements" }],
    stage: 3,
    at: "2026-10-21T14:05:00",
    updatedAt: "2026-10-22T08:20:00",
  },
  {
    id: "sample-headroom",
    sample: true,
    toolName: "Feeder headroom on the map",
    purpose: "Show the remaining transformer headroom on the connection map.",
    plugAfter: "render_map",
    documents: [{ name: "headroom.csv", kind: "data" }],
    stage: 2,
    at: "2026-10-22T10:30:00",
    updatedAt: "2026-10-22T16:15:00",
  },
  {
    id: "sample-coords",
    sample: true,
    toolName: "Missing coordinates letter",
    purpose: "Draft the request for coordinates when an application arrives without them.",
    plugAfter: "parse_request",
    documents: [{ name: "missing_fields.md", kind: "requirements" }],
    stage: 1,
    at: "2026-10-23T08:05:00",
    updatedAt: "2026-10-23T08:05:00",
  },
];

export function loadRequests() {
  let stored = [];
  try {
    const parsed = JSON.parse(localStorage.getItem(STORE_KEY) || "[]");
    if (Array.isArray(parsed)) stored = parsed.map(normalizeRequest);
  } catch {
    stored = [];
  }
  const ids = new Set(stored.map((item) => item.id));
  const samples = SAMPLE_REQUESTS.filter((item) => !ids.has(item.id)).map(normalizeRequest);
  return [...stored, ...samples];
}

export function saveRequests(items) {
  localStorage.setItem(STORE_KEY, JSON.stringify(items));
}

export function normalizeRequest(item) {
  const stage = Number(item.stage);
  const knownStage = stage >= 1 && stage <= 4;
  return {
    id: String(item.id),
    toolName: item.toolName || item.title || "Untitled tool",
    purpose: item.purpose || item.detail || "",
    engineer: item.engineer || "",
    plugAfter: item.plugAfter || "check_capacity",
    documents: Array.isArray(item.documents) ? item.documents.map((doc) => ({
      name: doc.name,
      kind: doc.kind || "document",
    })) : [],
    stage: knownStage ? stage : (item.toolName ? 1 : 4),
    sample: Boolean(item.sample),
    at: item.at || new Date().toISOString(),
    updatedAt: item.updatedAt || item.at || new Date().toISOString(),
  };
}

export function stageLabel(stage) {
  return REQUEST_STAGES.find((item) => item.id === stage)?.title || "Submitted";
}
