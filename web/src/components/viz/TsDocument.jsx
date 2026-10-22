export default function TsDocument({ document: doc, section3, onChange, editable }) {
  if (!doc && !section3) return null;
  const text = section3 || doc?.section3 || "";
  return (
    <div className="section">
      <h3>Sąlygų juodraštis ir oficialus maketas</h3>
      <div className="ts-split">
        <div>
          <label htmlFor="s3">§3 tekstas {editable ? "(redaguojamas)" : ""}</label>
          <textarea id="s3" className="edit" value={text} onChange={(e) => onChange?.(e.target.value)} readOnly={!editable} />
        </div>
        <div className="ts-doc">
          {doc?.watermark && <div className="wm">{doc.watermark}</div>}
          <h4>Prijungimo sąlygos · {doc?.ts_number || "PROJEKTAS"}</h4>
          <p>Parengta: {doc?.issue_date || "—"} · Galioja iki: {doc?.valid_until || "—"}</p>
          <p>Objektas: {doc?.object_name} · {doc?.kw} kW · {doc?.phases}F</p>
          <p>Klientas / adresas: {doc?.customer} / {doc?.address}</p>
          <p><b>1.</b> {doc?.section1}</p>
          <p><b>3.</b> {text}</p>
        </div>
      </div>
    </div>
  );
}
