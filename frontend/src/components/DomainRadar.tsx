const DOMAINS = ['Land', 'EM', 'Info', 'Cyber', 'Air', 'CBRN']

const COMPONENTS = [
  {
    name: 'GAMMA',
    color: '#f85149',
    values: [0.90, 0.75, 0.20, 0.15, 0.30, 0.10],
    fillOpacity: 0.12,
    strokeOpacity: 0.6,
  },
  {
    name: 'DELTA',
    color: '#d29922',
    values: [0.40, 0.35, 0.70, 0.55, 0.20, 0.15],
    fillOpacity: 0.12,
    strokeOpacity: 0.6,
  },
  {
    name: 'ECHO',
    color: '#58a6ff',
    values: [0.45, 0.25, 0.60, 0.35, 0.10, 0.05],
    fillOpacity: 0.10,
    strokeOpacity: 0.5,
  },
]

const CX = 100
const CY = 100
const RADIUS = 60

function polarPoint(domainIdx: number, scale: number): [number, number] {
  const angleDeg = -90 + domainIdx * 60
  const angleRad = (angleDeg * Math.PI) / 180
  return [
    CX + scale * RADIUS * Math.cos(angleRad),
    CY + scale * RADIUS * Math.sin(angleRad),
  ]
}

function hexPath(scale: number): string {
  return DOMAINS.map((_, i) => {
    const [x, y] = polarPoint(i, scale)
    return `${i === 0 ? 'M' : 'L'} ${x.toFixed(2)},${y.toFixed(2)}`
  }).join(' ') + ' Z'
}

function componentPath(values: number[]): string {
  return values.map((v, i) => {
    const [x, y] = polarPoint(i, v)
    return `${i === 0 ? 'M' : 'L'} ${x.toFixed(2)},${y.toFixed(2)}`
  }).join(' ') + ' Z'
}

export function DomainRadar() {
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
        marginBottom: 6,
      }}>
        Domain activity
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <svg viewBox="0 0 200 200" width={120} height={120} style={{ flexShrink: 0 }}>
          {/* Concentric grid hexagons */}
          {[0.15, 0.30, 0.60, 1.0].map(scale => (
            <path
              key={scale}
              d={hexPath(scale)}
              fill="none"
              stroke="#21262d"
              strokeWidth={0.5}
            />
          ))}

          {/* Axis lines */}
          {DOMAINS.map((_, i) => {
            const [x, y] = polarPoint(i, 1.0)
            return (
              <line
                key={i}
                x1={CX} y1={CY}
                x2={x.toFixed(2)} y2={y.toFixed(2)}
                stroke="#21262d"
                strokeWidth={0.5}
              />
            )
          })}

          {/* Axis labels */}
          {DOMAINS.map((label, i) => {
            const [x, y] = polarPoint(i, 1.18)
            return (
              <text
                key={label}
                x={x.toFixed(2)}
                y={y.toFixed(2)}
                textAnchor="middle"
                dominantBaseline="middle"
                fill="#30363d"
                fontSize={7}
                fontFamily="var(--font-mono)"
              >
                {label}
              </text>
            )
          })}

          {/* Component polygons */}
          {COMPONENTS.map(comp => (
            <path
              key={comp.name}
              d={componentPath(comp.values)}
              fill={comp.color}
              fillOpacity={comp.fillOpacity}
              stroke={comp.color}
              strokeOpacity={comp.strokeOpacity}
              strokeWidth={1}
            />
          ))}
        </svg>

        {/* Legend */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          {COMPONENTS.map(comp => (
            <div key={comp.name} style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
              <div style={{
                width: 8, height: 8, borderRadius: 1,
                background: comp.color,
                opacity: 0.7,
              }} />
              <span style={{ fontSize: 8, color: '#8b949e' }}>{comp.name}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
