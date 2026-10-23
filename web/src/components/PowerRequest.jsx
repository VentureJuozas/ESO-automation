import { useEffect, useState } from "react";

const EMPTY = {
  objectName: "Household connection",
  kw: "11",
  phases: "3",
  lat: "54.55929",
  lon: "25.27955",
};

export default function PowerRequest({ busy, onSubmit, draft }) {
  const [form, setForm] = useState(EMPTY);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!draft) return;
    setForm({
      objectName: draft.objectName,
      kw: String(draft.kw),
      phases: String(draft.phases),
      lat: String(draft.lat),
      lon: String(draft.lon),
    });
    setError("");
  }, [draft]);

  function setField(key, value) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  async function submit(event) {
    event.preventDefault();
    const kw = Number(form.kw);
    const phases = Number(form.phases);
    const lat = Number(form.lat);
    const lon = Number(form.lon);
    const objectName = form.objectName.trim();
    if (!objectName || !Number.isFinite(kw) || kw <= 0 || kw > 500) {
      setError("Enter an object name and a power between 1 and 500 kW.");
      return;
    }
    if (phases !== 1 && phases !== 3) {
      setError("Phases must be 1 or 3.");
      return;
    }
    if (!Number.isFinite(lat) || !Number.isFinite(lon)) {
      setError("Enter numeric coordinates.");
      return;
    }
    setError("");
    try {
      await onSubmit({ objectName, kw, phases, lat, lon });
    } catch (ex) {
      setError(String(ex.message || ex));
    }
  }

  return (
    <div className="change-view" data-testid="power-request">
      <div className="change-wrap power-wrap">
        <p className="change-kicker">New connection</p>
        <h1>Request power</h1>
        {draft?.note && <p className="test-lead">{draft.title}. {draft.note}.</p>}
        <form className="tool-card" onSubmit={submit}>
          <header>
            <b>New power request</b>
            <span>opens on the flow</span>
          </header>
          <label htmlFor="power-object">Object</label>
          <input
            id="power-object"
            data-testid="power-object"
            value={form.objectName}
            onChange={(event) => setField("objectName", event.target.value)}
            required
          />
          <div className="power-row">
            <div>
              <label htmlFor="power-kw">Requested power (kW)</label>
              <input
                id="power-kw"
                data-testid="power-kw"
                type="number"
                min="1"
                max="500"
                step="0.1"
                value={form.kw}
                onChange={(event) => setField("kw", event.target.value)}
                required
              />
            </div>
            <div>
              <label htmlFor="power-phases">Phases</label>
              <select
                id="power-phases"
                data-testid="power-phases"
                value={form.phases}
                onChange={(event) => setField("phases", event.target.value)}
              >
                <option value="1">1-phase</option>
                <option value="3">3-phase</option>
              </select>
            </div>
          </div>
          <div className="power-row">
            <div>
              <label htmlFor="power-lat">Latitude</label>
              <input
                id="power-lat"
                data-testid="power-lat"
                type="number"
                step="any"
                value={form.lat}
                onChange={(event) => setField("lat", event.target.value)}
                required
              />
            </div>
            <div>
              <label htmlFor="power-lon">Longitude</label>
              <input
                id="power-lon"
                data-testid="power-lon"
                type="number"
                step="any"
                value={form.lon}
                onChange={(event) => setField("lon", event.target.value)}
                required
              />
            </div>
          </div>
          {error && <p className="power-error">{error}</p>}
          <div className="tool-actions">
            <button className="exec" type="submit" data-testid="power-submit" disabled={busy}>
              Open on the flow
            </button>
          </div>
        </form>
        <p className="change-foot">Opens on the flow. Press Start to run it.</p>
      </div>
    </div>
  );
}
