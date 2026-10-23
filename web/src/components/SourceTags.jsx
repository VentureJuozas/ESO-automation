import { sourceLabel } from "../steps.js";

export default function SourceTags({ tags = [] }) {
  const uniq = [...new Set(tags.filter(Boolean))];
  if (!uniq.length) return null;
  return (
    <span className="badges">
      {uniq.map((t) => (
        <span key={t} className={`tag ${t}`} title={sourceLabel(t)}>
          {sourceLabel(t)}
        </span>
      ))}
    </span>
  );
}
