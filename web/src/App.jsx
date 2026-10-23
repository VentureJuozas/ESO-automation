import { useEffect, useMemo, useRef, useState } from "react";
import { connectEvents, getJSON, postJSON } from "./api.js";
import { Icon } from "./icons.jsx";
import WorkflowCanvas from "./components/WorkflowCanvas.jsx";
import StepSheet from "./components/StepSheet.jsx";
import HowItWorks from "./components/HowItWorks.jsx";
import RuleSheet from "./components/RuleSheet.jsx";
import TimeSaved from "./components/viz/TimeSaved.jsx";
import IntakePanel from "./components/viz/IntakePanel.jsx";
import QueueDesk from "./components/QueueDesk.jsx";
import Gallery from "./components/Gallery.jsx";
import PresentGuide from "./components/PresentGuide.jsx";
import MissingPanel from "./components/MissingPanel.jsx";
import WhatIfBar from "./components/WhatIfBar.jsx";
import CustomerPortal from "./components/CustomerPortal.jsx";
import AdapterSheet from "./components/AdapterSheet.jsx";
import Analytics from "./components/Analytics.jsx";
import { t } from "./i18n.js";
import { scenarioStickies } from "./workflow.js";

const EMPTY_FORM = { kw: 11, phases: 3, lat: 54.55929, lon: 25.27955, text: "", pending_kw: 0, object_name: "Naujas buitinis objektas" };

export default function App() {
  const [view, setView] = useState("queue");
  const [scenarios, setScenarios] = useState([]);
  const [samples, setSamples] = useState([]);
  const [history, setHistory] = useState([]);
  const [architecture, setArchitecture] = useState(null);
  const [queue, setQueue] = useState(null);
  const [gallery, setGallery] = useState(null);
  const [scenarioId, setScenarioId] = useState("hero");
  const [activeQueueId, setActiveQueueId] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [run, setRun] = useState(null);
  const [events, setEvents] = useState([]);
  const [runningTool, setRunningTool] = useState(null);
  const [selected, setSelected] = useState("parse_request");
  const [section3, setSection3] = useState("");
  const [error, setError] = useState("");
  const [open, setOpen] = useState({ paraiskos: true, istorija: true, kita: true });
  const [inspectorOpen, setInspectorOpen] = useState(true);
  const [overrideReason, setOverrideReason] = useState("");
  const [batching, setBatching] = useState(false);
  const [galleryRunning, setGalleryRunning] = useState(false);
  const [inboxBusy, setInboxBusy] = useState(false);
  const [lang, setLang] = useState("lt");
  const [presentOn, setPresentOn] = useState(false);
  const [presentStep, setPresentStep] = useState(0);
  const [presentPack, setPresentPack] = useState(null);
  const [whatIf, setWhatIf] = useState({ kw: 11, phases: 3, distance_m: 66, pending_kw: 0 });
  const [whatIfBusy, setWhatIfBusy] = useState(false);
  const [presentPlaying, setPresentPlaying] = useState(false);
  const [adapters, setAdapters] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const stopRef = useRef(() => {});

  function refreshQueue() {
    return getJSON("/api/queue").then((q) => {
      setQueue(q);
      if (q.batching) setBatching(true);
      return q;
    }).catch(() => {});
  }

  useEffect(() => {
    getJSON("/api/scenarios").then(setScenarios).catch((e) => setError(String(e)));
    getJSON("/api/samples").then(setSamples).catch(() => {});
    getJSON("/api/architecture").then(setArchitecture).catch(() => {});
    getJSON("/api/runs").then(setHistory).catch(() => {});
    refreshQueue();
    getJSON("/api/gallery").then(setGallery).catch(() => {});
    getJSON("/api/adapters").then((a) => setAdapters(a.adapters || [])).catch(() => {});
    getJSON("/api/analytics").then(setAnalytics).catch(() => {});
    getJSON("/api/health").then((h) => {
      if (h.offline) document.body.dataset.offline = "1";
    }).catch(() => { document.body.dataset.offline = "1"; });
  }, []);

  useEffect(() => {
    if (!batching && !(queue?.hud?.running)) return undefined;
    const t = setInterval(() => {
      refreshQueue().then((q) => {
        if (q && q.hud.running === 0 && q.hud.new === 0) setBatching(false);
      });
    }, 550);
    return () => clearInterval(t);
  }, [batching, queue?.hud?.running]);

  const current = scenarios.find((s) => s.id === scenarioId);
  const snap = run;
  const failed = Boolean(snap?.failed) && !snap?.overridden;
  const skipped = snap?.skipped || [];
  const status = snap?.status || "idle";
  const value = snap?.value;
  const selectedEvent = useMemo(
    () => [...events].reverse().find((e) => e.tool === selected && e.type !== "start") || null,
    [events, selected]
  );

  useEffect(() => {
    const s3 = snap?.draft?.section3 || snap?.issued?.section3;
    if (s3 && !section3) setSection3(s3);
  }, [snap?.draft, snap?.issued]);

  function pickNode(id) {
    setSelected(id);
    setInspectorOpen(true);
  }

  function listen(created) {
    stopRef.current();
    const close = connectEvents(
      created.id,
      (ev) => {
        if (ev.type === "start") {
          setRunningTool(ev.tool);
          setSelected(ev.tool);
          setInspectorOpen(true);
        } else if (ev.type === "tool") {
          setEvents((xs) => [...xs, ev]);
          setRunningTool(null);
          setSelected(ev.tool);
        } else if (ev.type === "interrupt") {
          setEvents((xs) => [...xs, ev]);
          setRunningTool(null);
          setSelected(ev.tool || (ev.failed ? "escalate" : "engineer_approval"));
          setInspectorOpen(true);
          getJSON(`/api/runs/${created.id}`).then((r) => {
            setRun(r);
            if (r.events) setEvents(r.events);
          }).catch(() => {});
        } else if (ev.type === "status" || ev.type === "done") {
          if (ev.snapshot) {
            setRun(ev.snapshot);
            if (ev.snapshot.draft?.section3) setSection3(ev.snapshot.draft.section3);
            if (ev.snapshot.events) setEvents(ev.snapshot.events);
          } else {
            getJSON(`/api/runs/${created.id}`).then((r) => {
              setRun(r);
              if (r.events) setEvents(r.events);
            });
          }
          if (ev.type === "done") setRunningTool(null);
          getJSON("/api/runs").then(setHistory).catch(() => {});
          refreshQueue();
        } else if (ev.type === "error") {
          setError(ev.message || "Klaida");
          setRunningTool(null);
        }
      },
      () => {}
    );
    stopRef.current = close;
  }

  function pickScenario(s) {
    setScenarioId(s.id);
    setActiveQueueId(null);
    setView("case");
    setForm({ ...EMPTY_FORM, ...s.form });
    setRun(null);
    setEvents([]);
    setSection3("");
    setSelected("parse_request");
    setInspectorOpen(true);
    setError("");
    setOverrideReason("");
  }

  function openIntake() {
    setScenarioId("intake");
    setActiveQueueId(null);
    setView("intake");
    setForm({ ...EMPTY_FORM, text: samples[0]?.text || "" });
    setRun(null);
    setEvents([]);
    setSection3("");
    setSelected("parse_request");
    setInspectorOpen(true);
    setError("");
    setOverrideReason("");
  }

  async function start() {
    setError("");
    setEvents([]);
    setSection3("");
    setRunningTool("parse_request");
    setSelected("parse_request");
    setInspectorOpen(true);
    setView("case");
    stopRef.current();
    try {
      let created;
      if (activeQueueId) {
        created = await postJSON(`/api/queue/${activeQueueId}/start`, {});
      } else {
        const sid = scenarioId === "intake" ? "intake" : scenarioId;
        created = await postJSON("/api/runs", { scenario_id: sid, text: form.text, form });
      }
      setRun(created);
      listen(created);
      getJSON(`/api/runs/${created.id}`).then((r) => {
        if (r.status && r.status !== "queued" && r.status !== "running") {
          setRun(r);
          if (r.events) setEvents(r.events);
        }
      }).catch(() => {});
    } catch (e) {
      setError(String(e));
      setRunningTool(null);
    }
  }

  async function openCase(c) {
    setError("");
    setActiveQueueId(c.id);
    setScenarioId("queue");
    setForm({ ...EMPTY_FORM, ...(c.form || {}) });
    setSection3(c.section3 || "");
    setSelected("parse_request");
    setInspectorOpen(true);
    setOverrideReason("");
    setView("case");
    if (c.run_id) {
      const r = await getJSON(`/api/runs/${c.run_id}`);
      setRun(r);
      setEvents(r.events || []);
      if (r.draft?.section3) setSection3(r.draft.section3);
      if (r.status === "running") listen(r);
      return;
    }
    setRun(null);
    setEvents([]);
    setRunningTool("parse_request");
    try {
      const created = await postJSON(`/api/queue/${c.id}/start`, {});
      setRun(created);
      listen(created);
    } catch (e) {
      setError(String(e));
      setRunningTool(null);
    }
  }

  async function openRun(rid) {
    const r = await getJSON(`/api/runs/${rid}`);
    setRun(r);
    setEvents(r.events || []);
    setView("case");
    setSelected("parse_request");
    setInspectorOpen(true);
    setActiveQueueId(r.queue_id || null);
    if (r.draft?.section3) setSection3(r.draft.section3);
  }

  async function approve(fromInbox, extraSection3) {
    const rid = fromInbox?.run_id || run?.id;
    if (!rid) return;
    if (!fromInbox) {
      setRunningTool("issue_ts");
      setSelected("issue_ts");
    }
    const snap2 = await postJSON(`/api/runs/${rid}/resume`, {
      decision: "approve",
      section3: extraSection3 || section3,
    });
    if (!fromInbox || rid === run?.id) {
      setRun(snap2);
      setEvents(snap2.events || events);
      setRunningTool(null);
      setSelected("issue_ts");
    }
    getJSON("/api/runs").then(setHistory).catch(() => {});
    refreshQueue();
  }

  async function override(fromInbox, reason) {
    const rid = fromInbox?.run_id || run?.id;
    if (!rid) return;
    setError("");
    try {
      const snap2 = await postJSON(`/api/runs/${rid}/resume`, {
        decision: "override",
        override_reason: reason || overrideReason,
      });
      if (!fromInbox || rid === run?.id) {
        setRun(snap2);
        setEvents(snap2.events || events);
        setSelected("engineer_approval");
        if (snap2.draft?.section3) setSection3(snap2.draft.section3);
      }
      refreshQueue();
    } catch (e) {
      setError(String(e.message || e));
    }
  }

  async function saveEdit(fromInbox, extraSection3) {
    const rid = fromInbox?.run_id || run?.id;
    if (!rid) return;
    const snap2 = await postJSON(`/api/runs/${rid}/resume`, { decision: "edit", section3: extraSection3 || section3 });
    if (!fromInbox || rid === run?.id) {
      setRun(snap2);
      setEvents(snap2.events || events);
    }
    refreshQueue();
  }

  async function rerun(fromTool) {
    if (!run?.id) return;
    setRunningTool(fromTool);
    const snap2 = await postJSON(`/api/runs/${run.id}/rerun`, {
      from_tool: fromTool,
      overrides: { pending_kw: form.pending_kw, kw: form.kw, phases: form.phases, lat: form.lat, lon: form.lon },
    });
    setRun(snap2);
    setEvents(snap2.events || []);
    setRunningTool(null);
    refreshQueue();
  }

  async function batchAll() {
    setBatching(true);
    await postJSON("/api/queue/batch", {});
    refreshQueue();
  }

  async function resetQueue() {
    const q = await postJSON("/api/demo/reset", {});
    setQueue(q);
    setBatching(false);
    setRun(null);
    setEvents([]);
    setHistory([]);
    setGallery((g) => ({ ...(g || {}), last: null }));
  }

  async function runGallery() {
    setGalleryRunning(true);
    try {
      const last = await postJSON("/api/gallery/run", {});
      setGallery((g) => ({ ...(g || {}), last }));
    } finally {
      setGalleryRunning(false);
    }
  }

  async function runGalleryWhatIf() {
    setGalleryRunning(true);
    try {
      const whatif = await postJSON("/api/gallery/whatif", {});
      setGallery((g) => ({ ...(g || {}), whatif }));
    } finally {
      setGalleryRunning(false);
    }
  }

  function applyBeat(pack, idx) {
    const beat = (pack?.beats || [])[idx];
    if (!beat) return;
    setView(beat.view);
    if (beat.apply === "queue_after") setQueue(pack.queue_after);
    if (beat.apply === "hero" && pack.hero) {
      setRun(pack.hero);
      setEvents(pack.hero.events || []);
      setScenarioId("hero");
    }
    if (beat.apply === "fail" && pack.fail) {
      setRun(pack.fail);
      setEvents(pack.fail.events || []);
      setScenarioId("fail_capacity");
    }
    if (beat.apply === "gallery") setGallery((g) => ({ ...(g || {}), last: pack.gallery }));
    if (beat.view === "analytics" && pack.analytics) setAnalytics(pack.analytics);
    if (beat.select) {
      setSelected(beat.select);
      setInspectorOpen(true);
    }
    document.body.dataset.spot = beat.spot || "";
  }

  async function startPresent() {
    const pack = presentPack || await getJSON("/api/present");
    setPresentPack(pack);
    setPresentOn(true);
    setPresentStep(0);
    setQueue(pack.queue_before);
    applyBeat(pack, 0);
    setPresentPlaying(true);
  }

  function goPresent(delta) {
    if (!presentPack) return;
    const next = Math.max(0, Math.min((presentPack.beats || []).length - 1, presentStep + delta));
    setPresentStep(next);
    applyBeat(presentPack, next);
  }

  useEffect(() => {
    if (!presentOn) return undefined;
    const onKey = (e) => {
      if (e.key === "ArrowRight") { e.preventDefault(); goPresent(1); }
      if (e.key === "ArrowLeft") { e.preventDefault(); goPresent(-1); }
      if (e.key === " ") { e.preventDefault(); setPresentPlaying((p) => !p); }
      if (e.key === "Escape") { setPresentOn(false); setPresentPlaying(false); document.body.dataset.spot = ""; }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [presentOn, presentPack, presentStep]);

  function restartPresent() {
    if (!presentPack) return;
    setPresentStep(0);
    applyBeat(presentPack, 0);
    setPresentPlaying(true);
  }

  useEffect(() => {
    if (!presentOn || !presentPlaying || !presentPack) return undefined;
    const beats = presentPack.beats || [];
    if (presentStep >= beats.length - 1) {
      setPresentPlaying(false);
      return undefined;
    }
    const ms = beats[presentStep]?.dwell_ms || presentPack.autoplay_ms || 20000;
    const t = setTimeout(() => goPresent(1), ms);
    return () => clearTimeout(t);
  }, [presentOn, presentPlaying, presentPack, presentStep]);

  useEffect(() => {
    if (view !== "split" && view !== "customer") return undefined;
    const t = setInterval(() => refreshQueue(), 1400);
    return () => clearInterval(t);
  }, [view]);

  async function liveWhatIf(vals) {
    setWhatIfBusy(true);
    try {
      const snap = await postJSON("/api/whatif", vals);
      setRun(snap);
      setEvents(snap.events || []);
      setView("case");
      setSelected(snap.failed ? "escalate" : "check_capacity");
      setInspectorOpen(true);
    } finally {
      setWhatIfBusy(false);
    }
  }

  async function supplyMissing() {
    if (!run?.id) return;
    setInboxBusy(true);
    try {
      const snap = await postJSON(`/api/runs/${run.id}/supply`, {
        lat: 54.55929,
        lon: 25.27955,
        kw: 11,
        phases: 3,
        text: "Užpildyta: 11 kW, 3F, 54,55929, 25,27955.",
      });
      setRun(snap);
      setEvents(snap.events || []);
      setSelected(snap.failed ? "escalate" : "select_solution");
      refreshQueue();
    } finally {
      setInboxBusy(false);
    }
  }

  async function inboxApprove(item, s3) {
    setInboxBusy(true);
    try { await approve(item, s3); } finally { setInboxBusy(false); }
  }
  async function inboxOverride(item, reason) {
    setInboxBusy(true);
    try { await override(item, reason); } finally { setInboxBusy(false); }
  }
  async function inboxEdit(item, s3) {
    setInboxBusy(true);
    try { await saveEdit(item, s3); } finally { setInboxBusy(false); }
  }

  const waiting = status === "awaiting_approval" || status === "escalated";
  const llmMode = architecture?.llm_mode || snap?.llm_mode || "offline";
  const hud = runningTool
    ? { cls: "run", text: `Vykdoma · ${runningTool}` }
    : status === "waiting_data"
      ? { cls: "wait", text: "Sustabdyta · request_missing_data" }
    : status === "escalated"
      ? { cls: "bad", text: "Šaka · check_capacity → escalate" }
      : waiting
        ? { cls: "wait", text: "Sustabdyta · inžinieriaus vartai" }
        : status === "issued"
          ? { cls: "ok", text: "Išduota · TS paruošta spausdinti" }
          : { cls: "", text: "Drobė · spustelėkite mazgą" };
  const issuedDoc = snap?.issued?.document || snap?.draft?.document;
  const crumb = view === "how"
    ? "Kaip tai veikia"
    : view === "rules"
      ? "Taisyklės"
      : view === "intake"
        ? "Nauja paraiška"
        : view === "queue"
          ? "Vadovo eilė"
          : view === "gallery"
            ? "Istorinė galerija"
          : view === "customer"
            ? "Klientų maketas"
          : view === "split"
            ? "Klientas ir stalas"
          : view === "integrations"
            ? "Integracijos"
          : view === "analytics"
            ? "Analitika"
            : <>Paraiškos <span>/</span> {current?.title || (scenarioId === "intake" ? "Nauja paraiška" : scenarioId === "queue" ? (run?.title || "Eilės byla") : "Naujas vartotojas, TP 12-608")}</>;

  return (
    <div className="app">
      <aside className="side">
        <div className="brand">
          <span className="mark"><Icon name="branch" size={16} /></span>
          <div><b>Sąlygos</b><small>Vadovo eilė · n8n drobė</small></div>
        </div>
        <nav className="nav">
          <button className={`item intake-nav${view === "queue" ? " on" : ""}`} type="button" data-testid="nav-desk" onClick={() => { setView("queue"); refreshQueue(); }}>
            <b>{t(lang, "desk")}</b>
            <small>{queue?.hud?.inbox_depth ?? 0} laukia · {queue?.hud?.new ?? 0} naujos</small>
          </button>
          <button className={`item${view === "gallery" ? " on" : ""}`} type="button" onClick={() => { setView("gallery"); getJSON("/api/gallery").then(setGallery).catch(() => {}); }}>
            <b>Istorinė galerija</b>
            <small>Back-test vs išduotos TS</small>
          </button>
          <button className={`item${view === "analytics" ? " on" : ""}`} type="button" data-testid="nav-analytics" onClick={() => { setView("analytics"); getJSON("/api/analytics").then(setAnalytics).catch(() => {}); }}>
            <b>{t(lang, "analytics")}</b>
            <small>Sintetinis mėnuo · prielaida</small>
          </button>
          <button className={`item intake-nav${view === "intake" || scenarioId === "intake" ? " on" : ""}`} type="button" onClick={openIntake}>
            <b>Nauja paraiška</b>
            <small>Laiškas, forma, žemėlapis</small>
          </button>
          <div className={`sec${open.paraiskos ? " open" : ""}`}>
            <button className={`sec-btn${open.paraiskos ? " open" : ""}`} type="button" onClick={() => setOpen((o) => ({ ...o, paraiskos: !o.paraiskos }))}>
              Scenarijai <span className="count">{scenarios.length}</span>
            </button>
            {open.paraiskos && scenarios.map((s) => (
              <button key={s.id} className={`item${view === "case" && scenarioId === s.id ? " on" : ""}`} type="button" data-testid={`scenario-${s.id}`} onClick={() => pickScenario(s)}>
                <b>{s.title}</b>
                <small>{s.subtitle}</small>
              </button>
            ))}
          </div>
          <div className={`sec${open.istorija ? " open" : ""}`}>
            <button className={`sec-btn${open.istorija ? " open" : ""}`} type="button" onClick={() => setOpen((o) => ({ ...o, istorija: !o.istorija }))}>
              Istorija <span className="count">{history.length}</span>
            </button>
            {open.istorija && history.slice(0, 6).map((h) => (
              <button key={h.id} className="item" type="button" onClick={() => openRun(h.id)}>
                <b>{(h.title || h.id).toString().slice(0, 22)} · {h.solution || "—"} {h.kw} kW</b>
                <small>{h.status}</small>
              </button>
            ))}
            {open.istorija && history.length > 6 && (
              <p className="side-note" style={{ padding: "4px 10px" }}>+{history.length - 6} senesnės</p>
            )}
          </div>
          <div className={`sec${open.kita ? " open" : ""}`}>
            <button className={`sec-btn${open.kita ? " open" : ""}`} type="button" onClick={() => setOpen((o) => ({ ...o, kita: !o.kita }))}>
              Kita
            </button>
            {open.kita && (
              <>
                <button className={`item${view === "how" ? " on" : ""}`} type="button" onClick={() => { setView("how"); setSelected("ui"); setInspectorOpen(true); }}>
                  <b>Kaip tai veikia</b><small>Architektūros drobė</small>
                </button>
                <button className={`item${view === "rules" ? " on" : ""}`} type="button" onClick={() => { setView("rules"); setSelected("parse_request"); setInspectorOpen(true); }}>
                  <b>Taisyklės</b><small>Mazgai ir ESO šaltiniai</small>
                </button>
                <button className={`item${view === "integrations" ? " on" : ""}`} type="button" onClick={() => { setView("integrations"); setSelected("gis"); setInspectorOpen(true); }}>
                  <b>Integracijos</b><small>Adapteriai mock / stub</small>
                </button>
                <button className={`item${view === "customer" ? " on" : ""}`} type="button" data-testid="nav-customer" onClick={() => setView("customer")}>
                  <b>Klientų maketas</b><small>Paraiška ir būsena</small>
                </button>
                <button className={`item${view === "split" ? " on" : ""}`} type="button" data-testid="nav-split" onClick={() => { setView("split"); refreshQueue(); }}>
                  <b>Klientas ir stalas</b><small>Split · minutes, ne dienos</small>
                </button>
                <a className="item" href="/api/onepager.html" target="_blank" rel="noreferrer">
                  <b>Vieno lapo santrauka</b><small>A4 palikti žiuriui</small>
                </a>
              </>
            )}
          </div>
        </nav>
        <p className="side-note">Skaičiai iš TP 12-608. Kainos — orientyras iš 26-E-37934. LLM: {llmMode}. Be asmens duomenų.</p>
      </aside>

      <section className="main">
        <header className="top">
          <div className="crumb">{crumb}</div>
          <div className="top-actions">
            <span className="badge">{llmMode === "offline" ? t(lang, "replay") : `LLM ${llmMode}`}</span>
            <span className="badge">{t(lang, "sqlite")}</span>
            <button className={`go${presentOn ? " on" : ""}`} type="button" data-testid="start-present" onClick={() => (presentOn ? (setPresentOn(false), document.body.dataset.spot = "") : startPresent())}>{t(lang, "present")}</button>
            <button className="go" type="button" onClick={() => setLang((l) => (l === "lt" ? "en" : "lt"))}>{t(lang, "lang")}</button>
            {(view === "case" || view === "intake") && (
              <>
                {status === "issued" && run?.id && (
                  <a className="go" href={`/api/runs/${run.id}/ts.html`} target="_blank" rel="noreferrer">Atidaryti TS</a>
                )}
                {run?.id && (
                  <a className="go" href={`/api/runs/${run.id}/audit.html`} target="_blank" rel="noreferrer">Auditas</a>
                )}
                <button className="exec" type="button" data-testid="run-flow" onClick={start} disabled={status === "running" || Boolean(runningTool)}>{t(lang, "runFlow")}</button>
              </>
            )}
            {view === "queue" && (
              <button className="exec" type="button" onClick={batchAll} disabled={batching || (queue?.hud?.new || 0) === 0}>{t(lang, "runAll")}</button>
            )}
          </div>
        </header>

        {view === "case" && (
          <div data-spot-target="time"><TimeSaved comparison={value?.comparison} /></div>
        )}
        {view === "case" && (
          <WhatIfBar values={whatIf} onChange={setWhatIf} onLive={liveWhatIf} busy={whatIfBusy} />
        )}

        <div className="canvas" style={{ flex: 1, minHeight: 0, display: "flex", flexDirection: "column" }}>
          {view === "case" && <div className={`exec-hud ${hud.cls}`}>{hud.text}</div>}
          <div className="workspace">
            <div className="wf-wrap" data-spot-target="canvas">
              {view === "split" && (
                <div className="split-view" data-spot-target="split">
                  <CustomerPortal compact onSubmitted={() => refreshQueue()} />
                  <QueueDesk
                    queue={queue}
                    batching={batching}
                    busy={inboxBusy}
                    onBatch={batchAll}
                    onReset={resetQueue}
                    onOpen={openCase}
                    onApprove={inboxApprove}
                    onOverride={inboxOverride}
                    onEdit={inboxEdit}
                    lang={lang}
                  />
                </div>
              )}
              {view === "customer" && <CustomerPortal onSubmitted={() => refreshQueue()} />}
              {view === "queue" && (
                <QueueDesk
                  queue={queue}
                  batching={batching}
                  busy={inboxBusy}
                  onBatch={batchAll}
                  onReset={resetQueue}
                  onOpen={openCase}
                  onApprove={inboxApprove}
                  onOverride={inboxOverride}
                  onEdit={inboxEdit}
                  lang={lang}
                />
              )}
              {view === "gallery" && (
                <div data-spot-target="taxonomy">
                  <Gallery gallery={gallery} running={galleryRunning} onRun={runGallery} onWhatIf={runGalleryWhatIf} onOpenRun={openRun} />
                </div>
              )}
              {view === "analytics" && <Analytics data={analytics} />}
              {view === "intake" && (
                <IntakePanel form={form} setForm={setForm} samples={samples} onStart={start} running={Boolean(runningTool)} />
              )}
              {view === "case" && (
                <WorkflowCanvas
                  events={events}
                  runningTool={runningTool}
                  failed={failed}
                  skipped={skipped}
                  selectedId={selected}
                  onSelect={pickNode}
                  stickies={scenarioStickies(current || (scenarioId === "intake" || scenarioId === "queue" ? { title: run?.title || "Eilės byla", subtitle: run?.assignee || "Vadovo eilė", notes: "Sintetinė / redaguota paraiška. Be asmens duomenų." } : null))}
                  inspectorOpen={inspectorOpen}
                  followId={runningTool}
                />
              )}
              {view === "integrations" && (
                <WorkflowCanvas
                  mode="adapters"
                  selectedId={selected}
                  onSelect={pickNode}
                  inspectorOpen={inspectorOpen}
                  architecture={architecture}
                />
              )}
              {view === "how" && (
                <WorkflowCanvas
                  mode="arch"
                  selectedId={selected}
                  onSelect={pickNode}
                  architecture={architecture}
                  inspectorOpen={inspectorOpen}
                />
              )}
              {view === "rules" && (
                <WorkflowCanvas
                  events={[]}
                  selectedId={selected}
                  onSelect={pickNode}
                  inspectorOpen={inspectorOpen}
                  stickies={[{ id: "rules-note", x: 36, y: 516, title: "Taisyklės prie mazgų", body: "Spustelėkite mazgą — dešinėje n8n skydelyje ESO šaltinis, įvestis ir ką tikrinti inžinieriui." }]}
                />
              )}
            </div>
            {view !== "queue" && view !== "gallery" && view !== "customer" && view !== "split" && view !== "analytics" && (inspectorOpen ? (
              <div className="inspector">
                {view === "case" && (
                  <StepSheet
                    toolId={selected}
                    event={selectedEvent}
                    running={runningTool === selected}
                    error={error}
                    catalog={architecture}
                    onRerun={run?.id ? rerun : null}
                    section3={section3}
                    setSection3={setSection3}
                    canEdit={waiting && !failed}
                    form={form}
                    setForm={setForm}
                    onClose={() => setInspectorOpen(false)}
                    runId={run?.id}
                    document={issuedDoc}
                    audit={snap?.audit}
                    skipped={skipped.includes(selected)}
                    emptyHint="Paleiskite eigą. Mazgai ant drobės užsidegs paeiliui kaip n8n."
                  />
                )}
                {view === "intake" && (
                  <section className="sheet">
                    <header className="sheet-head">
                      <div>
                        <div className="sheet-kicker">parse_request</div>
                        <h2>Gyvas skaitymas</h2>
                      </div>
                      <button type="button" className="insp-x" onClick={() => setInspectorOpen(false)} aria-label="Uždaryti">×</button>
                    </header>
                    <div className="sheet-body">
                      <p className="hint">Įklijuokite lietuvišką laišką arba pasirinkite pavyzdį. Parseris išskiria kW, fazes ir koordinates su pasitikėjimu. Be rakto — deterministinis replay.</p>
                    </div>
                  </section>
                )}
                {view === "how" && (
                  <section className="sheet">
                    <header className="sheet-head">
                      <div>
                        <div className="sheet-kicker">{selected}</div>
                        <h2>{(architecture?.layers || []).find((l) => l.id === selected)?.title || "Kaip tai veikia"}</h2>
                      </div>
                      <button type="button" className="insp-x" onClick={() => setInspectorOpen(false)} aria-label="Uždaryti">×</button>
                    </header>
                    <div className="sheet-body">
                      <HowItWorks architecture={architecture} layerId={selected} />
                    </div>
                  </section>
                )}
                {view === "integrations" && (
                  <section className="sheet">
                    <header className="sheet-head">
                      <div>
                        <div className="sheet-kicker">{selected}</div>
                        <h2>{(adapters.find((a) => a.id === selected) || {}).title || selected}</h2>
                      </div>
                      <button type="button" className="insp-x" onClick={() => setInspectorOpen(false)} aria-label="Uždaryti">×</button>
                    </header>
                    <div className="sheet-body">
                      <AdapterSheet adapter={adapters.find((a) => a.id === selected) || (architecture?.adapters || []).find((a) => a.id === selected)} />
                    </div>
                  </section>
                )}
                {view === "rules" && (
                  <section className="sheet">
                    <header className="sheet-head">
                      <div>
                        <div className="sheet-kicker">{selected}</div>
                        <h2>{(architecture?.tools || []).find((t) => t.id === selected)?.title_lt || selected}</h2>
                      </div>
                      <button type="button" className="insp-x" onClick={() => setInspectorOpen(false)} aria-label="Uždaryti">×</button>
                    </header>
                    <div className="sheet-body">
                      <RuleSheet toolId={selected} catalog={architecture} />
                    </div>
                  </section>
                )}
              </div>
            ) : (
              <button type="button" className="insp-reopen" onClick={() => setInspectorOpen(true)}>Mazgas</button>
            ))}
          </div>
          {view === "case" && status === "waiting_data" && (
            <div className="dock">
              <MissingPanel missing={snap?.missing} onSupply={supplyMissing} busy={inboxBusy} />
            </div>
          )}
          {view === "case" && status === "escalated" && (
            <div className="dock bad" data-testid="escalate-dock">
              <div style={{ flex: 1 }}>
                <b>Patikra nepraėjo — perduota inžinieriui</b>
                <div style={{ color: "var(--muted)", fontSize: 12, marginBottom: 8 }}>
                  {snap?.escalate?.numbers
                    ? `${snap.escalate.numbers.after_kw} kW vs ${snap.escalate.numbers.limit_80_kw} kW (80 %). Override reikalauja priežasties ir rašomas į auditą.`
                    : "Sąlygos neišduodamos be inžinieriaus override."}
                </div>
                <textarea
                  className="edit"
                  style={{ minHeight: 64 }}
                  placeholder="Override priežastis (mažiausiai 8 simboliai)…"
                  value={overrideReason}
                  onChange={(e) => setOverrideReason(e.target.value)}
                />
              </div>
              {run?.id && (
                <a className="go" data-testid="brief-link" href={`/api/runs/${run.id}/brief.html`} target="_blank" rel="noreferrer">Stiprinimo paketas</a>
              )}
              <button className="ink" type="button" onClick={() => override()} disabled={overrideReason.trim().length < 8}>
                Inžinieriaus override
              </button>
            </div>
          )}
          {view === "case" && status === "awaiting_approval" && (
            <div className="dock">
              <div>
                <b>{snap?.overridden ? "Override įrašytas — peržiūrėkite §3" : "Laukia inžinieriaus patvirtinimo"}</b>
                <div style={{ color: "var(--muted)", fontSize: 12 }}>
                  {snap?.overridden ? `Priežastis: ${snap.audit?.[0]?.reason}` : "Peržiūrėkite §3 dešiniame skydelyje, tada išduokite."}
                </div>
              </div>
              <div style={{ display: "flex", gap: 8 }}>
                {run?.id && <a className="go" href={`/api/runs/${run.id}/audit.html`} target="_blank" rel="noreferrer">Auditas</a>}
                <button className="go" type="button" onClick={() => saveEdit()}>Įrašyti §3 pataisą</button>
                <button className="exec" type="button" onClick={() => approve()}>Patvirtinti ir išduoti</button>
              </div>
            </div>
          )}
        </div>
      </section>
      {presentOn && (
        <PresentGuide
          pack={presentPack}
          step={presentStep}
          lang={lang}
          playing={presentPlaying}
          onPrev={() => goPresent(-1)}
          onNext={() => goPresent(1)}
          onClose={() => { setPresentOn(false); setPresentPlaying(false); document.body.dataset.spot = ""; }}
          onLang={() => setLang((l) => (l === "lt" ? "en" : "lt"))}
          onToggle={() => setPresentPlaying((p) => !p)}
          onRestart={restartPresent}
        />
      )}
    </div>
  );
}
