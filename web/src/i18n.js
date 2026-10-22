const DICT = {
  lt: {
    desk: "Vadovo eilė",
    gallery: "Istorinė galerija",
    intake: "Laisvas tekstas",
    present: "Pristatymas",
    lang: "EN",
    runAll: "Paleisti visas",
    reset: "Atstatyti demo",
    runFlow: "Paleisti eigą",
    replay: "Replay / be rakto",
    sqlite: "SQLite",
    waiting: "Laukia duomenų",
    approve: "Patvirtinti",
    supply: "Pateikti duomenis",
    whatif: "What-if",
    fill: "What-if užpildymas",
  },
  en: {
    desk: "Manager desk",
    gallery: "Historical gallery",
    intake: "Free text",
    present: "Present",
    lang: "LT",
    runAll: "Run all",
    reset: "Reset demo",
    runFlow: "Run graph",
    replay: "Replay / no key",
    sqlite: "SQLite",
    waiting: "Waiting for data",
    approve: "Approve",
    supply: "Supply data",
    whatif: "What-if",
    fill: "What-if fill",
  },
};

export function t(lang, key) {
  return (DICT[lang] || DICT.lt)[key] || key;
}
