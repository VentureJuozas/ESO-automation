export default function BreakerTable({ table = [], selected, requestedKw }) {
  if (!table.length) return null;
  const amps = selected?.amps;
  const phases = selected?.phases || table[0]?.phases || 3;
  return (
    <div className="section">
      <p className="formula">{requestedKw ?? selected?.kw} kW, {phases}-phase → {selected?.label || `C ${amps} A`}</p>
      <div className="table-wrap">
        <table className="grid-table">
          <thead>
            <tr><th>Up to kW</th><th>C, A</th><th>Phases</th></tr>
          </thead>
          <tbody>
            {table.map((row) => {
              const on = row.amps === amps && row.kw_max === selected?.table_bound_kw;
              return (
                <tr key={`${row.kw_max}-${row.amps}`} className={on ? "hi" : ""}>
                  <td>≤ {row.kw_max}</td>
                  <td>C {row.amps} A</td>
                  <td>{row.phases}F</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
