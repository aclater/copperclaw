interface ConfidenceRingProps {
  pct: number
  label: string
  sublabel: string
  color: string
}

const R = 32
const CIRC = 2 * Math.PI * R  // ~201

export function ConfidenceRing({ pct, label, sublabel, color }: ConfidenceRingProps) {
  const filled = (pct / 100) * CIRC
  const gap = CIRC - filled

  return (
    <div style={{
      background: 'var(--bg-panel)',
      border: '1px solid var(--border)',
      borderRadius: 6,
      padding: '10px',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
    }}>
      <svg width={80} height={80} viewBox="0 0 80 80">
        {/* background ring */}
        <circle cx={40} cy={40} r={R} fill="none" stroke="#21262d" strokeWidth={6} />
        {/* progress ring */}
        <circle
          cx={40} cy={40} r={R}
          fill="none"
          stroke={color}
          strokeWidth={6}
          strokeLinecap="round"
          strokeDasharray={`${filled} ${gap}`}
          transform="rotate(-90 40 40)"
        />
        <text x={40} y={37} textAnchor="middle" fill="var(--text-primary)"
          fontSize={18} fontWeight={500} fontFamily="var(--font-mono)">
          {pct}
        </text>
        <text x={40} y={50} textAnchor="middle" fill="var(--text-secondary)"
          fontSize={8} fontFamily="var(--font-mono)">
          {label}
        </text>
      </svg>
      <div style={{ fontSize: 8, color: 'var(--text-secondary)', marginTop: 2, textAlign: 'center' }}>
        {sublabel}
      </div>
    </div>
  )
}
