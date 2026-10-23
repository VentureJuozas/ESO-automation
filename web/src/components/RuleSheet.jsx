import SourceTags from "./SourceTags.jsx";

export default function RuleSheet({ toolId, catalog }) {
  const meta = (catalog?.tools || []).find((t) => t.id === toolId);
  if (!meta) {
    return <div className="empty">Pasirinkite mazgą drobėje — taisyklė atsidaro čia, kaip n8n mazgo nustatymai.</div>;
  }
  const tags = [];
  if (meta.data?.includes("real") || meta.data?.includes("išmatu")) tags.push("real");
  if (meta.data?.includes("rule") || meta.kind === "human") tags.push("rule");
  if (meta.data?.includes("inferred") || meta.data?.includes("išvest")) tags.push("inferred");
  if (meta.data?.includes("synthetic") || meta.data?.includes("sintet")) tags.push("synthetic");
  return (
    <div>
      <p className="hint">{meta.engineer}</p>
      <div className="section">
        <h3>Įvestis</h3>
        <p>{meta.inputs}</p>
      </div>
      <div className="section">
        <h3>Išvestis</h3>
        <p>{meta.outputs}</p>
      </div>
      <div className="section">
        <h3>Taisyklė</h3>
        <p>{meta.rule}</p>
        {meta.rule_ref && (
          <p className="rule" style={{ marginTop: 8 }}>
            <a href={meta.rule_ref.url} target="_blank" rel="noreferrer">{meta.rule_ref.label} ↗</a>
            {meta.rule_ref.local && <span style={{ color: "var(--muted)" }}>, {meta.rule_ref.local}</span>}
          </p>
        )}
      </div>
      <div className="section">
        <h3>Duomenys</h3>
        <p>{meta.data}</p>
        <SourceTags tags={tags} />
      </div>
    </div>
  );
}
