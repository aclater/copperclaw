import { useState } from 'react'
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

const SOURCE_TYPES = ['SIGINT', 'IMINT', 'HUMINT', 'ACOUSTIC', 'COT'] as const

const now = Date.now()
const MOCK_EVENTS: CollectionEvent[] = [
  { id: 'c1', source_type: 'SIGINT',   timestamp_zulu: new Date(now - 15 * 60000).toISOString(), confidence_weight: 6,  target_id: 'TGT-ECHO-001'  },
  { id: 'c2', source_type: 'IMINT',    timestamp_zulu: new Date(now - 8  * 60000).toISOString(), confidence_weight: 9,  target_id: 'TGT-ECHO-001'  },
  { id: 'c3', source_type: 'HUMINT',   timestamp_zulu: new Date(now - 32 * 60000).toISOString(), confidence_weight: 7,  target_id: 'TGT-ECHO-001'  },
  { id: 'c4', source_type: 'ACOUSTIC', timestamp_zulu: new Date(now - 55 * 60000).toISOString(), confidence_weight: 4,  target_id: 'TGT-GAMMA-002' },
  { id: 'c5', source_type: 'SIGINT',   timestamp_zulu: new Date(now - 90 * 60000).toISOString(), confidence_weight: 3,  target_id: 'TGT-ECHO-002'  },
  { id: 'c6', source_type: 'COT',      timestamp_zulu: new Date(now - 5  * 60000).toISOString(), confidence_weight: 5,  target_id: 'TGT-DELTA-001' },
  { id: 'c7', source_type: 'IMINT',    timestamp_zulu: new Date(now - 120* 60000).toISOString(), confidence_weight: 8,  target_id: 'TGT-GAMMA-001' },
  { id: 'c8', source_type: 'HUMINT',   timestamp_zulu: new Date(now - 60 * 60000).toISOString(), confidence_weight: 6,  target_id: 'TGT-ECHO-002'  },
  { id: 'c9', source_type: 'COT',      timestamp_zulu: new Date(now - 40 * 60000).toISOString(), confidence_weight: 4,  target_id: 'TGT-ECHO-001'  },
]

const TIME_LABELS = ['G+4:00', 'G+5:00', 'G+6:00', 'G+6:30', 'now']
const TIME_POSITIONS = [0, 25, 50, 75, 100]

function blipSize(weight: number): number {
  return Math.max(5, Math.min(15, (weight / 10) * 13 + 3))
}

function blipOpacity(weight: number): number {
  return 0.35 + (weight / 10) * 0.65
}

function blipLeft(timestamp: string): number {
  const ageMs = Date.now() - new Date(timestamp).getTime()
  const ageMin = ageMs / 60000
  return Math.max(0, Math.min(100, (1 - ageMin / 150) * 100))
}

export function SeismoPanel({ events }: SeismoPanelProps) {
  const [hovered, setHovered] = useState<string | null>(null)
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
      flex: '0 0 180px',
    }}>
      {/* Title */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
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
          <div key={srcType} style={{ display: 'flex', alignItems: 'center', gap: 4, marginBottom: 2 }}>
            <div style={{
              width: 52,
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
              height: 28,
            }}>
              {typeEvents.map(ev => {
                const leftPct = blipLeft(ev.timestamp_zulu)
                const size = blipSize(ev.confidence_weight)
                const opacity = blipOpacity(ev.confidence_weight)
                const color = SOURCE_COLOR[ev.source_type] ?? '#8b949e'
                const isHov = hovered === ev.id
                return (
                  <div
                    key={ev.id}
                    style={{
                      position: 'absolute',
                      left: `${leftPct}%`,
                      top: '50%',
                      transform: 'translate(-50%, -50%)',
                      width: size,
                      height: size,
                      borderRadius: '50%',
                      background: color,
                      opacity,
                      cursor: 'default',
                    }}
                    onMouseEnter={() => setHovered(ev.id)}
                    onMouseLeave={() => setHovered(null)}
                    title={`${ev.source_type} · conf ${Math.round(ev.confidence_weight * 10)}%`}
                  >
                    {isHov && (
                      <div style={{
                        position: 'absolute',
                        top: -18,
                        left: '50%',
                        transform: 'translateX(-50%)',
                        background: '#161b22',
                        border: '1px solid #21262d',
                        color: '#e6edf3',
                        fontSize: 8,
                        padding: '1px 5px',
                        borderRadius: 3,
                        whiteSpace: 'nowrap',
                        pointerEvents: 'none',
                        zIndex: 10,
                      }}>
                        {ev.source_type} · conf {Math.round(ev.confidence_weight * 10)}%
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        )
      })}

      {/* Time axis */}
      <div style={{
        position: 'relative',
        marginTop: 4,
        paddingLeft: 56,
        height: 16,
      }}>
        {TIME_LABELS.map((label, i) => (
          <div
            key={label}
            style={{
              position: 'absolute',
              left: `${TIME_POSITIONS[i]}%`,
              transform: 'translateX(-50%)',
              fontSize: 7,
              color: '#30363d',
              whiteSpace: 'nowrap',
            }}
          >
            {label}
          </div>
        ))}
      </div>

      {/* Footer */}
      <div style={{
        fontSize: 8,
        color: 'var(--text-dim)',
        borderTop: '1px solid var(--border-dim)',
        paddingTop: 4,
        marginTop: 2,
      }}>
        bubble size = confidence · hover for details
      </div>
    </div>
  )
}
