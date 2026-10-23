/** Per-step data source, rule quote and result copy. Docs hold provenance. */

export const BRIEFINGS = {
  parse_request: {
    source: {
      system: "CRM application",
      dataset: "Household connection request · TP 12-608",
      fields: "kW, phases, coordinates, object name",
      timestamp: "2026-02-06 19:15 UTC",
    },
    rule: {
      quote: "Household connections ≤ 250 kW are decided within 3 working days.",
      ref: "KNOWLEDGE.md §5 · ESO connection-conditions process",
    },
  },
  locate_connection_point: {
    source: {
      system: "GIS topology",
      dataset: "Objects_network_power · TP 12-608 poles and cabinets",
      fields: "lat, lon, feeder, element id, distance",
      timestamp: "as of the 12-608 extract",
    },
    rule: {
      quote: "Connect at the nearest network element on the supplying feeder.",
      ref: "SCOPE.md · network selection",
    },
  },
  render_map: {
    source: {
      system: "GIS topology",
      dataset: "TP 12-608 geometry",
      fields: "substation, feeder, poles, request pin",
      timestamp: "as of the 12-608 extract",
    },
    rule: {
      quote: "The issued TS includes a GIS annex of the connection point.",
      ref: "Technical requirements · GIS annex",
    },
  },
  check_capacity: {
    source: {
      system: "Power BI / SCADA load data",
      dataset: "pastotes_load_kas15min · TP 12-608",
      fields: "peak_kw, nominal_kVA, 80/90 % limits",
      timestamp: "2026-02-06 19:15 UTC",
    },
    rule: {
      quote: "Transformer loading after connection must stay ≤ 80 % of nameplate (320 kW on 400 kVA). 90 % is the hard stop.",
      ref: "SCOPE 1d · Substations_info",
    },
  },
  check_voltage_drop: {
    source: {
      system: "GIS topology + line-load calculator",
      dataset: "Skaičiuoklė nuo 2018 m. · L-200 4A-50",
      fields: "conductor, length, permitted kW, houses",
      timestamp: "calculator tables in src/line_load.py",
    },
    rule: {
      quote: "Supply voltage must remain ≥ 207 V (230 V − 10 %, LST EN 50160).",
      ref: "LST EN 50160 · KNOWLEDGE voltage quality",
    },
  },
  check_reliability: {
    source: {
      system: "GIS topology",
      dataset: "TP 12-608 transformer count and feeder type",
      fields: "transformer_count, radial flag, solution id",
      timestamp: "as of the 12-608 extract",
    },
    rule: {
      quote: "N-1 at 0.4 kV equals the single transformer nameplate. A pole KAS does not interrupt neighbours.",
      ref: "SCOPE 3a–3c",
    },
  },
  check_future: {
    source: {
      system: "Power BI / SCADA load data",
      dataset: "Reserved capacity on TP 12-608",
      fields: "peak_kw, reserved_kw, headroom to 80 %",
      timestamp: "2026-02-06 19:15 UTC",
    },
    rule: {
      quote: "Leave headroom to the 80 % transformer limit after this connection and any reserved load.",
      ref: "SCOPE 4a–4c",
    },
  },
  select_solution: {
    source: {
      system: "GIS topology",
      dataset: "Feeder type and nearest element",
      fields: "overhead/cable, cabinet_at_plot, distance",
      timestamp: "as of the 12-608 extract",
    },
    rule: {
      quote: "A = existing cabinet on the plot. B = new pole KAS on an overhead feeder. C = cable cut-in.",
      ref: "SCOPE.md solution table",
    },
  },
  size_breaker: {
    source: {
      system: "Pricing catalogue / rules",
      dataset: "Srovės transf. įvertinimas",
      fields: "permitted kW, phases → C-characteristic A",
      timestamp: "KNOWLEDGE.md §15",
    },
    rule: {
      quote: "3-phase 11 kW maps to C 20 A.",
      ref: "KNOWLEDGE.md §15 breaker table",
    },
  },
  estimate_cost: {
    source: {
      system: "Pricing catalogue",
      dataset: "Connection unit rates (26-E-37934 sheet)",
      fields: "breaker install, KS/KAS, labour 11.78 %, VAT 21 %",
      timestamp: "rate sheet dated with the 26-E-37934 file",
    },
    rule: {
      quote: "Capitalised labour = 11.78 % of materials. VAT = 21 %.",
      ref: "cost_estimate_26-E-37934.md",
    },
  },
  draft_ts_section3: {
    source: {
      system: "TS registry",
      dataset: "Issued 0.4 kV household conditions",
      fields: "solution, breaker, feeder, pole, §3 actions",
      timestamp: "this run",
    },
    rule: {
      quote: "§3 lists the operator actions. Numbers come from the tools, not the language model.",
      ref: "ESO connection-conditions content",
    },
  },
  engineer_approval: {
    source: {
      system: "TS registry · audit log",
      dataset: "This run, SHA-256 of every tool I/O",
      fields: "decision, §3 text, engineer id",
      timestamp: "at the gate",
    },
    rule: {
      quote: "An engineer signs, edits §3, or records an override before issue.",
      ref: "Process gate",
    },
  },
  issue_ts: {
    source: {
      system: "TS registry",
      dataset: "Issued conditions 26-E-DEMO-…",
      fields: "ts_number, dates, 2-page document + GIS annex",
      timestamp: "on approval",
    },
    rule: {
      quote: "The issued document is the two-page Lithuanian Prijungimo sąlygos, with a GIS annex.",
      ref: "TS registry",
    },
  },
};
