"""
OPERATION COPPERCLAW — Operator Tool Definitions
COSMIC INDIGO // REL KESTREL COALITION // EXERCISE

Six Anthropic tool schemas for the operator LLM interface.
"""

TOOLS = [
    {
        "name": "cycle_start",
        "description": "Initiate a new F3EAD targeting cycle against a priority target. "
                       "This publishes a cycle_start command to copperclaw.operator-commands, "
                       "which triggers the ISR Tasking service to begin collection.",
        "input_schema": {
            "type": "object",
            "properties": {
                "priority_target": {
                    "type": "string",
                    "enum": [
                        "TGT-ECHO-001",
                        "TGT-ECHO-002",
                        "TGT-GAMMA-001",
                        "TGT-DELTA-001",
                        "TGT-GAMMA-002",
                    ],
                    "description": "The HPTL target ID to begin the cycle against.",
                },
                "operator_intent": {
                    "type": "string",
                    "description": "Plain-language operator intent for this cycle (e.g. 'Capture VARNAK — capture preferred, KSOF direct action').",
                },
                "cycle_id": {
                    "type": "string",
                    "description": "Cycle identifier (e.g. CYCLE-0001). Generated automatically if not provided.",
                },
            },
            "required": ["priority_target"],
        },
    },
    {
        "name": "retask_isr",
        "description": "Redirect a named ISR asset to a new target and PIR. "
                       "Publishes a retask command to copperclaw.operator-commands.",
        "input_schema": {
            "type": "object",
            "properties": {
                "asset": {
                    "type": "string",
                    "enum": ["RAVEN-1", "RAVEN-2", "KITE-7", "EAGLE-SIGINT", "SHADOW-COMMS"],
                    "description": "The ISR asset to retask.",
                },
                "new_target": {
                    "type": "string",
                    "enum": [
                        "TGT-ECHO-001",
                        "TGT-ECHO-002",
                        "TGT-GAMMA-001",
                        "TGT-DELTA-001",
                        "TGT-GAMMA-002",
                    ],
                    "description": "The new target to direct the asset against.",
                },
                "new_pir": {
                    "type": "string",
                    "enum": ["PIR-001", "PIR-002", "PIR-003", "PIR-004", "PIR-NEW"],
                    "description": "The Priority Intelligence Requirement to address.",
                },
                "operator_rationale": {
                    "type": "string",
                    "description": "Reason for the retask.",
                },
            },
            "required": ["asset", "new_target", "new_pir", "operator_rationale"],
        },
    },
    {
        "name": "authorize_target",
        "description": "Inject COMKJTF engagement authorization for a target pending commander decision. "
                       "This unblocks the commander hold point and allows execution to proceed.",
        "input_schema": {
            "type": "object",
            "properties": {
                "target_id": {
                    "type": "string",
                    "enum": [
                        "TGT-ECHO-001",
                        "TGT-ECHO-002",
                        "TGT-GAMMA-001",
                        "TGT-DELTA-001",
                        "TGT-GAMMA-002",
                    ],
                },
                "tnp_id": {
                    "type": "string",
                    "description": "The report_id of the TargetNominationPackage being authorized.",
                },
                "authorized": {
                    "type": "boolean",
                    "description": "Must be true to authorize. Use hold_target to hold.",
                },
                "commanders_guidance": {
                    "type": "string",
                    "description": "COMKJTF guidance to the execution element.",
                },
                "civcas_threshold": {
                    "type": "string",
                    "description": "CIVCAS abort threshold (mandatory for OILCAN and CDE-4+).",
                },
            },
            "required": ["target_id", "tnp_id", "authorized", "commanders_guidance"],
        },
    },
    {
        "name": "hold_target",
        "description": "Place a target on hold with a stated reason. "
                       "The commander hold point remains blocked until hold is lifted.",
        "input_schema": {
            "type": "object",
            "properties": {
                "target_id": {
                    "type": "string",
                    "enum": [
                        "TGT-ECHO-001",
                        "TGT-ECHO-002",
                        "TGT-GAMMA-001",
                        "TGT-DELTA-001",
                        "TGT-GAMMA-002",
                    ],
                },
                "hold_reason": {
                    "type": "string",
                    "enum": [
                        "PID-INSUFFICIENT",
                        "CDE-UNACCEPTABLE",
                        "NSL-PROXIMITY",
                        "ROE-NOT-MET",
                        "INTEL-STALE",
                        "LEGAL-REVIEW-REQUIRED",
                        "COMMANDER-DISCRETION",
                        "AWAIT-CIVILIAN-WINDOW",
                    ],
                },
                "hold_explanation": {
                    "type": "string",
                    "description": "Plain-language explanation of the hold decision.",
                },
                "resume_condition": {
                    "type": "string",
                    "description": "What must change before the hold can be lifted.",
                },
            },
            "required": ["target_id", "hold_reason", "hold_explanation"],
        },
    },
    {
        "name": "request_bda",
        "description": "Request immediate BDA assessment of a recently executed target.",
        "input_schema": {
            "type": "object",
            "properties": {
                "target_id": {
                    "type": "string",
                    "enum": [
                        "TGT-ECHO-001",
                        "TGT-ECHO-002",
                        "TGT-GAMMA-001",
                        "TGT-DELTA-001",
                        "TGT-GAMMA-002",
                    ],
                },
                "execution_report_id": {
                    "type": "string",
                    "description": "The report_id of the ExecutionReport to assess.",
                },
                "urgency": {
                    "type": "string",
                    "enum": ["IMMEDIATE", "PRIORITY", "ROUTINE"],
                },
            },
            "required": ["target_id", "execution_report_id", "urgency"],
        },
    },
    {
        "name": "inject_commander_guidance",
        "description": "Inject plain-language COMKJTF guidance into the cycle state. "
                       "Used to add contextual guidance without triggering specific tool actions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "guidance": {
                    "type": "string",
                    "description": "The COMKJTF guidance text.",
                },
                "applies_to": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of target IDs or agent names this guidance applies to.",
                },
            },
            "required": ["guidance"],
        },
    },
]
