import type { PirSatisfaction, CollectionEvent } from '../types'

interface CcirPanelProps {
  pirs: PirSatisfaction[]
  recentCollection: CollectionEvent[]
}

const SOURCE_COLOR: Record<string, string> = {
  SIGINT:   '#f85149',
  IMINT:    '#d29922',
  HUMINT:   '#3fb950',
  ACOUSTIC: '#8b949e',
  COT:      '#58a6ff',
}

const STATUS_COLOR: Record<string, string> = {
  GREEN: '#3fb950',
  AMBER: '#d29922',
  RED:   '#f85149',
}

const STATUS_LABEL: Record<string, string> = {
  GREEN: 'SATISFIED',
  AMBER: 'BUILDING',
  RED:   'CRITICAL',
}

const PIR_TARGET_MAP: Record<string, string> = {
  'PIR-001': 'TGT-ECHO-001',
  'PIR-002': 'TGT-ECHO-002',
  'PIR-003': 'TGT-GAMMA-001',
  'PIR-004': 'TGT-DELTA-001',
}

export function CcirPanel({ pirs, recentCollection }: CcirPanelProps) {
  return (
    <div style={{
      background: 'var(--bg-panel)',
      border: '1px solid var(--border)',
      borderRadius: 6,
      padding: '8px 10px',
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

      {pirs.map(pir => {
        const targetId = PIR_TARGET_MAP[pir.pir_id]
        const cues = recentCollection.filter(e => e.target_id === targetId)
        const statusColor = STATUS_COLOR[pir.status] ?? '#8b949e'
        const statusLabel = STATUS_LABEL[pir.status] ?? pir.status

        return (
          <div key={pir.pir_id} style={{ marginBottom: 10 }}>
            {/* PIR header row */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
              <div style={{ width: 36, fontSize: 9, color: 'var(--text-secondary)', flexShrink: 0 }}>
                {pir.pir_id}
              </div>
              <div style={{ flex: 1, position: 'relative', height: 6 }}>
                {/* Track */}
                <div style={{
                  position: 'absolute',
                  inset: 0,
                  background: 'var(--border)',
                  borderRadius: 3,
                  overflow: 'hidden',
                }}>
                  {/* Fill */}
                  <div style={{
                    width: `${pir.satisfaction_pct}%`,
                    height: '100%',
                    background: statusColor,
                    borderRadius: 3,
                    transition: 'width 0.6s ease',
                  }} />
                </div>
                {/* Threshold marker */}
                <div style={{
                  position: 'absolute',
                  top: 0, bottom: 0,
                  left: `${pir.threshold_pct}%`,
                  width: 1,
                  background: '#30363d',
                }} />
              </div>
              {/* Status badge */}
              <div style={{
                fontSize: 7,
                color: statusColor,
                border: `1px solid ${statusColor}`,
                borderRadius: 10,
                padding: '0 4px',
                flexShrink: 0,
                letterSpacing: '0.05em',
              }}>
                {statusLabel}
              </div>
            </div>

            {/* Collection cue chips */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, paddingLeft: 42 }}>
              {cues.length === 0 ? (
                <span style={{
                  fontSize: 8,
                  color: '#30363d',
                  fontStyle: 'italic',
                }}>
                  no collection
                </span>
              ) : cues.map(ev => {
                const color = SOURCE_COLOR[ev.source_type] ?? '#8b949e'
                const delta = Math.round((ev.confidence_weight / 10) * 15 + 2)
                return (
                  <div key={ev.id} style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 3,
                    background: '#0d1117',
                    border: '1px solid #21262d',
                    borderRadius: 10,
                    padding: '1px 5px',
                  }}>
                    <div style={{
                      width: 4, height: 4, borderRadius: '50%',
                      background: color, flexShrink: 0,
                    }} />
                    <span style={{ fontSize: 7, color: '#8b949e' }}>
                      {ev.source_type}
                    </span>
                    <span style={{ fontSize: 7, color: color }}>
                      +{delta}%
                    </span>
                  </div>
                )
              })}
            </div>
          </div>
        )
      })}
    </div>
  )
}
