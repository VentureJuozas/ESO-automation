export default function WhatIfBar({ values, onChange, onLive, busy }) {
  return (
    <div className="whatif-bar">
      <div className="kicker">What-if, gyvas perskaičiavimas</div>
      <label>
        kW {values.kw}
        <input data-testid="whatif-kw" type="range" min="3" max="120" step="1" value={values.kw} onChange={(e) => onChange({ ...values, kw: Number(e.target.value) })} />
      </label>
      <label>
        Fazės
        <select value={values.phases} onChange={(e) => onChange({ ...values, phases: Number(e.target.value) })}>
          <option value={1}>1F</option>
          <option value={3}>3F</option>
        </select>
      </label>
      <label>
        Atstumas {values.distance_m} m
        <input type="range" min="8" max="400" step="2" value={values.distance_m} onChange={(e) => onChange({ ...values, distance_m: Number(e.target.value) })} />
      </label>
      <label className="chk">
        <input
          type="checkbox"
          checked={values.pending_kw > 0}
          onChange={(e) => onChange({ ...values, pending_kw: e.target.checked ? 40 : 0 })}
        />
        Rezervuota +40 kW
      </label>
      <button className="go" type="button" data-testid="whatif-run" disabled={busy} onClick={() => onLive(values)}>Skaičiuoti</button>
    </div>
  );
}
