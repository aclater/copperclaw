import type { CollectionEvent } from '../types'

interface SeismoPanelProps {
  events: CollectionEvent[]
}

const SOURCE_COLOR: Record<string, string> = {
  SIGINT:   '#f85149',
  IMINT:    '#d29922',
  HUMINT:   '#3fb950',
  ACOUSTIC: '#8b949e',
  COT:      '#58a6ff',
}

const SOURCE_TYPES = ['SIGINT', 'IMINT', 'HUMINT', 'ACOUSTIC'] as const

const MOCK_EVENTS: CollectionEvent[] = [
  { id: 'c1', source_type: 'SIGINT',   timestamp_zulu: '', confidence_weight: 6, target_id: 'TGT-ECHO-001'  },
  { id: 'c2', source_type: 'IMINT',    timestamp_zulu: '', confidence_weight: 9, target_id: 'TGT-ECHO-001'  },
  { id: 'c3', source_type: 'HUMINT',   timestamp_zulu: '', confidence_weight: 7, target_id: 'TGT-ECHO-001'  },
  { id: 'c4', source_type: 'ACOUSTIC', timestamp_zulu: '', confidence_weight: 4, target_id: 'TGT-GAMMA-002' },
  { id: 'c5', source_type: 'SIGINT',   timestamp_zulu: '', confidence_weight: 3, target_id: 'TGT-ECHO-002'  },
]

export function SeismoPanel({ events }: SeismoPanelProps) {
  const isMock = !events || events.length === 0
  const displayEvents = isMock ? MOCK_EVENTS : events

  return (
    <div style={{
      background: 'var(--bg-panel)',
      border: '1px solid var(--border)',
      borderRadius: 6,
      padding: '8px 10px',
      display: 'flex',
      flexDirection: 'column',
      flex: '0 0 160px',
    }}>
      {/* Title */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
        <span style={{ fontSize: 9, color: 'var(--text-dim)', letterSpacing: '0.08em' }}>
          SENSOR FEED
        </span>
        <span style={{
          fontSize: 8,
          background: 'var(--blue-bg)',
          color: 'var(--blue)',
          border: '1px solid var(--blue-bdr)',
          borderRadius: 10,
          padding: '0 5px',
        }}>
          SEISMO
        </span>
        {isMock && (
          <span style={{
            fontSize: 8,
            background: 'var(--amber-bg)',
            color: 'var(--amber)',
            border: '1px solid var(--amber)',
            borderRadius: 10,
            padding: '0 5px',
          }}>
            sim
          </span>
        )}
      </div>

      {/* Rows per source type */}
      {SOURCE_TYPES.map(srcType => {
        const typeEvents = displayEvents.filter(e => e.source_type === srcType)
        return (
          <div key={srcType} style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
            <div style={{
              width: 36,
              fontSize: 8,
              color: 'var(--text-dim)',
              textAlign: 'right',
              flexShrink: 0,
            }}>
              {srcType}
            </div>
            <div style={{
              flex: 1,
              position: 'relative',
              height: 18,
            }}>
              {typeEvents.map((ev, idx) => {
                const leftPct = 10 + (idx / Math.max(typeEvents.length - 1, 1)) * 80
                const size = (ev.confidence_weight / 10) * 12 + 3
                const color = SOURCE_COLOR[ev.source_type] ?? 'var(--text-dim)'
                return (
                  <div
                    key={ev.id}
                    title={`${ev.source_type} — weight ${ev.confidence_weight} — ${ev.target_id ?? 'unknown'}`}
                    style={{
                      position: 'absolute',
                      left: `${leftPct}%`,
                      top: '50%',
                      transform: 'translate(-50%, -50%)',
                      width: size,
                      height: size,
                      borderRadius: '50%',
                      background: color,
                      opacity: 0.75,
                    }}
                  />
                )
              })}
            </div>
          </div>
        )
      })}

      {/* Footer */}
      <div style={{
        fontSize: 8,
        color: 'var(--text-dim)',
        borderTop: '1px solid var(--border-dim)',
        paddingTop: 4,
        marginTop: 2,
      }}>
        ← earlier · now →&nbsp;&nbsp;bubble size = confidence
      </div>
    </div>
  )
}
