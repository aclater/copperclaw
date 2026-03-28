/**
 * OPERATION COPPERCLAW — Frontend Display Map
 * ============================================
 * COSMIC INDIGO // REL KESTREL COALITION
 * EXERCISE — EXERCISE — EXERCISE
 *
 * Maps generic schema enum values to human-readable platform and
 * munition labels for the briefing console.
 *
 * IMPORTANT: This file lives in the React frontend ONLY.
 * It is NEVER sent to the backend, injected into agent prompts,
 * or included in any Kafka message payload.
 * Agents operate exclusively on the generic enum values.
 *
 * Usage:
 *   import { DISPLAY_MAP } from './displayMap';
 *   const label = DISPLAY_MAP.ExecutionMethod['PRECISION_AIR'];
 *   // → "GBU-38 JDAM / GBU-12 Paveway II"
 */

export const DISPLAY_MAP = {

  ExecutionMethod: {
    PRECISION_STRIKE:        "Precision Air Strike (PGM)",
    PRECISION_AIR:           "GBU-38 JDAM / GBU-12 Paveway II",
    LOW_COLLATERAL_AIR:      "GBU-39B Small Diameter Bomb",
    ATTACK_AVIATION:         "AH-64E Apache (Hellfire / 30mm)",
    SOF_DIRECT_ACTION:       "KSOF Ground Assault / MH-60M DAP",
    CAPTURE_OPERATION:       "KSOF Capture Operation",
    ARTILLERY_FIRE:          "M109A7 Paladin / AS-90 (155mm)",
    NON_KINETIC_EW:          "Electronic Warfare Effect",
    NON_KINETIC_INFLUENCE:   "Influence Operations",
    NON_KINETIC_CYBER:       "Cyber Effect",
    SURVEILLANCE_ONLY:       "ISR — No Kinetic Effect",
  },

  MunitionCategory: {
    LASER_GUIDED_BOMB:       "GBU-12 Paveway II (Laser-guided)",
    GPS_GUIDED_BOMB:         "GBU-38 JDAM (GPS/INS, all-weather)",
    SMALL_DIAMETER_BOMB:     "GBU-39B SDB (Low collateral, RTL-appropriate)",
    HELLFIRE:                "AGM-114 Hellfire (Apache)",
    CANNON_30MM:             "M230 30mm Chain Gun (Apache)",
    ARTILLERY_155MM:         "155mm (M109A7 Paladin / AS-90)",
    NON_KINETIC:             "Non-kinetic effect (EW / Cyber)",
    NONE:                    "No munition — observation / capture",
  },

  PlatformType: {
    FIXED_WING_ISR:          "MC-12W Liberty (SAR/EO)",
    SIGINT_PLATFORM:         "RC-135V/W Rivet Joint",
    ROTARY_QRF:              "UH-60M Black Hawk",
    SOF_AVIATION:            "MH-60M DAP",
    ATTACK_ROTARY:           "AH-64E Apache",
    ARTILLERY_PLATFORM:      "M109A7 Paladin / AS-90",
    HUMINT_SOURCE:           "KITE-7 (HUMINT — PRENN network)",
    GROUND_SIGINT:           "SHADOW COMMS (National SIGINT)",
    JTAC:                    "JTAC Team",
  },

  ISRAsset: {
    RAVEN_1:                 "MC-12W Liberty — RAVEN-1 (SAR/EO, 18hr endurance, on VICTOR-5-KILO)",
    RAVEN_2:                 "MC-12W Liberty — RAVEN-2 (reserve, available for retasking)",
    KITE_7:                  "KITE-7 (HUMINT — PRENN logistics network access)",
    EAGLE_SIGINT:            "RC-135V/W Rivet Joint — EAGLE SIGINT (SLV comms bands, intermittent)",
    SHADOW_COMMS:            "SHADOW COMMS — National SIGINT Regiment (48hr response)",
    JTAC_TEAM:               "JTAC Team (terminal attack control, 3 available)",
  },

  TargetID: {
    "TGT-ECHO-001":          "VARNAK — ECHO Commander (HVI / TST)",
    "TGT-ECHO-002":          "KAZMER — ECHO IED Facilitator (HVI / TST)",
    "TGT-GAMMA-001":         "IRONBOX — GAMMA C2 Node",
    "TGT-DELTA-001":         "OILCAN — PRENN Fuel Depot (Dual-use / RTL)",
    "TGT-GAMMA-002":         "STONEPILE — GAMMA Mortar Position (Expedited)",
  },

  EngagementAuthority: {
    COMKJTF:                 "COMKJTF — Commander, KESTREL Joint Task Force",
    "TF-KESTREL-CDR":        "TF KESTREL Commander (Delegated)",
    "J3-FIRES":              "J3 FIRES — Non-lethal effects only",
    DENIED:                  "Denied — Authority withheld",
    PENDING:                 "Pending — Awaiting legal review or further intelligence",
  },

  CyclePhase: {
    FIND:                    "Phase SERPENT — Find",
    FIX:                     "Phase SERPENT — Fix",
    FINISH:                  "Phase COPPER — Finish",
    EXPLOIT:                 "Phase COPPER — Exploit",
    ASSESS:                  "Phase CLAW — Assess",
    DEVELOP:                 "Phase CLAW — Develop",
    HOLD:                    "HOLD — Commander decision pending",
    COMPLETE:                "Cycle Complete",
  },

  EffectType: {
    DESTROY:                 "Destroy",
    NEUTRALISE:              "Neutralise",
    DISRUPT:                 "Disrupt",
    DEGRADE:                 "Degrade",
    DENY:                    "Deny",
    SUPPRESS:                "Suppress",
    DECEIVE:                 "Deceive",
    DELAY:                   "Delay",
    INTERDICT:               "Interdict",
    REMOVE:                  "Remove from Network (HVI)",
    EXPLOIT:                 "Exploit (Non-kinetic access)",
  },

  BDAOutcome: {
    "TARGET-DESTROYED":      "Target Destroyed",
    "TARGET-NEUTRALISED":    "Target Neutralised",
    "TARGET-DISRUPTED":      "Target Disrupted",
    "EFFECT-NOT-ACHIEVED":   "Effect Not Achieved — Re-engagement Required",
    "PARTIAL-EFFECT":        "Partial Effect",
    UNKNOWN:                 "BDA Unknown — Collection Incomplete",
    "CIVCAS-ASSESSED":       "⚠ CIVCAS Assessed — Mandatory Reporting Triggered",
  },

  ConfidenceLevel: {
    HIGH:                    "HIGH — Multi-source, recent, corroborated",
    MODERATE:                "MODERATE — Single reliable source or corroborated but aged",
    LOW:                     "LOW — Single source, uncorroborated",
    UNCONFIRMED:             "UNCONFIRMED — Raw intelligence, not yet assessed",
  },

  CDETier: {
    "CDE-1":                 "CDE-1 — Minimal risk (rural, no civilian presence)",
    "CDE-2":                 "CDE-2 — Low risk (rural, sparse population)",
    "CDE-3":                 "CDE-3 — Moderate risk (TF CDR can approve)",
    "CDE-4":                 "CDE-4 — Elevated risk (COMKJTF required)",
    "CDE-5":                 "CDE-5 — High risk: urban / significant civilian presence (COMKJTF required)",
    "CDE-6":                 "CDE-6 — Exceptional: KJTF Legal + COMKJTF + report to higher HQ",
    "NOT-REQUIRED":          "CDE Not Required (outside VICTOR-5/6)",
  },

  HoldReason: {
    "PID-INSUFFICIENT":      "PID Insufficient — 72hr POL standard not met",
    "CDE-UNACCEPTABLE":      "CDE Unacceptable — Proportionality not satisfied",
    "NSL-PROXIMITY":         "NSL Proximity — Too close to protected object",
    "ROE-NOT-MET":           "ROE Not Met",
    "INTEL-STALE":           "Intelligence Stale — Too aged to act on",
    "LEGAL-REVIEW-REQUIRED": "Legal Review Required — JAG assessment pending",
    "COMMANDER-DISCRETION":  "Commander's Discretion — COMKJTF hold",
    "AWAIT-CIVILIAN-WINDOW": "Awaiting Civilian Absence Window (OILCAN — 2200–0300 local)",
  },

  ComponentID: {
    GAMMA:                   "Component GAMMA — Conventional Remnant Force",
    DELTA:                   "Component DELTA — State-backed Non-state Actors",
    ECHO:                    "Component ECHO — Extremist HVI Sub-cell",
    UNKNOWN:                 "Unknown / Unattributed",
  },

  /**
   * CDE profile labels used in the Commander decision panel.
   * Displayed alongside the TNP munition recommendation.
   */
  CDEProfile: {
    LOWEST_COLLATERAL:       "Lowest collateral — RTL and CDE-4/5 appropriate",
    STANDARD_LASER:          "Standard collateral — laser-guided, requires lasing platform",
    STANDARD_GPS:            "Standard collateral — GPS/INS, all-weather capable",
    CAPTURE_ONLY:            "Zero collateral — capture operation, DOMEX value preserved",
    ARTILLERY_LOW_CDE:       "Artillery — appropriate for CDE-1/2, open terrain only",
    ROTARY_PRECISION:        "Rotary precision — MANPADS threat assessment required",
  },

} as const;

// Type helpers for TypeScript consumers
export type ExecutionMethodLabel = typeof DISPLAY_MAP.ExecutionMethod[keyof typeof DISPLAY_MAP.ExecutionMethod];
export type TargetIDLabel = typeof DISPLAY_MAP.TargetID[keyof typeof DISPLAY_MAP.TargetID];
export type CyclePhaseLabel = typeof DISPLAY_MAP.CyclePhase[keyof typeof DISPLAY_MAP.CyclePhase];

/**
 * Helper: resolve any enum value to its display label.
 * Returns the raw value if no mapping found (graceful degradation).
 */
export function resolveLabel(
  category: keyof typeof DISPLAY_MAP,
  value: string
): string {
  const map = DISPLAY_MAP[category] as Record<string, string>;
  return map[value] ?? value;
}
