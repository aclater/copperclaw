import type { CommanderLogEntry } from '../types'

interface DecisionLogProps {
  entries: CommanderLogEntry[]
}

const AGENT_STYLE: Record<string, { bg: string; color: string }> = {
  ISR:   { bg: 'var(--green-bg)',  color: 'var(--green)' },
  J2:    { bg: 'var(--blue-bg)',   color: 'var(--blue)'  },
  LEGAL: { bg: 'var(--green-bg)',  color: 'var(--green)' },
  CMD:   { bg: 'var(--amber-bg)',  color: 'var(--amber)' },
  EXEC:  { bg: 'var(--red-bg)',    color: 'var(--red)'   },
  BDA:   { bg: 'var(--blue-bg)',   color: 'var(--blue)'  },
}

const DEFAULT_STYLE = { bg: 'var(--border-dim)', color: 'var(--text-secondary)' }

export function DecisionLog({ entries }: DecisionLogProps) {
  const last4 = entries.slice(-4)

  return (
    <div style={{
      background: 'var(--bg-panel)',
      border: '1px solid var(--border)',
      borderRadius: 6,
      padding: '8px 10px',
      display: 'flex',
      flexDirection: 'column',
      gap: 6,
    }}>
      <div style={{ fontSize: 9, color: 'var(--text-dim)', letterSpacing: '0.08em', marginBottom: 2 }}>
        DECISION LOG
      </div>
      {last4.map((entry, i) => {
        const style = AGENT_STYLE[entry.agent] ?? DEFAULT_STYLE
        return (
          <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 6 }}>
            <div style={{
              width: 48,
              fontSize: 9,
              color: 'var(--text-dim)',
              fontVariantNumeric: 'tabular-nums',
              flexShrink: 0,
              paddingTop: 1,
            }}>
              {entry.timestamp_zulu}
            </div>
            <div style={{
              fontSize: 9,
              background: style.bg,
              color: style.color,
              border: `1px solid ${style.bg}`,
              borderRadius: 10,
              padding: '1px 6px',
              flexShrink: 0,
              lineHeight: 1.4,
            }}>
              {entry.agent}
            </div>
            <div style={{
              fontSize: 10,
              color: 'var(--text-secondary)',
              lineHeight: 1.4,
              flex: 1,
            }}>
              {entry.message}
            </div>
          </div>
        )
      })}
    </div>
  )
}
