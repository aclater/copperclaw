import type { AgentState, AgentStatus } from '../types'

interface AgentMeshProps {
  agents: AgentState[]
}

const DOT_COLOR: Record<AgentStatus, string> = {
  ACTIVE: 'var(--green)',
  HOLD:   'var(--amber)',
  IDLE:   'var(--idle)',
  ERROR:  'var(--red)',
}

const DETAIL_COLOR: Record<AgentStatus, string> = {
  ACTIVE: 'var(--text-secondary)',
  HOLD:   'var(--amber)',
  IDLE:   'var(--text-dim)',
  ERROR:  'var(--red)',
}

export function AgentMesh({ agents }: AgentMeshProps) {
  return (
    <div style={{
      background: 'var(--bg-panel)',
      border: '1px solid var(--border)',
      borderRadius: 6,
      padding: '8px 10px',
    }}>
      {/* Title row */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
        <span style={{ fontSize: 9, color: 'var(--text-dim)', letterSpacing: '0.08em' }}>
          AI AGENT STATUS
        </span>
        <span style={{
          fontSize: 8,
          background: 'var(--green-bg)',
          color: 'var(--green)',
          border: '1px solid var(--green-bdr)',
          borderRadius: 10,
          padding: '0 5px',
        }}>
          LIVE
        </span>
      </div>

      {agents.map(agent => {
        const isCommanderHold = agent.name === 'commander' && agent.status === 'HOLD'
        return (
          <div key={agent.name} style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            marginBottom: 4,
          }}>
            {/* Status dot */}
            <div style={{
              width: 6,
              height: 6,
              borderRadius: '50%',
              background: DOT_COLOR[agent.status],
              flexShrink: 0,
              animation: agent.status === 'HOLD' ? 'blink 1.2s step-end infinite' : undefined,
            }} />

            {/* Name */}
            <div style={{
              width: 68,
              fontSize: 9,
              color: 'var(--text-secondary)',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
              flexShrink: 0,
            }}>
              {agent.name}
            </div>

            {/* Detail */}
            <div style={{
              flex: 1,
              fontSize: 9,
              color: isCommanderHold ? 'var(--amber)' : DETAIL_COLOR[agent.status],
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
              fontWeight: isCommanderHold ? 500 : undefined,
            }}>
              {agent.detail}
            </div>
          </div>
        )
      })}
    </div>
  )
}
