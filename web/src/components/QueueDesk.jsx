import { useState } from "react";

const STATUS_LT = {
  new: "Nauja",
  running: "Vykdoma",
  awaiting_approval: "Laukia inžinieriaus",
  issued: "Išduota",
  escalated: "Eskaluota",
  error: "Klaida",
  queued: "Eilėje",
  waiting_data: "Laukia duomenų",
};

function slaLabel(sla) {
  if (!sla) return "—";
  if (sla.overdue) return "Vėluoja";
  const s = Math.max(0, sla.remaining_s || 0);
  const d = Math.floor(s / 86400);
  const h = Math.floor((s % 86400) / 3600);
  if (sla.due_today) return h > 0 ? `Šiandien · ${h} h` : "Šiandien";
  return d > 0 ? `${d} d ${h} h` : `${h} h`;
}

function when(ts) {
  if (!ts) return "—";
  return new Date(ts * 1000).toLocaleString("lt-LT", {
    hour: "2-digit",
    minute: "2-digit",
    day: "2-digit",
    month: "2-digit",
  });
}

function InboxCard({ item, reason, setReason, section3, setSection3, busy, onApprove, onOverride, onEdit, onOpen }) {
  const waiting = item.status === "awaiting_approval";
  const failed = item.status === "escalated";
  return (
    <article className={`inbox-card${failed ? " bad" : ""}`} data-testid={`inbox-card-${item.id}`} data-title={item.title}>
      <header>
        <b>{item.title}</b>
        <span className={`st ${item.status}`}>{STATUS_LT[item.status] || item.status}</span>
      </header>
      <p>{item.kw || "—"} kW · {item.solution || item.mix || "—"} · {item.assignee}</p>
      {failed && (
        <>
          <p className="hint bad-hint">{item.brief_title || "Stiprinimo paketas"} · {item.failed_at || "check_capacity"}</p>
          <textarea
            className="edit"
            placeholder="Override priežastis (mažiausiai 8 simboliai)…"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
          />
        </>
      )}
      {waiting && (
        <textarea
          className="edit"
          placeholder="§3 pataisa (neprivaloma)…"
          value={section3}
          onChange={(e) => setSection3(e.target.value)}
        />
      )}
      <div className="inbox-actions">
        <button className="go" type="button" onClick={() => onOpen(item)}>Drobė</button>
        {item.run_id && (
          <a className="go" href={`/api/runs/${item.run_id}/audit.html`} target="_blank" rel="noreferrer">Auditas</a>
        )}
        {failed && item.run_id && (
          <a className="go" data-testid={`inbox-brief-${item.id}`} href={`/api/runs/${item.run_id}/brief.html`} target="_blank" rel="noreferrer">Paketas</a>
        )}
        {waiting && (
          <>
            <button className="go" type="button" disabled={busy} onClick={() => onEdit(item, section3)}>Įrašyti §3</button>
            <button className="exec" type="button" data-testid={`inbox-approve-${item.id}`} disabled={busy} onClick={() => onApprove(item, section3)}>Patvirtinti</button>
          </>
        )}
        {failed && (
          <button className="ink" type="button" disabled={busy || (reason || "").trim().length < 8} onClick={() => onOverride(item, reason)}>
            Override
          </button>
        )}
      </div>
    </article>
  );
}

export default function QueueDesk({
  queue,
  batching,
  busy,
  onBatch,
  onReset,
  onOpen,
  onApprove,
  onOverride,
  onEdit,
}) {
  const hud = queue?.hud || {};
  const cases = queue?.cases || [];
  const inbox = queue?.inbox || [];
  const [reasons, setReasons] = useState({});
  const [edits, setEdits] = useState({});

  return (
    <div className="desk">
      <div className="desk-main">
        <header className="desk-head">
          <div>
            <div className="kicker">Vadovo eilė · TP 12-608</div>
            <h2>Šiandienos paraiškos</h2>
            <p className="hint">Sintetinės, redaguotos bylos. SLA — 3 darbo dienos (KNOWLEDGE §5, buitinis ≤250 kW).</p>
          </div>
          <div className="desk-actions">
            <button className="go" type="button" onClick={onReset} disabled={batching}>Atstatyti demo</button>
            <button className="exec" type="button" onClick={onBatch} disabled={batching || hud.new === 0}>
              {batching ? "Vykdoma…" : "Paleisti visas"}
            </button>
          </div>
        </header>
        <div className="hud-grid" data-spot-target="hud">
          <div className="hud"><b>{hud.processed ?? 0}</b><span>Apdorota šiandien</span></div>
          <div className="hud"><b>{hud.saved_min_today ?? 0}</b><span>Inž. min. sutaupyta šiandien</span></div>
          <div className="hud"><b>{hud.monthly_hours ?? 0} h</b><span>Šį mėnesį (prielaida)</span></div>
          <div className="hud"><b>{hud.inbox_depth ?? 0}</b><span>Patvirtinimo eilė</span></div>
        </div>
        <p className="assume">{hud.note || "Minutės ir 40 bylų / mėn. — prielaida, ne ESO statistika."}</p>
        <div className="table-wrap desk-table" data-spot-target="table">
          <table className="grid-table">
            <thead>
              <tr>
                <th>Byla</th>
                <th>Mix</th>
                <th>kW</th>
                <th>Būsena</th>
                <th>SLA</th>
                <th>Priskirta</th>
                <th>Pateikta</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {cases.map((c) => (
                <tr key={c.id} className={c.status === "running" ? "hi" : ""} onClick={() => onOpen(c)}>
                  <td>
                    <b>{c.title}</b>
                    <small> {c.id}{c.data_gap ? " · trūksta duomenų" : ""}</small>
                  </td>
                  <td><span className={`mix ${c.mix}`}>{c.mix}</span></td>
                  <td>{c.kw ?? "—"}</td>
                  <td><span className={`st ${c.status}`}>{STATUS_LT[c.status] || c.status}</span></td>
                  <td>
                    <span className={`sla${c.sla?.overdue ? " late" : ""}${c.sla?.due_today ? " today" : ""}`}>
                      {slaLabel(c.sla)}
                    </span>
                  </td>
                  <td>{c.assignee}</td>
                  <td>{when(c.submitted_at)}</td>
                  <td>
                    {c.run_id && (
                      <a className="mini" href={`/api/runs/${c.run_id}/audit.html`} target="_blank" rel="noreferrer" onClick={(e) => e.stopPropagation()}>
                        Auditas
                      </a>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      <aside className="desk-inbox" data-spot-target="inbox">
        <div className="kicker">Inžinieriaus pašto dėžutė</div>
        <h3>Patvirtinimai ir eskalacijos</h3>
        {inbox.length === 0 && <p className="empty">Tuščia — paleiskite eilę.</p>}
        {inbox.map((item) => (
          <InboxCard
            key={item.id}
            item={item}
            reason={reasons[item.id] || ""}
            setReason={(v) => setReasons((m) => ({ ...m, [item.id]: v }))}
            section3={edits[item.id] ?? item.section3 ?? ""}
            setSection3={(v) => setEdits((m) => ({ ...m, [item.id]: v }))}
            busy={busy}
            onApprove={onApprove}
            onOverride={onOverride}
            onEdit={onEdit}
            onOpen={onOpen}
          />
        ))}
      </aside>
    </div>
  );
}
