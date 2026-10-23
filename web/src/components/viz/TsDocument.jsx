export default function TsDocument({ document: doc, section3, onChange, editable, runId }) {
  if (!doc && !section3) return null;
  const text = section3 || doc?.section3 || "";
  return (
    <div className="section">
      <div className="ts-toolbar">
        <h3>Prijungimo sąlygų dokumentas</h3>
        {runId && (
          <span style={{ display: "flex", gap: 8 }}>
            <a className="go" href={`/api/runs/${runId}/ts.html`} target="_blank" rel="noreferrer">HTML</a>
            <a className="go" href={`/api/runs/${runId}/ts.pdf`} target="_blank" rel="noreferrer">PDF</a>
            <a className="go" href={`/api/runs/${runId}/ts.docx`}>Word</a>
          </span>
        )}
      </div>
      {editable && (
        <label htmlFor="s3" className="ts-edit-label">§3</label>
      )}
      {editable && (
        <textarea id="s3" className="edit" value={text} onChange={(e) => onChange?.(e.target.value)} />
      )}
      {runId ? (
        <iframe
          className="ts-frame"
          title="Prijungimo sąlygos"
          src={`/api/runs/${runId}/ts.html`}
        />
      ) : (
        <p className="ts-s3">{text}</p>
      )}
    </div>
  );
}
