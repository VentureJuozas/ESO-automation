export async function getJSON(path) {
  const r = await fetch(path);
  if (!r.ok) throw new Error(`${path} ${r.status}`);
  return r.json();
}

export async function postJSON(path, body) {
  const r = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`${path} ${r.status}`);
  return r.json();
}

export function connectEvents(runId, onEvent, onError) {
  const es = new EventSource(`/api/runs/${runId}/events`);
  const handle = (ev) => {
    try {
      onEvent(JSON.parse(ev.data));
    } catch (err) {
      onError?.(err);
    }
  };
  ["tool", "interrupt", "status", "done", "error", "message"].forEach((t) => {
    es.addEventListener(t, handle);
  });
  es.onerror = () => onError?.(new Error("SSE"));
  return () => es.close();
}
