export type TargetId =
  | 'TGT-ECHO-001' | 'TGT-ECHO-002' | 'TGT-GAMMA-001'
  | 'TGT-DELTA-001' | 'TGT-GAMMA-002'

export type TargetOutcome =
  | 'NEUTRALIZED'
  | 'CAPTURED'
  | 'PARTIAL_EFFECT'
  | 'REENGAGEMENT_REQUIRED'

export type CyclePhase =
  | 'FIND' | 'FIX' | 'FINISH' | 'EXPLOIT' | 'ASSESS' | 'DEVELOP'
  | 'HOLD' | 'COMPLETE' | 'IDLE'

export type ConfidenceLevel =
  | 'LOW' | 'MODERATE' | 'MODERATE_HIGH' | 'HIGH'

export type AgentName =
  | 'isr-tasking' | 'collection' | 'allsource-analyst'
  | 'target-nomination' | 'legal-review' | 'commander'
  | 'execution' | 'bda' | 'develop'
  | 'cot-gateway' | 'state' | 'sse-bridge'

export type AgentStatus = 'ACTIVE' | 'HOLD' | 'IDLE' | 'ERROR'

export interface AgentState {
  name: AgentName
  status: AgentStatus
  detail: string
  last_updated: string
}

export interface TargetState {
  target_id: TargetId
  codename: string
  phase: CyclePhase
  confidence: number       // 0-100
  pir_number: string
  legal_cleared: boolean
  hold_reason?: string
  outcome?: TargetOutcome
  last_confirmed_zulu?: string  // ISO timestamp of last collection report fix
  position_uncertainty?: number // 0-1, grows over time
}

export interface PirSatisfaction {
  pir_id: string
  satisfaction_pct: number
  threshold_pct: number
  status: 'RED' | 'AMBER' | 'GREEN'
}

export interface CollectionEvent {
  id: string
  source_type: 'SIGINT' | 'IMINT' | 'HUMINT' | 'ACOUSTIC' | 'COT'
  timestamp_zulu: string
  confidence_weight: number  // 1-10, drives bubble size
  target_id?: TargetId
}

export interface CommanderLogEntry {
  timestamp_zulu: string
  agent: string
  message: string
  level: 'INFO' | 'HOLD' | 'LEGAL' | 'EXECUTE' | 'ASSESS'
}

export interface CycleState {
  cycle_id: string
  active_target_id?: TargetId
  active_target_codename?: string
  phase: CyclePhase
  cycle_start_zulu: string
  elapsed_seconds: number
  agents: AgentState[]
  targets: TargetState[]
  pir_satisfaction: PirSatisfaction[]
  recent_collection: CollectionEvent[]
  commander_log: CommanderLogEntry[]
  awaiting_commander: boolean
  hold_target_id?: TargetId
  hold_tnp_id?: string
}

export interface OperatorMessage {
  role: 'operator' | 'system'
  content: string
  timestamp_zulu: string
}
