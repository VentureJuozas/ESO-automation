export default function PresentGuide({ pack, step, lang, onPrev, onNext, onClose, onLang }) {
  const beats = pack?.beats || [];
  const beat = beats[step] || beats[0];
  if (!beat) return null;
  const copy = beat[lang] || beat.lt;
  const n = beats.length;
  return (
    <div className="present-bar" role="dialog" aria-label="Pristatymas">
      <div className="present-progress" aria-hidden>
        <div style={{ width: `${((step + 1) / n) * 100}%` }} />
      </div>
      <div className="present-row">
        <div>
          <div className="kicker">{lang === "en" ? "Guided path" : "Vedamas kelias"} · {step + 1}/{n}</div>
          <h3>{copy.title}</h3>
          <p>{copy.say}</p>
        </div>
        <div className="present-nav">
          <button className="go" type="button" onClick={onLang}>{lang === "en" ? "LT" : "EN"}</button>
          <button className="go" type="button" onClick={onPrev} disabled={step === 0}>←</button>
          <button className="exec" type="button" onClick={onNext} disabled={step >= n - 1}>→</button>
          <button className="go" type="button" onClick={onClose}>{lang === "en" ? "Exit" : "Baigti"}</button>
        </div>
      </div>
    </div>
  );
}
