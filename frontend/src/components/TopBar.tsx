import { useState, useEffect } from 'react'
import type { CycleState } from '../types'

interface TopBarProps {
  state: CycleState
  connected: boolean
}

function utcClock(): string {
  return new Date().toISOString().slice(11, 19) + 'Z'
}

export function TopBar({ state, connected }: TopBarProps) {
  const [clock, setClock] = useState(utcClock)

  useEffect(() => {
    const t = setInterval(() => setClock(utcClock()), 1000)
    return () => clearInterval(t)
  }, [])

  const activeAgents = state.agents.filter(a => a.status !== 'IDLE').length

  return (
    <div style={{
      height: 38,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 12px',
      borderBottom: '1px solid var(--border)',
      background: 'var(--bg-panel)',
    }}>
      {/* Left: title */}
      <div>
        <span style={{ fontSize: 13, fontWeight: 500, color: 'var(--text-primary)' }}>
          Operation Copperclaw
        </span>
        <span style={{ fontSize: 10, color: 'var(--text-secondary)', marginLeft: 12 }}>
          TF Kestrel // AO Harrow // G+7
        </span>
      </div>

      {/* Right: chips + clock */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        {state.awaiting_commander && (
          <Chip label="Commander hold" color="amber" />
        )}
        {state.phase !== 'IDLE' && (
          <Chip label="Cycle active" color="green" />
        )}
        <Chip label={`${activeAgents} services`} color="green" />
        {connected && <Chip label="SSE live" color="green" />}
        <div style={{ fontSize: 10, color: 'var(--text-secondary)', marginLeft: 6, fontVariantNumeric: 'tabular-nums' }}>
          {clock}
        </div>
      </div>
    </div>
  )
}

function Chip({ label, color }: { label: string; color: 'amber' | 'green' | 'red' }) {
  const styles = {
    amber: { bg: 'var(--amber-bg)', border: 'var(--amber-bdr)', text: 'var(--amber)' },
    green: { bg: 'var(--green-bg)', border: 'var(--green-bdr)', text: 'var(--green)' },
    red:   { bg: 'var(--red-bg)',   border: 'var(--red-bdr)',   text: 'var(--red)'   },
  }[color]

  return (
    <span style={{
      fontSize: 10,
      padding: '2px 8px',
      borderRadius: 3,
      background: styles.bg,
      border: `1px solid ${styles.border}`,
      color: styles.text,
    }}>
      {label}
    </span>
  )
}
