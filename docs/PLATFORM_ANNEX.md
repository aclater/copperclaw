# ANNEX P — TF KESTREL EQUIPMENT AND PLATFORM REFERENCE
**OPERATION COPPERCLAW | OPORD 007-XX SUPPLEMENT**
**COSMIC INDIGO // REL KESTREL COALITION**
**EXERCISE — EXERCISE — EXERCISE**

> **BRIEFING USE ONLY.** This annex is for human presenters and audience orientation.
> It is never injected into agent system prompts, LLM calls, or schema fields.
> All automated simulation outputs use generic operational categories.

---

## 1. ISR ASSETS — TF KESTREL

### MC-12W Liberty — RAVEN-1 / RAVEN-2
**Role:** Persistent wide-area ISR, full-motion video and synthetic aperture radar  
**Capability:** Dual-sensor EO/IR and SAR suite; 18-hour endurance enables continuous pattern-of-life collection against HESSEK District targets. Real-time downlink to TF KESTREL J2 fusion cell.  
**Employment in AO HARROW:** RAVEN-1 is the primary asset for PIR-001 (VARNAK pattern of life), currently tracking at VICTOR-5-KILO. RAVEN-2 held in reserve for contingency retasking.  
**Limitation:** Single-aperture collection — cannot simultaneously collect against separated grids. Endurance constrains continuous coverage of all five HPTL targets simultaneously.

### RC-135V/W Rivet Joint — EAGLE SIGINT
**Role:** Airborne signals intelligence collection and exploitation  
**Capability:** Broad-spectrum SIGINT collection across HF, VHF, UHF, and SHF bands; onboard fusion and near-real-time reporting. Tasked against SLV Component ECHO communications pattern and Component GAMMA tactical frequencies.  
**Employment in AO HARROW:** Intermittent coverage due to theatre-level tasking competition. Primary collection against ECHO courier network. SLV's deliberate preference for physical couriers over digital communications significantly degrades EAGLE SIGINT utility against ECHO.  
**Limitation:** 48-hour advance tasking cycle for extended collection windows. Tasking competed at national level.

### SHADOW COMMS — National SIGINT (KESTREL Signals Regiment)
**Role:** Ground-based SIGINT, direction-finding, and communications intelligence  
**Capability:** Persistent ground-based collection at fixed and semi-fixed sites; complements RC-135 with lower-altitude coverage of localised SLV tactical communications.  
**Employment in AO HARROW:** Keyed against Component GAMMA tactical radio nets and Component DELTA logistics coordination frequencies. 48-hour minimum response for re-tasking.

### UH-60M Black Hawk — Rotary QRF
**Role:** Tactical mobility, quick reaction force, ISR cueing (crew-served observation)  
**Capability:** Provides rapid ground force lift for exploitation follow-on. Not a dedicated ISR platform — crew observation and JTAC-from-air capability as secondary function.  
**Employment in AO HARROW:** Pre-positioned at FOB GREYSTONE for QRF tasking post-Finish. Critical for KSOF insertion and extraction on HVI capture operations.

### KITE-7 — HUMINT Source
**Role:** Human intelligence; PRENN logistics network access  
**Capability:** Established source with access to PRENN Energy logistics operations, providing ground-truth confirmation of Component DELTA nightly vehicle movements at OILCAN (TGT-DELTA-001). Graded B/2 reliability.  
**Employment in AO HARROW:** Primary source for PIR-004 (OILCAN civilian absence window). Last report 36 hours ago — collection currency is degrading. Re-contact required before any engagement window is confirmed.  
**Limitation:** Access limited to DELTA logistics sphere; no access to ECHO network.

---

## 2. FIRES ASSETS — TF KESTREL

### M109A7 Paladin — US Artillery Element
**Role:** Self-propelled 155mm howitzer; direct and precision fire support  
**Capability:** Precision-guided munitions capable with Excalibur (GPS/INS). Conventional HE available for area targets. Rapid displacement for counter-battery protection.  
**Employment in AO HARROW:** Primary fires asset for TGT-GAMMA-002 (STONEPILE) engagement. Open terrain and confirmed military-only target makes this the preferred option for expedited mortar suppression. CDE-2 assessed for STONEPILE engagement.  
**Limitation:** Not appropriate for CDE-4/5 urban-proximate targets without precision-guided munitions. Not the primary option for HESSEK District targets.

### AS-90 — UK Artillery Element
**Role:** Self-propelled 155mm howitzer (UK-flagged fires)  
**Capability:** Equivalent capability to M109A7 for most fire missions. Interoperable within TF KESTREL fires coordination cell.  
**Employment in AO HARROW:** Available as alternate fires asset for GAMMA-layer targets. UK national caveats may apply for certain target types — coordinate through J3 FIRES.

### AH-64E Apache — Attack Aviation
**Role:** Rotary-wing attack, close air support, armed ISR  
**Capability:** Longbow radar for target acquisition; Hellfire missile and 30mm cannon for precision engagement. Can operate in degraded weather and low-light. MANPADS threat from 9K38 Igla (see adversary section) requires threat assessment before low-altitude employment.  
**Employment in AO HARROW:** Available for precision engagement of mobile or time-sensitive targets. Preferred for GAMMA materiel targets where artillery is inappropriate. MANPADS threat assessment mandatory before any Apache employment in grid zones VICTOR-5/6.  
**Limitation:** Endurance limits continuous loiter. Vulnerable to SLV MANPADS in contested airspace.

### Precision Air-Delivered Munitions (via JTAC coordination)
**Role:** Fixed-wing precision strike  
**Employment notes for briefing:**

| Munition | Guidance | Profile | Preferred Employment |
|---|---|---|---|
| GBU-12 Paveway II | Laser-guided | Standard collateral | Open terrain targets (IRONBOX, STONEPILE backup) |
| GBU-38 JDAM | GPS/INS | Standard collateral, all-weather | IRONBOX (C2 node); reliable in low-visibility |
| GBU-39B Small Diameter Bomb | GPS/INS | Lowest collateral profile | RTL and CDE-sensitive targets (OILCAN, HESSEK-proximate) |

> The GBU-39B SDB is the preferred munition for any engagement in VICTOR-5/6 where CDE tier is 4 or above, or where the target is on the RTL. Its small warhead minimises collateral radius while maintaining precision against hardened or semi-hardened structures.

---

## 3. SPECIAL OPERATIONS — KSOF ELEMENT

### MH-60M DAP (Direct Action Penetrator) — KSOF Aviation
**Role:** Special operations aviation; armed assault, escort, CASEVAC  
**Capability:** Enhanced performance Black Hawk variant configured for direct action. Provides both insertion/extraction and fire support for ground assault. Terrain-following navigation for low-observable approach.  
**Employment in AO HARROW:** KSOF primary platform for HVI capture operations (VARNAK, KAZMER). The capture-preferred ROE for both ECHO HVI targets reflects their exploitation value — KSOF direct action with MH-60M DAP insertion is the designed Finish method.  
**Limitation:** KSOF not available for routine ISR or non-HVI tasks. Availability requires COMKJTF coordination.

---

## 4. ADVERSARY SYSTEMS — SLV EQUIPMENT REFERENCE

> These systems inform the threat picture for ISR operators, JTAC teams, and the targeting audience. They are the basis for the threat assessment embedded in the simulation scenario. Not injected into agent schemas.

### 120mm 2B11 Sani — STONEPILE Mortar System
**Role:** Heavy mortar, indirect fire  
**Context:** Soviet-legacy system consistent with GAMMA component origin as a conventional remnant force. The 2B11 provides significant range and effect against FOB GREYSTONE perimeter. Acoustic detection (6 hours ago) and subsequent IMINT cueing identifies the firing position at TGT-GAMMA-002 (STONEPILE). The crew-served nature of the system means crew suppression or system destruction both achieve the NEUTRALISE effect.

### 9K38 Igla (SA-18 Grouse) — MANPADS Threat
**Role:** Man-portable air defence system  
**Context:** Assessed in SLV inventory across all three components; most likely held by GAMMA conventional element. Represents the primary threat to low-altitude rotary-wing operations (Apache, Black Hawk, MH-60M DAP) in AO HARROW. MANPADS threat assessment is mandatory before any rotary-wing fires mission in VICTOR-5/6. ISR confirmation of MANPADS operator location is a standing collection requirement.

### RP-377 Series — SLV Electronic Warfare
**Role:** Tactical communications jamming  
**Context:** Low-tier EW capability assessed to DELTA component for deniable disruption of Coalition UHF tactical communications. Consistent with state-backing providing dual-use electronic equipment. Affects JTAC-to-aircraft coordination frequencies. J6 must maintain alternate comms plan for any fires mission in MORRUSK-adjacent grids.

---

## 5. BRIEFER'S NOTES

- The simulation's automated agents use **generic operational categories** throughout (e.g. `PRECISION_STRIKE`, `SOF_DIRECT_ACTION`). The frontend renders these as human-readable labels using the display map (Artifact 2).
- This annex is the **only place** real system designations appear in the COPPERCLAW package.
- When presenting to NATO/MoD audiences, use this annex to contextualise the operational display. Point to the Apache or MC-12W designations on this document; point to the live simulation for cycle execution.
- The scenario is **entirely synthetic**. No classified information is represented. All system capabilities described are drawn from open sources.

---
*ANNEX P END | COSMIC INDIGO // REL KESTREL COALITION | EXERCISE*
