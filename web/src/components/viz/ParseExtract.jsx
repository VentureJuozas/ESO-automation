import SourceTags from "../SourceTags.jsx";

const FIELD_LT = {
  kw: "Galia",
  phases: "Fazės",
  coords: "Koordinatės",
  object_name: "Objektas",
};

function highlight(text, highlights = []) {
  if (!text) return <span className="muted">Nėra šaltinio teksto — skaityta iš formos.</span>;
  const marks = [...highlights]
    .filter((h) => h.start != null && h.end != null && h.start < h.end)
    .sort((a, b) => a.start - b.start);
  const out = [];
  let cursor = 0;
  marks.forEach((h, i) => {
    const start = Math.max(cursor, h.start);
    const end = Math.min(text.length, h.end);
    if (start > cursor) out.push(<span key={`t${i}`}>{text.slice(cursor, start)}</span>);
    if (end > start) {
      out.push(<mark key={`m${i}`} data-field={h.field} title={FIELD_LT[h.field] || h.field}>{text.slice(start, end)}</mark>);
      cursor = end;
    }
  });
  if (cursor < text.length) out.push(<span key="tail">{text.slice(cursor)}</span>);
  return out;
}

export default function ParseExtract({ outputs }) {
  if (!outputs) return null;
  const parsed = outputs.parsed || {};
  const extraction = outputs.extraction || {};
  const highlights = outputs.highlights || [];
  const fields = Object.values(extraction);
  return (
    <div className="section">
      <h3>Išskaityti laukai</h3>
      <div className="extract-grid">
        {["kw", "phases", "coords", "object_name"].map((key) => {
          const hit = extraction[key];
          const value = key === "coords"
            ? (hit?.value ? `${hit.value[0]}, ${hit.value[1]}` : `${parsed.lat}, ${parsed.lon}`)
            : (hit?.value ?? parsed[key]);
          const conf = hit?.confidence ?? (hit ? 0.5 : 0);
          return (
            <div key={key} className="extract-card">
              <b>{FIELD_LT[key] || key}</b>
              <span>{value ?? "—"}</span>
              <i style={{ width: `${Math.round(conf * 100)}%` }} />
              <small>{hit ? `${hit.source} · ${Math.round(conf * 100)} %` : "nėra"}</small>
            </div>
          );
        })}
      </div>
      <h3>Šaltinio tekstas</h3>
      <pre className="source-text">{highlight(outputs.source_text || parsed.source_text, highlights)}</pre>
      {fields.length === 0 && <p className="map-note">Offline parseris naudojo formos reikšmes.</p>}
      <p className="map-note">
        Klientas: {outputs.customer_placeholder}. {outputs.address_placeholder}
        <SourceTags tags={["synthetic", parsed.source_tags].flat()} />
      </p>
    </div>
  );
}
