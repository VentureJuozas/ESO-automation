import { fmtEur } from "../../steps.js";
import SourceTags from "../SourceTags.jsx";

export default function CostTable({ cost }) {
  if (!cost) return null;
  const vat = (cost.gross || 0) - (cost.net || 0);
  return (
    <div className="section">
      <h3>Sąmata (orientyras 26-E-37934)</h3>
      <table className="cost">
        <thead>
          <tr><th>Eilutė</th><th>Kiekis</th><th>Šaltinis</th><th>Suma</th></tr>
        </thead>
        <tbody>
          {(cost.lines || []).map((l) => (
            <tr key={l.id}>
              <td>
                {l.item}
                {l.note && <small>{l.note}</small>}
              </td>
              <td>{l.qty} {l.unit}</td>
              <td><SourceTags tags={[l.source]} /></td>
              <td>{fmtEur(l.price)}</td>
            </tr>
          ))}
          <tr className="sum"><td colSpan={3}>Medžiagos</td><td>{fmtEur(cost.materials)}</td></tr>
          <tr className="sum"><td colSpan={3}>Kapitalizuotas darbas 11,78 %</td><td>{fmtEur(cost.labour)}</td></tr>
          <tr className="sum"><td colSpan={3}>Iš viso be PVM</td><td>{fmtEur(cost.net)}</td></tr>
          <tr className="sum"><td colSpan={3}>PVM 21 %</td><td>{fmtEur(vat)}</td></tr>
          <tr className="sum total"><td colSpan={3}>Iš viso su PVM</td><td>{fmtEur(cost.gross)}</td></tr>
        </tbody>
      </table>
      <p className="map-note">{cost.note} <SourceTags tags={["real", "synthetic"]} /></p>
    </div>
  );
}
