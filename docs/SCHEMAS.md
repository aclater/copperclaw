# SCHEMAS — OPERATION COPPERCLAW
COSMIC INDIGO // REL KESTREL COALITION | EXERCISE — EXERCISE — EXERCISE

Schema reference for all agent-to-agent message types and operator layer types.
Generated from copperclaw_shared v1.0.0. For use in agent system prompts (Phase 3).

---

## GridReference

Military Grid Reference System (MGRS) location within AO HARROW. Uses the fictional VICTOR-N-LETTER-XXXXXX format (e.g. VICTOR-5-KILO-229-447).

| Field | Type | Required | Description |
|---|---|---|---|
| zone | str | Yes | Grid zone designator, e.g. `VICTOR-5`, `VICTOR-4`, `VICTOR-6`. |
| sector | str | Yes | Sector letter within zone, e.g. `KILO`, `LIMA`, `NOVEMBER`, `OSCAR`. |
| easting | str | Yes | 3-digit easting within sector, e.g. `229`, `312`, `088`. |
| northing | str | Yes | 3-digit northing within sector, e.g. `447`, `509`, `271`. |

---

## TimeWindow

A time window in Zulu time. Used for civilian absence windows (OILCAN), ISR tasking windows, and POL observation periods.

| Field | Type | Required | Description |
|---|---|---|---|
| start_zulu | str | Yes | Window start time in HHMM Zulu, e.g. `2200` for OILCAN civilian absence. |
| end_zulu | str | Yes | Window end time in HHMM Zulu, e.g. `0300`. |
| duration_hours | Optional[float] | No | Duration in hours, computed or supplied. |
| confirmed | bool | No | Whether this window has been confirmed by collection (e.g. KITE-7 OILCAN window). Defaults to False. |

---

## IntelSource

A single intelligence source contributing to a report. Multiple sources may be listed; confidence is assessed across all.

| Field | Type | Required | Description |
|---|---|---|---|
| source_type | IntelSourceType | Yes | Intelligence discipline of this source (SIGINT, HUMINT, IMINT, OSINT, DOMEX, ACOUSTIC, FUSION). |
| asset_id | Optional[ISRAsset] | No | Named ISR asset if applicable, e.g. RAVEN-1, KITE-7. |
| report_age_hours | float | Yes | Age of this source's reporting in hours at time of assessment. KESTREL standard: >72hr is considered stale for personality targets. |
| reliability_grade | str | Yes | Source reliability grade A–F (A=completely reliable, F=reliability unknown). KITE-7 is graded B; EAGLE-SIGINT intermittent = C. |
| information_grade | str | Yes | Information content grade 1–6 (1=confirmed, 6=cannot be judged). Used with reliability to form NATO STANAG source grading. |
| summary | str | Yes | One-sentence summary of what this source reported, in plain language. |

---

## CivilianConsideration

Civilian presence and collateral damage assessment for a target. Populated by the Target Nomination agent; reviewed by the Commander agent.

| Field | Type | Required | Description |
|---|---|---|---|
| cde_tier | CDETier | Yes | CDE tier per ROE Card Alpha-7 Section 5. Determines engagement authority. Values: CDE-1 through CDE-6, NOT-REQUIRED. CDE 1–3 = TF KESTREL CDR; CDE 4–5 = COMKJTF; CDE 6 = KJTF Legal + COMKJTF. |
| civilian_presence_assessed | bool | Yes | Whether civilians are assessed to be present at or near the target. |
| civilian_count_estimate | Optional[int] | No | Estimated civilian count if present. None = not assessed / zero confirmed. |
| nsl_proximity_metres | Optional[float] | No | Distance to nearest NSL object in metres. NSL objects include HESSEK Mosque Complex and MORRUSK Hospital. |
| proportionality_statement | str | Yes | Plain-language proportionality assessment: expected collateral harm vs anticipated military advantage. Must satisfy AJP-3.9 and ROE Alpha-7. |
| precautionary_measures | List[str] | No | List of precautionary measures taken or recommended, e.g. `["Wait for OILCAN civilian absence window 2200–0300", "Use precision munition to minimise blast radius"]`. Defaults to empty list. |

---

## ROEChecklist

Mandatory ROE compliance checklist per ROE Card Alpha-7. Completed by the Target Nomination agent; reviewed by the Commander agent. All four LOAC principles must be satisfied for engagement to be lawful.

| Field | Type | Required | Description |
|---|---|---|---|
| military_necessity_met | bool | Yes | Confirms the target offers definite military advantage. Every target nominated must contribute to attaining the commander's objectives (FM 3-60 §1-4). |
| distinction_confirmed | bool | Yes | Confirms the target is a legitimate military objective, distinguished from civilians and civilian objects per LOAC. |
| proportionality_satisfied | bool | Yes | Confirms expected CIVCAS/collateral damage is not excessive relative to anticipated concrete and direct military advantage. |
| precaution_applied | bool | Yes | Confirms all feasible precautionary measures have been considered and applied per AJP-3.9 and ROE Alpha-7 Section 1. |
| pid_standard_met | bool | Yes | Confirms Positive Identification has been achieved. For personality targets: dual-source, 72-hour POL minimum (KESTREL standard). |
| not_on_nsl | bool | Yes | Confirms the target is NOT on the No-Strike List. NSL includes MORRUSK Hospital, HESSEK Mosque, UN-flagged facilities. |
| rtl_constraints_noted | Optional[str] | No | If target is on the Restricted Target List, describes constraints. E.g. OILCAN: `Engage only 2200–0500 local with confirmed civilian absence; no incendiary effects; precision munitions only.` |
| cde_completed | bool | Yes | Confirms CDE has been completed where mandatory (all VICTOR-5/6 engagements). CDE is not required for STONEPILE (outside VICTOR-5/6, rural). |
| engagement_authority_confirmed | EngagementAuthority | Yes | The engagement authority that applies per ROE Alpha-7 and AGM. HVI and TST: COMKJTF. STONEPILE: TF KESTREL CDR. Values: COMKJTF, TF-KESTREL-CDR, J3-FIRES, DENIED, PENDING. |
| legal_review_required | bool | No | Whether JAG/legal review is required before engagement authority is granted. Mandatory for CDE 6 and all dual-use facilities with civilian presence. Defaults to False. |

---

## ReportBase

Common fields inherited by all agent-produced reports. Provides traceability, classification, and cycle linkage.

| Field | Type | Required | Description |
|---|---|---|---|
| report_id | str | No | Unique report identifier (UUID4). Auto-generated if not supplied. |
| classification | ClassificationMarking | No | Exercise classification marking. Defaults to `COSMIC INDIGO // REL KESTREL COALITION`. |
| exercise_serial | str | No | Exercise serial identifier. Defaults to `COPPERCLAW-SIM-001`. |
| cycle_id | str | Yes | Identifier for the F3EAD cycle this report belongs to. Format: CYCLE-NNNN, e.g. `CYCLE-0001`. Injected by orchestrator. |
| phase | CyclePhase | Yes | The F3EAD phase during which this report was produced. |
| producing_agent | str | Yes | The agent role that produced this report, e.g. `ISR-TASKING`, `COLLECTION`, `ALL-SOURCE-ANALYST`, `TARGET-NOMINATION`, `COMMANDER`, `EXECUTION`, `BDA`, `DEVELOP`. |
| timestamp_zulu | datetime | No | Report production timestamp in Zulu time. Auto-generated. |
| target_id | TargetID | Yes | The primary HPTL target this report addresses. |
| narrative | str | Yes | Plain-language narrative summary. Must be parseable by a downstream agent and renderable in the frontend panel. Minimum 20 characters. |

---

## ISRTaskingOrder

ISR Tasking agent → Collection agent. Initiates the FIND phase. Extends ReportBase with phase fixed to FIND.

| Field | Type | Required | Description |
|---|---|---|---|
| report_id | str | No | UUID4. Auto-generated. |
| classification | ClassificationMarking | No | Defaults to COSMIC INDIGO // REL KESTREL COALITION. |
| exercise_serial | str | No | Defaults to COPPERCLAW-SIM-001. |
| cycle_id | str | Yes | F3EAD cycle identifier. |
| phase | CyclePhase | No | Fixed to FIND. |
| producing_agent | str | Yes | Set to `ISR-TASKING`. |
| timestamp_zulu | datetime | No | Auto-generated. |
| target_id | TargetID | Yes | HPTL target being tasked against. |
| narrative | str | Yes | Tasking narrative. Min 20 characters. |
| pir_addressed | List[PIRNumber] | Yes | PIR(s) this collection task is designed to answer, e.g. `[PIR-001]` for VARNAK location development. Minimum 1 entry. |
| asset_tasked | ISRAsset | Yes | Named ISR asset being tasked. Must be available and appropriate to the collection requirement. |
| collection_window | TimeWindow | Yes | The Zulu time window during which collection should occur. |
| target_area | GridReference | Yes | Primary collection area. For PIR-001 (VARNAK): VICTOR-5-KILO-229-447 and adjacent grids in HESSEK District. |
| collection_method | IntelSourceType | Yes | The intelligence discipline this asset will employ, e.g. IMINT for RAVEN-1. |
| specific_indicators | List[str] | No | Specific indicators the collection asset should look for. Defaults to empty list. |
| priority | int | Yes | Collection priority 1–5 (1=highest). Drives asset deconfliction. Must be between 1 and 5 inclusive. |
| retask_from_previous | bool | No | Whether this is a retask of an asset from a previous collection line. Defaults to False. |
| previous_task_id | Optional[str] | No | report_id of the ISRTaskingOrder this replaces, if retasking. |

---

## CollectionReport

Collection agent → All-Source Analyst agent. Carries raw intelligence from sensor execution against an ISRTaskingOrder. Extends ReportBase with phase fixed to FIX.

| Field | Type | Required | Description |
|---|---|---|---|
| report_id | str | No | UUID4. Auto-generated. |
| classification | ClassificationMarking | No | Defaults to COSMIC INDIGO // REL KESTREL COALITION. |
| exercise_serial | str | No | Defaults to COPPERCLAW-SIM-001. |
| cycle_id | str | Yes | F3EAD cycle identifier. |
| phase | CyclePhase | No | Fixed to FIX. |
| producing_agent | str | Yes | Set to `COLLECTION`. |
| timestamp_zulu | datetime | No | Auto-generated. |
| target_id | TargetID | Yes | HPTL target this report addresses. |
| narrative | str | Yes | Collection narrative. Min 20 characters. |
| tasking_order_id | str | Yes | report_id of the ISRTaskingOrder that generated this collection. |
| asset_id | ISRAsset | Yes | The ISR asset that conducted this collection. |
| pir_addressed | List[PIRNumber] | Yes | PIR(s) this report partially or fully answers. |
| collection_start_zulu | str | Yes | Collection window start in HHMM Zulu, e.g. `0600`, `2200`. |
| collection_end_zulu | str | Yes | Collection window end in HHMM Zulu, e.g. `0800`, `2300`. |
| source_type | IntelSourceType | Yes | Intelligence discipline of this collection. |
| raw_intelligence | str | Yes | Raw intelligence product in plain language — what the sensor observed, intercepted, or reported. Written in the voice of the platform/source. Not yet fused or assessed. Min 30 characters. |
| location_confirmed | Optional[GridReference] | No | If the collection confirmed a target location, the grid. None if not confirmed. |
| pol_hours_added | Optional[float] | No | For personality targets: additional hours of pattern-of-life observation this collection contributes. Must be >= 0. |
| pol_total_hours | Optional[float] | No | Running total of POL hours accumulated against this personality target. VARNAK baseline: 48hrs; PID requires 72hrs. Must be >= 0. |
| negative_information | Optional[str] | No | What the collection did NOT find, where relevant. Negative information is valid intelligence (FM 3-60 §2-10). |
| follow_on_collection_required | bool | Yes | Whether additional collection is needed before PID standard can be met. |
| confidence | ConfidenceLevel | Yes | Confidence in the accuracy of this collection report. Values: HIGH, MODERATE, LOW, UNCONFIRMED. |

---

## IntelligenceAssessment

All-Source Analyst agent → Target Nomination agent. Fuses multiple CollectionReports into a comprehensive target assessment that gates TNP generation. Extends ReportBase with phase fixed to FIX.

| Field | Type | Required | Description |
|---|---|---|---|
| report_id | str | No | UUID4. Auto-generated. |
| classification | ClassificationMarking | No | Defaults to COSMIC INDIGO // REL KESTREL COALITION. |
| exercise_serial | str | No | Defaults to COPPERCLAW-SIM-001. |
| cycle_id | str | Yes | F3EAD cycle identifier. |
| phase | CyclePhase | No | Fixed to FIX. |
| producing_agent | str | Yes | Set to `ALL-SOURCE-ANALYST`. |
| timestamp_zulu | datetime | No | Auto-generated. |
| target_id | TargetID | Yes | HPTL target being assessed. |
| narrative | str | Yes | Assessment narrative. Min 20 characters. |
| source_reports | List[str] | Yes | List of report_ids of CollectionReports fused in this assessment. Minimum 1 entry. |
| sources | List[IntelSource] | Yes | Structured source list with reliability and information grades. Minimum 1 entry. |
| target_type | TargetType | Yes | Target category per FM 3-60: PERSONALITY for HVI; NODE for IRONBOX; DUAL_USE for OILCAN; FIRE_POSITION for STONEPILE. |
| target_codename | TargetCodename | Yes | HPTL codename for this target. |
| siv_component | ComponentID | Yes | Which SLV component this target belongs to (GAMMA, DELTA, ECHO, UNKNOWN). |
| confirmed_location | Optional[GridReference] | No | Current confirmed location. None if location not yet confirmed. |
| location_confidence | ConfidenceLevel | Yes | Confidence in the confirmed location. |
| pol_hours_complete | Optional[float] | No | For personality targets: total POL hours accumulated. KESTREL standard = 72hr minimum. VARNAK baseline: 48hr. |
| pid_standard_met | bool | Yes | Whether KESTREL PID standard is met: dual-source confirmation AND 72-hour pattern of life for personality targets. Gates whether a TNP can be generated. |
| pid_shortfall | Optional[str] | No | If pid_standard_met=False, describes what is missing, e.g. `VARNAK POL is 56hrs complete; 16hrs additional observation required.` |
| intelligence_gaps | List[str] | No | Remaining intelligence gaps for this target. Defaults to empty list. |
| exploitation_value | str | Yes | Assessment of intelligence exploitation value if target is engaged. Values: CRITICAL, HIGH, MEDIUM, LOW. |
| threat_to_friendly_forces | Optional[str] | No | If the target poses a direct threat to friendly forces, describes it. STONEPILE poses mortar threat to FOB GREYSTONE. |
| recommended_action | str | Yes | All-Source Analyst's recommended next action. |
| overall_confidence | ConfidenceLevel | Yes | Overall assessment confidence across all sources. |

---

## TargetNominationPackage

Target Nomination agent → Commander agent. Formal targeting package nominating a target for engagement authority. The Commander agent reviews and issues EngagementAuthorization or a hold. Extends ReportBase with phase fixed to FINISH.

| Field | Type | Required | Description |
|---|---|---|---|
| report_id | str | No | UUID4. Auto-generated. |
| classification | ClassificationMarking | No | Defaults to COSMIC INDIGO // REL KESTREL COALITION. |
| exercise_serial | str | No | Defaults to COPPERCLAW-SIM-001. |
| cycle_id | str | Yes | F3EAD cycle identifier. |
| phase | CyclePhase | No | Fixed to FINISH. |
| producing_agent | str | Yes | Set to `TARGET-NOMINATION`. |
| timestamp_zulu | datetime | No | Auto-generated. |
| target_id | TargetID | Yes | HPTL target being nominated. |
| narrative | str | Yes | TNP narrative. Min 20 characters. |
| assessment_id | str | Yes | report_id of the IntelligenceAssessment this TNP is based on. |
| target_codename | TargetCodename | Yes | HPTL codename for this target. |
| target_type | TargetType | Yes | Target type category. |
| target_location | GridReference | Yes | Confirmed target location at time of nomination. |
| desired_effect | EffectType | Yes | Desired effect from FM 3-60 §1-6 vocabulary. HVI: REMOVE; IRONBOX: DESTROY; OILCAN: DISRUPT; STONEPILE: NEUTRALISE. |
| recommended_execution_method | ExecutionMethod | Yes | Recommended method of engagement. Must be appropriate to target type and ROE. HVI (capture preferred): SOF_DIRECT_ACTION; STONEPILE: ARTILLERY_FIRE. |
| alternative_execution_methods | List[ExecutionMethod] | No | Alternative execution methods if recommended method is unavailable. Defaults to empty list. |
| engagement_window | Optional[TimeWindow] | No | Recommended engagement window. Mandatory for OILCAN (2200–0300 local, civilian absence). Optional for other targets. |
| roe_checklist | ROEChecklist | Yes | Completed ROE compliance checklist per ROE Card Alpha-7. All fields must be populated. Commander agent will review each field. |
| civilian_consideration | CivilianConsideration | Yes | CDE and civilian presence assessment. |
| is_tst | bool | Yes | Whether this target is designated as a Time-Sensitive Target. TST targets: VARNAK (TGT-ECHO-001) and KAZMER (TGT-ECHO-002) only. |
| tst_justification | Optional[str] | No | If is_tst=True, the justification for TST designation. Required per JP 3-60. |
| exploitation_plan | str | Yes | Plan for exploitation following the Finish action. |
| requesting_authority | str | No | The authority requesting this engagement. Defaults to `J2/J3 TF KESTREL`. |
| roe_compliance_summary | str | Yes | Plain-language summary of ROE compliance assessment written for COMKJTF review. Must address all four LOAC principles explicitly. |

---

## EngagementAuthorization

Commander agent → Execution agent. Reviews the TNP as COMKJTF and issues either authorization or a hold decision. May reflect a real operator decision if operator_injected=True. Extends ReportBase with phase fixed to FINISH.

| Field | Type | Required | Description |
|---|---|---|---|
| report_id | str | No | UUID4. Auto-generated. |
| classification | ClassificationMarking | No | Defaults to COSMIC INDIGO // REL KESTREL COALITION. |
| exercise_serial | str | No | Defaults to COPPERCLAW-SIM-001. |
| cycle_id | str | Yes | F3EAD cycle identifier. |
| phase | CyclePhase | No | Fixed to FINISH. |
| producing_agent | str | Yes | Set to `COMMANDER`. |
| timestamp_zulu | datetime | No | Auto-generated. |
| target_id | TargetID | Yes | HPTL target being actioned. |
| narrative | str | Yes | Commander's decision narrative. Min 20 characters. |
| tnp_id | str | Yes | report_id of the TargetNominationPackage being actioned. |
| target_codename | TargetCodename | Yes | HPTL codename. |
| authorized | bool | Yes | Whether engagement is authorized. True = execute; False = hold (see hold_reason). |
| hold_reason | Optional[HoldReason] | No | If authorized=False, the reason for holding. Must be populated when authorized=False. Values: PID-INSUFFICIENT, CDE-UNACCEPTABLE, NSL-PROXIMITY, ROE-NOT-MET, INTEL-STALE, LEGAL-REVIEW-REQUIRED, COMMANDER-DISCRETION, AWAIT-CIVILIAN-WINDOW. |
| hold_explanation | Optional[str] | No | If authorized=False, plain-language explanation of the hold decision. |
| authority_level | EngagementAuthority | Yes | The engagement authority being exercised. |
| authorized_execution_method | Optional[ExecutionMethod] | No | If authorized=True, the approved execution method. May differ from TNP recommendation. |
| authorized_engagement_window | Optional[TimeWindow] | No | If authorized=True, the approved engagement window. Commander may constrain the window further than TNP recommended. |
| commanders_guidance | str | Yes | Commander's guidance to the Execution agent. |
| operator_injected | bool | No | Whether this decision reflects a real operator input via the Operator LLM layer. Defaults to False. |
| operator_instruction | Optional[str] | No | The operator's natural-language instruction that drove this decision, if operator_injected=True. |
| civcas_threshold | Optional[str] | No | Commander's explicit CIVCAS threshold for this engagement. Mandatory for OILCAN and any CDE 5+ engagement. |

---

## ExecutionReport

Execution agent → BDA agent. Simulates the fires/effects action authorised by the EngagementAuthorization. Extends ReportBase with phase fixed to EXPLOIT.

| Field | Type | Required | Description |
|---|---|---|---|
| report_id | str | No | UUID4. Auto-generated. |
| classification | ClassificationMarking | No | Defaults to COSMIC INDIGO // REL KESTREL COALITION. |
| exercise_serial | str | No | Defaults to COPPERCLAW-SIM-001. |
| cycle_id | str | Yes | F3EAD cycle identifier. |
| phase | CyclePhase | No | Fixed to EXPLOIT. |
| producing_agent | str | Yes | Set to `EXECUTION`. |
| timestamp_zulu | datetime | No | Auto-generated. |
| target_id | TargetID | Yes | HPTL target engaged. |
| narrative | str | Yes | Execution narrative. Min 20 characters. |
| authorization_id | str | Yes | report_id of the EngagementAuthorization that directed this execution. |
| target_codename | TargetCodename | Yes | HPTL codename of the target engaged. |
| execution_method_used | ExecutionMethod | Yes | The execution method actually used. May differ from authorization if circumstances required adaptation. |
| method_deviation | Optional[str] | No | If execution method differed from authorization, explains why. |
| engagement_time_zulu | str | Yes | Time of engagement in HHMM Zulu, e.g. `0215`, `1437`. |
| engagement_grid | GridReference | Yes | Grid at which the engagement occurred. |
| execution_narrative | str | Yes | Detailed narrative of the execution. Written in the voice of the fires/effects simulator. Min 50 characters. |
| immediate_effects_observed | str | Yes | Immediate effects observed at time of engagement, before BDA assessment. |
| civcas_observed | bool | Yes | Whether any actual or suspected civilian casualties were observed. If True, immediate reporting to COMKJTF is mandatory per ROE Alpha-7 §7. |
| civcas_detail | Optional[str] | No | If civcas_observed=True, detail of observed CIVCAS. Mandatory when civcas_observed=True. |
| exploitation_opportunity | bool | Yes | Whether the execution created exploitation opportunities (accessible site, captured persons, recoverable material). |
| exploitation_description | Optional[str] | No | If exploitation_opportunity=True, what is available for exploitation. |
| follow_on_isr_required | bool | Yes | Whether ISR tasking is needed immediately post-execution, e.g. for BDA collection. |

---

## BDAReport

BDA agent → Develop agent. Assesses the effect of the execution against the desired effect stated in the TNP. Determines whether the objective was achieved and what further action is required. Extends ReportBase with phase fixed to ASSESS.

| Field | Type | Required | Description |
|---|---|---|---|
| report_id | str | No | UUID4. Auto-generated. |
| classification | ClassificationMarking | No | Defaults to COSMIC INDIGO // REL KESTREL COALITION. |
| exercise_serial | str | No | Defaults to COPPERCLAW-SIM-001. |
| cycle_id | str | Yes | F3EAD cycle identifier. |
| phase | CyclePhase | No | Fixed to ASSESS. |
| producing_agent | str | Yes | Set to `BDA`. |
| timestamp_zulu | datetime | No | Auto-generated. |
| target_id | TargetID | Yes | HPTL target assessed. |
| narrative | str | Yes | BDA narrative. Min 20 characters. |
| execution_report_id | str | Yes | report_id of the ExecutionReport this BDA assesses. |
| target_codename | TargetCodename | Yes | HPTL codename of the assessed target. |
| desired_effect | EffectType | Yes | The desired effect from the TNP against which this BDA assesses. |
| bda_outcome | BDAOutcome | Yes | Assessment of whether the desired effect was achieved. Values: TARGET-DESTROYED, TARGET-NEUTRALISED, TARGET-DISRUPTED, EFFECT-NOT-ACHIEVED, PARTIAL-EFFECT, UNKNOWN, CIVCAS-ASSESSED. |
| physical_damage_assessment | str | Yes | Assessment of physical damage or status. For materiel: structural/functional damage. For personality: confirmed status (captured/KIA/escaped/unknown). For dual-use: operational status of the facility. |
| functional_damage_assessment | str | Yes | Assessment of functional damage — whether the target's military function has been degraded. |
| network_effect_assessment | str | Yes | Assessment of the effect on the broader SLV network. |
| civcas_confirmed | bool | Yes | Whether civilian casualties are confirmed in BDA. If True, CIVCAS reporting chain must be triggered. |
| civcas_count | Optional[int] | No | Confirmed or estimated CIVCAS count. Exercise use only. |
| re_engagement_required | bool | Yes | Whether the target requires re-engagement to achieve the desired effect. |
| re_engagement_rationale | Optional[str] | No | If re_engagement_required=True, the rationale. |
| exploitation_results | Optional[str] | No | Summary of exploitation results from the Finish phase that inform BDA. |
| bda_collection_gaps | List[str] | No | Collection gaps remaining in the BDA — what could not be assessed. Defaults to empty list. |
| assessment_confidence | ConfidenceLevel | Yes | Confidence in this BDA assessment. |

---

## DevelopLead

Develop agent → ISR Tasking agent (closes the F3EAD loop). Processes DOMEX products, BDA results, and exploitation intelligence to generate new leads and updated requirements. Extends ReportBase with phase fixed to DEVELOP.

| Field | Type | Required | Description |
|---|---|---|---|
| report_id | str | No | UUID4. Auto-generated. |
| classification | ClassificationMarking | No | Defaults to COSMIC INDIGO // REL KESTREL COALITION. |
| exercise_serial | str | No | Defaults to COPPERCLAW-SIM-001. |
| cycle_id | str | Yes | F3EAD cycle identifier. |
| phase | CyclePhase | No | Fixed to DEVELOP. |
| producing_agent | str | Yes | Set to `DEVELOP`. |
| timestamp_zulu | datetime | No | Auto-generated. |
| target_id | TargetID | Yes | HPTL target this develop report derives from. |
| narrative | str | Yes | Develop narrative. Min 20 characters. |
| bda_report_id | str | Yes | report_id of the BDAReport that generated these leads. |
| source_target | TargetCodename | Yes | The HPTL target from whose exploitation these leads derive. |
| new_leads | List[str] | No | List of new intelligence leads generated by DOMEX and exploitation. Each lead should be specific and actionable. Defaults to empty list. |
| new_pir_requirements | List[str] | No | New Priority Intelligence Requirements generated by the Develop phase, to be formalised by the ISR Tasking agent in the next cycle. Defaults to empty list. |
| network_update | str | Yes | Updated assessment of the SLV target network following this cycle. Describes changes in network structure, identified gaps, and remaining nodes. |
| recommended_next_target | Optional[TargetID] | No | Recommended HPTL target for the next cycle, based on lead analysis. None if a new target not on current HPTL is identified. |
| new_target_nomination | Optional[str] | No | If a new target not on the current HPTL is identified, describes it for J2 development. |
| cycle_recommendation | str | Yes | Develop agent's recommendation for next cycle action, e.g. `INITIATE new cycle against TGT-ECHO-002 (KAZMER)` or `RE-ENGAGE TGT-DELTA-001 (OILCAN)`. |
| domex_products | List[str] | No | List of DOMEX products generated (documents, devices, media). Defaults to empty list. |
| dissemination_list | List[str] | No | Agencies and cells to which DOMEX products and leads are disseminated. Defaults to empty list. |

---

## TargetCycleStatus

Status of a single target within the current cycle. Embedded in CycleState.target_statuses.

| Field | Type | Required | Description |
|---|---|---|---|
| target_id | TargetID | Yes | HPTL target identifier. |
| codename | TargetCodename | Yes | HPTL codename. |
| current_phase | CyclePhase | Yes | Current F3EAD phase for this target. |
| pid_met | bool | Yes | Whether PID standard has been met for this target. |
| pol_hours_complete | Optional[float] | No | Total POL hours accumulated for personality targets. |
| last_report_id | Optional[str] | No | report_id of the most recent agent report for this target. |
| last_report_type | Optional[str] | No | Report type name of the most recent report, e.g. `CollectionReport`. |
| authorized | Optional[bool] | No | Whether engagement has been authorized for this target. None if not yet at Commander hold point. |
| bda_outcome | Optional[BDAOutcome] | No | BDA outcome if the target has been engaged. None if not yet assessed. |
| on_hold | bool | No | Whether the target is currently on hold. Defaults to False. |
| hold_reason | Optional[HoldReason] | No | The reason for the hold if on_hold=True. |
| notes | Optional[str] | No | Free-text notes on this target's status. |

---

## ISRAssetStatus

Current status of a named ISR asset. Embedded in CycleState.isr_asset_statuses.

| Field | Type | Required | Description |
|---|---|---|---|
| asset_id | ISRAsset | Yes | Named ISR asset identifier (RAVEN-1, RAVEN-2, KITE-7, EAGLE-SIGINT, SHADOW-COMMS, JTAC-TEAM). |
| currently_tasked | bool | Yes | Whether this asset is currently on a collection task. |
| current_task_target | Optional[TargetID] | No | The HPTL target the asset is currently tasked against. None if not tasked. |
| current_pir | Optional[PIRNumber] | No | The PIR the asset is currently addressing. None if not tasked. |
| available_from_zulu | Optional[str] | No | HHMM Zulu time from which the asset will next be available. None if currently available. |
| endurance_hours_remaining | Optional[float] | No | Asset endurance remaining in hours. |
| notes | Optional[str] | No | Free-text notes on asset status, e.g. maintenance, repositioning. |

---

## CycleState

Full current state of the F3EAD simulation cycle. Injected as context into the Operator LLM on every turn. Also the primary data structure for the frontend operational display. Republished to copperclaw.cycle-state by the state-service after every mutation.

| Field | Type | Required | Description |
|---|---|---|---|
| classification | ClassificationMarking | No | Defaults to COSMIC INDIGO // REL KESTREL COALITION. |
| exercise_serial | str | No | Defaults to COPPERCLAW-SIM-001. |
| cycle_id | str | Yes | Current cycle identifier, e.g. `CYCLE-0001`. |
| cycle_sequence | int | Yes | Monotonically increasing cycle counter. Must be >= 1. |
| timestamp_zulu | datetime | No | Auto-generated. |
| overall_phase | CyclePhase | Yes | The current dominant phase of the cycle. Individual targets may be in different phases within the same cycle. |
| commander_priority_target | TargetID | No | Current commander's priority target. Defaults to TGT-ECHO-001 (VARNAK). |
| target_statuses | List[TargetCycleStatus] | Yes | Status of each HPTL target in the current cycle. |
| isr_asset_statuses | List[ISRAssetStatus] | No | Current status of each named ISR asset. Defaults to empty list. |
| active_pirs | List[PIRNumber] | No | PIRs currently active and driving collection. Defaults to empty list. |
| latest_report_ids | Dict[str, str] | No | Map of producing_agent → latest report_id for that agent in this cycle, e.g. `{"COLLECTION": "uuid..."}`. Defaults to empty dict. |
| pending_commander_decision | Optional[str] | No | report_id of a TargetNominationPackage awaiting Commander decision. Non-null signals the frontend to render the Commander Decision UI. |
| cycle_events | List[str] | No | Ordered list of significant cycle events as plain-language strings. Defaults to empty list. |
| operator_guidance_active | Optional[str] | No | Any active operator guidance injected via inject_commander_guidance tool. Displayed in the frontend and injected into agent context. |
| simulation_warnings | List[str] | No | Non-blocking warnings surfaced by agents, e.g. ISR asset endurance low, CIVCAS risk elevated, stale intelligence. Defaults to empty list. |

---

## CommanderLogEntry

A single entry in the append-only Commander's Log maintained by the Operator LLM. Provides chronological accountability for all decisions in the simulation. Published to copperclaw.commander-log.

| Field | Type | Required | Description |
|---|---|---|---|
| entry_id | str | No | UUID4. Auto-generated. |
| timestamp_zulu | datetime | No | Auto-generated. |
| cycle_id | str | Yes | The cycle this entry belongs to. |
| entry_type | Literal[...] | Yes | Category of this log entry. Values: `OPERATOR_COMMAND`, `AGENT_EVENT`, `ENGAGEMENT_AUTHORIZED`, `ENGAGEMENT_HELD`, `CIVCAS_REPORT`, `CYCLE_START`, `CYCLE_COMPLETE`, `ISR_RETASK`, `OPERATOR_GUIDANCE`, `SYSTEM_NOTE`. |
| actor | str | Yes | Who or what generated this entry, e.g. `OPERATOR`, `COMKJTF`, `ISR-TASKING`, `COLLECTION`, `SYSTEM`. |
| subject_target | Optional[TargetID] | No | Target this entry relates to, if applicable. |
| content | str | Yes | The log entry content in plain language, written in chronological operational voice. |
| related_report_id | Optional[str] | No | report_id of the agent report this entry relates to, for traceability. |
| classification | ClassificationMarking | No | Defaults to COSMIC INDIGO // REL KESTREL COALITION. |

---

## SSEEvent

Server-Sent Event envelope for streaming agent state to the frontend. The SSE bridge wraps every consumed Kafka message in this envelope. The frontend routes on event_type to update the correct UI panel.

| Field | Type | Required | Description |
|---|---|---|---|
| event_type | Literal[...] | Yes | Event type string used by the frontend to route the payload. Values: `cycle_state_update`, `isr_tasking_order`, `collection_report`, `intelligence_assessment`, `target_nomination_package`, `engagement_authorization`, `execution_report`, `bda_report`, `develop_lead`, `commander_log_entry`, `operator_tool_result`, `simulation_error`. |
| cycle_id | str | Yes | The cycle this event belongs to. |
| timestamp_zulu | datetime | No | Auto-generated. |
| data | Dict[str, Any] | Yes | The full serialised payload — a ReportBase subclass or CycleState, serialised with `model.model_dump()`. |
| sequence | int | Yes | Monotonically increasing sequence number within the cycle. Frontend uses this to detect missed events. Must be >= 0. |

---

## CycleStartTool

Operator tool: `cycle_start`. Initiates a new F3EAD targeting cycle. The operator may specify the priority target; defaults to COMKJTF priority.

| Field | Type | Required | Description |
|---|---|---|---|
| tool_name | Literal["cycle_start"] | No | Fixed to `cycle_start`. |
| priority_target | TargetID | No | Target to prioritise in this cycle. Defaults to TGT-ECHO-001 (VARNAK). |
| operator_intent | Optional[str] | No | Optional plain-language operator intent statement to inject into agent context. |

---

## RetaskISRTool

Operator tool: `retask_isr`. Redirects a named ISR asset to a new target/PIR.

| Field | Type | Required | Description |
|---|---|---|---|
| tool_name | Literal["retask_isr"] | No | Fixed to `retask_isr`. |
| asset | ISRAsset | Yes | The ISR asset to retask. |
| new_target | TargetID | Yes | The target to task the asset against. |
| new_pir | PIRNumber | Yes | The PIR the retasked collection will address. |
| operator_rationale | str | Yes | Operator's rationale for the retask. |

---

## AuthorizeTargetTool

Operator tool: `authorize_target`. Injects a COMKJTF engagement authorization decision into the Commander agent. Reflects an actual operator decision at the human-in-the-loop node.

| Field | Type | Required | Description |
|---|---|---|---|
| tool_name | Literal["authorize_target"] | No | Fixed to `authorize_target`. |
| target_id | TargetID | Yes | The target being authorized. |
| tnp_id | str | Yes | report_id of the TNP being actioned. |
| authorized | bool | Yes | Whether engagement is authorized. |
| commanders_guidance | str | Yes | COMKJTF's guidance to the Execution agent. |
| civcas_threshold | Optional[str] | No | CIVCAS threshold constraint for this engagement. |

---

## HoldTargetTool

Operator tool: `hold_target`. Places a target on hold, preventing the cycle from proceeding to Finish.

| Field | Type | Required | Description |
|---|---|---|---|
| tool_name | Literal["hold_target"] | No | Fixed to `hold_target`. |
| target_id | TargetID | Yes | The target to place on hold. |
| hold_reason | HoldReason | Yes | Reason for the hold. |
| hold_explanation | str | Yes | Plain-language hold explanation. |
| resume_condition | Optional[str] | No | Condition under which the hold should be lifted, e.g. `Resume when VARNAK POL reaches 72 hours.` |

---

## RequestBDATool

Operator tool: `request_bda`. Directs the BDA agent to produce an immediate assessment of a target following execution, outside of the normal cycle cadence.

| Field | Type | Required | Description |
|---|---|---|---|
| tool_name | Literal["request_bda"] | No | Fixed to `request_bda`. |
| target_id | TargetID | Yes | The target requiring BDA. |
| execution_report_id | str | Yes | report_id of the ExecutionReport to assess. |
| urgency | Literal["IMMEDIATE", "PRIORITY", "ROUTINE"] | No | BDA urgency. IMMEDIATE = within 1hr; PRIORITY = within 6hrs; ROUTINE = next cycle. Defaults to `PRIORITY`. |

---

## InjectCommanderGuidanceTool

Operator tool: `inject_commander_guidance`. Injects plain-language COMKJTF guidance into the cycle state and all subsequent agent contexts. Does not directly authorize or hold — provides intent that agents must incorporate into their reasoning.

| Field | Type | Required | Description |
|---|---|---|---|
| tool_name | Literal["inject_commander_guidance"] | No | Fixed to `inject_commander_guidance`. |
| guidance | str | Yes | COMKJTF guidance in plain language. Injected into cycle state and all subsequent agent system contexts. |
| applies_to | Optional[List[TargetID]] | No | If guidance applies to specific targets only, list them. None = guidance applies to all targets in the cycle. |

---

## OperatorToolResult

What the FastAPI backend returns to the Operator LLM after processing a tool call. Used to confirm the action was taken and update the operator's context.

| Field | Type | Required | Description |
|---|---|---|---|
| tool_name | str | Yes | The tool call that was processed. |
| success | bool | Yes | Whether the tool call was successfully processed. |
| message | str | Yes | Plain-language result message for the Operator LLM context. |
| affected_cycle_id | str | Yes | The cycle_id of the cycle affected by this tool call. |
| generated_report_id | Optional[str] | No | If the tool call generated a new report, its report_id. |
| updated_cycle_state | Optional[CycleState] | No | Updated CycleState snapshot following the tool call. Injected into operator context for next turn. |
| error_detail | Optional[str] | No | If success=False, the error detail. |
