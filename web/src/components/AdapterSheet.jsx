export default function AdapterSheet({ adapter }) {
  if (!adapter) return <p className="empty">Pasirinkite adapterio mazgą.</p>;
  return (
    <div>
      <p className="hint">{adapter.real_system}</p>
      <div className="kv">
        <div><span>Būsena</span><b className={`st ${adapter.mode}`}>{adapter.mode}</b></div>
        <div><span>Tiekia</span><b>{adapter.supplies}</b></div>
        <div><span>Vartoja</span><b>{(adapter.consumed_by || []).join(", ")}</b></div>
      </div>
      <p className="assume">
        {adapter.mode === "mock"
          ? "Mock: dabartiniai 12-608 / redaguoti duomenys."
          : "Stub: dokumentuotas kelias, neprijungta."}
      </p>
    </div>
  );
}
