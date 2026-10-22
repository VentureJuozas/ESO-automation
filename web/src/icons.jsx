export const ICONS = {
  doc: "M7 3.5h7l4.5 4.5V20a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4.5a1 1 0 0 1 1-1z M14 3.5V8h4.5",
  pin: "M12 21s7-6.1 7-11a7 7 0 1 0-14 0c0 4.9 7 11 7 11z M12 10a2.2 2.2 0 1 0 0.001 0",
  grid: "M4 4h6.5v6.5H4z M13.5 4H20v6.5h-6.5z M4 13.5H10.5V20H4z M13.5 13.5H20V20h-6.5z",
  branch: "M6 6a2 2 0 1 0 0.001 0 M6 18a2 2 0 1 0 0.001 0 M18 12a2 2 0 1 0 0.001 0 M8 6h4a4 4 0 0 1 4 4 M8 18h4a4 4 0 0 0 4-4",
  send: "M4 12l16-7-6 16-2.5-6.5L4 12z",
  check: "M5 12.5l5 5L19 7",
  bang: "M12 7v7M12 17.5v.5",
};

export function Icon({ name, size = 24 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <path d={ICONS[name] || ICONS.branch} />
    </svg>
  );
}

export function Check() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round">
      <path d={ICONS.check} />
    </svg>
  );
}

export function Bang() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round">
      <path d={ICONS.bang} />
    </svg>
  );
}
