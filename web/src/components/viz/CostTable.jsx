import { fmtEur } from "../../steps.js";

export default function CostTable({ cost }) {
  if (!cost) return null;
  const vat = (cost.gross || 0) - (cost.net || 0);
  return (
    <div className="section">
      <table className="cost">
        <thead>
          <tr><th>Item</th><th>Qty</th><th>Amount</th></tr>
        </thead>
        <tbody>
          {(cost.lines || []).map((l) => (
            <tr key={l.id}>
              <td>{l.item}</td>
              <td>{l.qty} {l.unit}</td>
              <td>{fmtEur(l.price)}</td>
            </tr>
          ))}
          <tr className="sum"><td colSpan={2}>Materials</td><td>{fmtEur(cost.materials)}</td></tr>
          <tr className="sum"><td colSpan={2}>Labour 11.78 %</td><td>{fmtEur(cost.labour)}</td></tr>
          <tr className="sum"><td colSpan={2}>Net</td><td>{fmtEur(cost.net)}</td></tr>
          <tr className="sum"><td colSpan={2}>VAT 21 %</td><td>{fmtEur(vat)}</td></tr>
          <tr className="sum total"><td colSpan={2}>Gross</td><td>{fmtEur(cost.gross)}</td></tr>
        </tbody>
      </table>
    </div>
  );
}
