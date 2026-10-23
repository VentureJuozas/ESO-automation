export default function PresentGuide({ pack, step, lang, playing, onPrev, onNext, onClose, onLang, onToggle, onRestart }) {
  const beats = pack?.beats || [];
  const beat = beats[step] || beats[0];
  if (!beat) return null;
  const copy = beat[lang] || beat.lt;
  const n = beats.length;
  const last = step >= n - 1;
  const totalMin = Math.round((pack?.total_ms || 270000) / 60000 * 10) / 10;
  return (
    <div className="present-bar" role="dialog" aria-label="Pristatymas" data-testid="present-bar">
      <div className="present-progress" aria-hidden>
        <div style={{ width: `${((step + 1) / n) * 100}%` }} />
      </div>
      <div className="present-row">
        <div className="present-copy">
          <div className="kicker" data-testid="present-kicker">
            {lang === "en" ? "Guided path" : "Vedamas kelias"} · {step + 1}/{n} · {playing ? (lang === "en" ? "autoplay" : "auto") : (lang === "en" ? "paused" : "pauzė")} · {totalMin} min
          </div>
          <h3 data-testid="present-title">{copy.title}</h3>
          <p data-testid="present-say">{copy.say}</p>
        </div>
        <div className="present-cluster">
          <div className="lang-switch" role="group" aria-label="Language">
            <button className={lang === "lt" ? "on" : ""} type="button" data-testid="present-lt" onClick={() => lang !== "lt" && onLang()}>LT</button>
            <button className={lang === "en" ? "on" : ""} type="button" data-testid="present-en" onClick={() => lang !== "en" && onLang()}>EN</button>
          </div>
          <button className="go" type="button" data-testid="present-toggle" onClick={onToggle}>
            {playing ? (lang === "en" ? "Pause" : "Pauzė") : last ? (lang === "en" ? "Done" : "Pabaiga") : (lang === "en" ? "Play" : "Tęsti")}
          </button>
          <button className="go" type="button" data-testid="present-prev" onClick={onPrev} disabled={step === 0}>←</button>
          <button className="exec" type="button" data-testid="present-next" onClick={onNext} disabled={last}>→</button>
          {last && (
            <button className="exec" type="button" data-testid="present-restart" onClick={onRestart}>
              {lang === "en" ? "Restart" : "Iš naujo"}
            </button>
          )}
          <button className="go" type="button" data-testid="present-exit" onClick={onClose}>{lang === "en" ? "Exit" : "Baigti"}</button>
        </div>
      </div>
    </div>
  );
}
