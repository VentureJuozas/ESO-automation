import { GROUPS, groupOf } from "../steps.js";
import { Bang, Check, Icon } from "../icons.jsx";

function status(group, events, runningTool, failed) {
  const evs = events.filter((e) => e.type === "tool" || e.type === "interrupt");
  const mine = group.tools.map((t) => evs.find((e) => e.tool === t)).filter(Boolean);
  if (group.tools.includes(runningTool)) return ["Vykdoma", "run"];
  if (mine.some((e) => e.outputs?.escalate || e.type === "interrupt" && failed)) {
    if (group.id === "isdavimas" && events.some((e) => e.type === "interrupt")) return ["Laukia", "stop"];
    if (mine.some((e) => e.outputs?.escalate)) return ["Nepraeina", "stop"];
  }
  const doneTools = group.tools.filter((t) => ["engineer_approval", "issue_ts", "escalate"].includes(t) ? false : true);
  const allDone = doneTools.every((t) => evs.some((e) => e.tool === t));
  if (allDone && mine.length) return ["Atlikta", "done"];
  if (mine.length) return ["Dalinai", "partial"];
  if (group.id === "isdavimas" && events.some((e) => e.type === "interrupt")) return ["Laukia", "stop"];
  return ["Laukia", "wait"];
}

export default function Flow({ events, runningTool, failed, selectedGroup, onSelect }) {
  return (
    <div className="flow">
      {GROUPS.map((g, i) => {
        const [word, cls] = status(g, events, runningTool, failed);
        return (
          <span key={g.id} style={{ display: "flex", alignItems: "flex-start" }}>
            <button
              className={`node${selectedGroup === g.id ? " on" : ""}`}
              style={{ "--hue": g.hue }}
              type="button"
              onClick={() => onSelect(g.id, g.tools[0])}
            >
              <span className={`box ${cls}`}>
                <Icon name={g.icon} />
                {cls === "done" && <span className="pip done"><Check /></span>}
                {cls === "stop" && <span className="pip stop"><Bang /></span>}
              </span>
              <span className="cap">{g.title}</span>
              <span className={`sub ${cls}`}>{word}</span>
            </button>
            {i < GROUPS.length - 1 && <div className={`wire${cls === "done" ? " done" : ""}`} />}
          </span>
        );
      })}
    </div>
  );
}

export { groupOf };
