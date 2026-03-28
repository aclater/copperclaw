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

function formatTimestamp(ts: string): string {
  // If already has seconds (HH:MM:SSZ), return as-is
  // If HH:MMZ format, insert :00
  if (/^\d{2}:\d{2}:\d{2}Z?$/.test(ts)) return ts
  // Try parsing as ISO or partial
  const match = ts.match(/^(\d{2}:\d{2})Z?$/)
  if (match) return `${match[1]}:00Z`
  return ts
}

export function DecisionLog({ entries }: DecisionLogProps) {
  const last6 = entries.slice(-6)
  const hasMore = entries.length > 6

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
      {last6.map((entry, i) => {
        const style = AGENT_STYLE[entry.agent] ?? DEFAULT_STYLE
        return (
          <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 6 }}>
            <div style={{
              width: 54,
              fontSize: 9,
              color: 'var(--text-dim)',
              fontVariantNumeric: 'tabular-nums',
              flexShrink: 0,
              paddingTop: 1,
            }}>
              {formatTimestamp(entry.timestamp_zulu)}
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
              overflow: 'hidden',
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
            } as React.CSSProperties}>
              {entry.message}
            </div>
          </div>
        )
      })}
      {hasMore && (
        <div style={{ fontSize: 8, color: '#30363d', textAlign: 'right' }}>
          scroll to see more
        </div>
      )}
    </div>
  )
}
