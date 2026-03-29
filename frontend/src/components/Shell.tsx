import { useCallback } from 'react'
import type { CycleState, OperatorMessage } from '../types'
import { TopBar } from './TopBar'
import { MetricCard } from './MetricCard'
import { ConfidenceRing } from './ConfidenceRing'
import { CcirPanel } from './CcirPanel'
import { DomainRadar } from './DomainRadar'
import { TacticalMap } from './TacticalMap'
import { HoldStrip } from './HoldStrip'
import { DecisionLog } from './DecisionLog'
import { AgentMesh } from './AgentMesh'
import { SeismoPanel } from './SeismoPanel'
import { OperatorChat } from './OperatorChat'

interface ShellProps {
  state: CycleState
  connected: boolean
  operatorInput: string
  setOperatorInput: (v: string) => void
  transmit: () => void
  sending: boolean
  messages: OperatorMessage[]
  appendMessage: (msg: OperatorMessage) => void
}

export function Shell({
  state, connected,
  operatorInput, setOperatorInput, transmit, sending, messages, appendMessage,
}: ShellProps) {
  const awaitingCount = state.awaiting_commander ? 1 : 0
  const awaitingTarget = state.active_target_codename ?? '—'
  const activeTargetCount = state.targets.filter(
    t => t.phase !== 'IDLE' && t.phase !== 'COMPLETE'
  ).length
  const primaryPir = state.pir_satisfaction.find(p => p.pir_id === 'PIR-001')
  const holdTarget = state.targets.find(t => t.target_id === state.hold_target_id)

  const handleMapAction = useCallback((msg: string) => {
    appendMessage({
      role: 'operator' as const,
      content: msg,
      timestamp_zulu: new Date().toISOString(),
    })
  }, [appendMessage])

  return (
    <div style={{
      display: 'grid',
      gridTemplateRows: '38px 1fr',
      height: '100vh',
      overflow: 'hidden',
      background: 'var(--bg-shell)',
    }}>
      {/* Top bar */}
      <TopBar state={state} connected={connected} />

      {/* Main content */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '160px 1fr 260px',
        gap: 6,
        padding: 6,
        overflow: 'hidden',
        minHeight: 0,
      }}>
        {/* Left column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6, overflow: 'hidden', minHeight: 0 }}>
          <MetricCard
            value={awaitingCount}
            label="Target awaiting auth"
            sub={awaitingCount > 0 ? awaitingTarget : 'None pending'}
            color={awaitingCount > 0 ? 'var(--amber)' : 'var(--green)'}
          />
          <MetricCard
            value={activeTargetCount}
            label="Targets being tracked"
            sub={`${state.targets.length} on HPTL`}
            color="var(--green)"
          />
          <ConfidenceRing
            pct={primaryPir?.satisfaction_pct ?? 0}
            label="PIR-001"
            sublabel="VARNAK intel"
            color={
              primaryPir?.status === 'GREEN' ? 'var(--green)' :
              primaryPir?.status === 'AMBER' ? 'var(--amber)' :
              'var(--red)'
            }
          />
          <DomainRadar />
          <CcirPanel
            pirs={state.pir_satisfaction}
            recentCollection={state.recent_collection}
          />
          <DecisionLog entries={state.commander_log} />
        </div>

        {/* Center column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6, overflow: 'hidden', minHeight: 0 }}>
          <div style={{ flex: 1, overflow: 'hidden', minHeight: 0 }}>
            <TacticalMap
              targets={state.targets}
              cycleState={state}
              onActionExecuted={handleMapAction}
            />
          </div>
          <HoldStrip
            visible={state.awaiting_commander}
            targetId={state.hold_target_id}
            codename={holdTarget?.codename}
            tnpId={state.hold_tnp_id}
          />
        </div>

        {/* Right column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6, overflow: 'hidden', minHeight: 0 }}>
          <AgentMesh agents={state.agents} />
          <SeismoPanel events={state.recent_collection} />
          <OperatorChat
            input={operatorInput}
            setInput={setOperatorInput}
            transmit={transmit}
            sending={sending}
            messages={messages}
            cycleId={state.cycle_id}
            activeTarget={state.active_target_codename}
          />
        </div>
      </div>
    </div>
  )
}
