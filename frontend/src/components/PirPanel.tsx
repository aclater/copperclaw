import type { PirSatisfaction } from '../types'

interface PirPanelProps {
  pirs: PirSatisfaction[]
}

const STATUS_COLOR: Record<string, string> = {
  GREEN: 'var(--green)',
  AMBER: 'var(--amber)',
  RED:   'var(--red)',
}

export function PirPanel({ pirs }: PirPanelProps) {
  return (
    <div style={{
      background: 'var(--bg-panel)',
      border: '1px solid var(--border)',
      borderRadius: 6,
      padding: '10px',
    }}>
      <div style={{
        fontSize: 9,
        color: 'var(--text-secondary)',
        letterSpacing: '0.1em',
        textTransform: 'uppercase',
        marginBottom: 8,
      }}>
        Intel requirements
      </div>
      {pirs.map(pir => (
        <div key={pir.pir_id} style={{
          display: 'flex',
          alignItems: 'center',
          gap: 6,
          marginBottom: 6,
        }}>
          <div style={{ width: 36, fontSize: 9, color: 'var(--text-secondary)', flexShrink: 0 }}>
            {pir.pir_id}
          </div>
          <div style={{
            flex: 1,
            height: 5,
            background: 'var(--border)',
            borderRadius: 3,
            overflow: 'hidden',
          }}>
            <div style={{
              width: `${pir.satisfaction_pct}%`,
              height: '100%',
              background: STATUS_COLOR[pir.status] ?? 'var(--idle)',
              borderRadius: 3,
              transition: 'width 0.6s ease',
            }} />
          </div>
          <div style={{ width: 26, fontSize: 9, color: STATUS_COLOR[pir.status], textAlign: 'right', flexShrink: 0 }}>
            {pir.satisfaction_pct}%
          </div>
        </div>
      ))}
    </div>
  )
}
