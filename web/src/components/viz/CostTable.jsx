import { fmtEur } from "../../steps.js";

export default function CostTable({ cost }) {
  if (!cost) return null;
  return (
    <div className="section">
      <h3>Sąmata (orientyras)</h3>
      <table className="cost">
        <tbody>
          {(cost.lines || []).map((l) => (
            <tr key={l.id}><td>{l.item}</td><td>{fmtEur(l.price)}</td></tr>
          ))}
          <tr><td>Iš viso be PVM</td><td>{fmtEur(cost.net)}</td></tr>
          <tr><td>Iš viso su PVM 21 %</td><td>{fmtEur(cost.gross)}</td></tr>
        </tbody>
      </table>
      <p style={{ color: "var(--muted)", fontSize: 12 }}>{cost.note}</p>
    </div>
  );
}
