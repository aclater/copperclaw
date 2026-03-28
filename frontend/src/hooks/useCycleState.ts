import { useState, useEffect, useRef } from 'react'
import type { CycleState } from '../types'

const MOCK_STATE: CycleState = {
  cycle_id: 'G7-0047',
  active_target_id: 'TGT-ECHO-001',
  active_target_codename: 'VARNAK',
  phase: 'HOLD',
  cycle_start_zulu: new Date(Date.now() - 188000).toISOString(),
  elapsed_seconds: 188,
  awaiting_commander: true,
  hold_target_id: 'TGT-ECHO-001',
  hold_tnp_id: 'TNP-0047',
  agents: [
    { name: 'isr-tasking',       status: 'ACTIVE', detail: 'RAVEN-1 → VICTOR-5-KILO', last_updated: '' },
    { name: 'collection',        status: 'ACTIVE', detail: '3 reports sent',           last_updated: '' },
    { name: 'allsource-analyst', status: 'ACTIVE', detail: 'Assessment ready',         last_updated: '' },
    { name: 'target-nomination', status: 'ACTIVE', detail: 'TNP-0047 complete',        last_updated: '' },
    { name: 'legal-review',      status: 'ACTIVE', detail: 'Cleared — CDE Tier 2',    last_updated: '' },
    { name: 'commander',         status: 'HOLD',   detail: 'Waiting for you',          last_updated: '' },
    { name: 'execution',         status: 'IDLE',   detail: 'Idle',                     last_updated: '' },
    { name: 'bda',               status: 'IDLE',   detail: 'Idle',                     last_updated: '' },
    { name: 'develop',           status: 'IDLE',   detail: 'Idle',                     last_updated: '' },
    { name: 'cot-gateway',       status: 'ACTIVE', detail: 'Sim mode 30s',             last_updated: '' },
    { name: 'state',             status: 'ACTIVE', detail: 'G7-0047',                  last_updated: '' },
    { name: 'sse-bridge',        status: 'ACTIVE', detail: 'Streaming',                last_updated: '' },
  ],
  targets: [
    { target_id: 'TGT-ECHO-001',  codename: 'VARNAK',    phase: 'HOLD',    confidence: 78, pir_number: 'PIR-001', legal_cleared: true  },
    { target_id: 'TGT-ECHO-002',  codename: 'KAZMER',    phase: 'ASSESS',  confidence: 45, pir_number: 'PIR-002', legal_cleared: false },
    { target_id: 'TGT-GAMMA-001', codename: 'IRONBOX',   phase: 'FIND',    confidence: 91, pir_number: 'PIR-003', legal_cleared: false },
    { target_id: 'TGT-DELTA-001', codename: 'OILCAN',    phase: 'FIX',     confidence: 55, pir_number: 'PIR-004', legal_cleared: false },
    { target_id: 'TGT-GAMMA-002', codename: 'STONEPILE', phase: 'FIND',    confidence: 30, pir_number: 'PIR-001', legal_cleared: false },
  ],
  pir_satisfaction: [
    { pir_id: 'PIR-001', satisfaction_pct: 78, threshold_pct: 72, status: 'AMBER' },
    { pir_id: 'PIR-002', satisfaction_pct: 32, threshold_pct: 72, status: 'RED'   },
    { pir_id: 'PIR-003', satisfaction_pct: 91, threshold_pct: 72, status: 'GREEN' },
    { pir_id: 'PIR-004', satisfaction_pct: 55, threshold_pct: 72, status: 'AMBER' },
  ],
  recent_collection: [
    { id: 'c1', source_type: 'SIGINT',   timestamp_zulu: '', confidence_weight: 6, target_id: 'TGT-ECHO-001'  },
    { id: 'c2', source_type: 'IMINT',    timestamp_zulu: '', confidence_weight: 9, target_id: 'TGT-ECHO-001'  },
    { id: 'c3', source_type: 'HUMINT',   timestamp_zulu: '', confidence_weight: 7, target_id: 'TGT-ECHO-001'  },
    { id: 'c4', source_type: 'ACOUSTIC', timestamp_zulu: '', confidence_weight: 4, target_id: 'TGT-GAMMA-002' },
    { id: 'c5', source_type: 'SIGINT',   timestamp_zulu: '', confidence_weight: 3, target_id: 'TGT-ECHO-002'  },
  ],
  commander_log: [
    { timestamp_zulu: '15:01:14Z', agent: 'ISR',   level: 'INFO',    message: 'RAVEN-1 retasked to VICTOR-5-KILO — begin VARNAK pattern of life collection' },
    { timestamp_zulu: '15:02:38Z', agent: 'J2',    level: 'INFO',    message: '3 reports fused — VARNAK POL 78hr — confidence MODERATE-HIGH — PID standard met' },
    { timestamp_zulu: '15:03:11Z', agent: 'LEGAL', level: 'LEGAL',   message: 'TNP-0047 cleared — CDE Tier 2 — capture method recommended — no NSL conflicts' },
    { timestamp_zulu: '15:04:07Z', agent: 'CMD',   level: 'HOLD',    message: 'Cycle paused — COMKJTF authorization required before execution proceeds' },
  ],
}

export function useCycleState() {
  const [state, setState] = useState<CycleState>(MOCK_STATE)
  const [connected, setConnected] = useState(false)
  const esRef = useRef<EventSource | null>(null)

  useEffect(() => {
    const es = new EventSource('/api/stream')
    esRef.current = es

    es.onopen = () => setConnected(true)
    es.onerror = () => setConnected(false)

    es.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data)
        if (data.event_type === 'cycle_state') {
          setState(data.payload as CycleState)
        }
      } catch { /* ignore parse errors */ }
    }

    return () => { es.close(); esRef.current = null }
  }, [])

  return { state, connected }
}
