interface MetricCardProps {
  value: string | number
  label: string
  sub?: string
  color?: string
}

export function MetricCard({ value, label, sub, color }: MetricCardProps) {
  return (
    <div style={{
      background: 'var(--bg-panel)',
      border: '1px solid var(--border)',
      borderRadius: 6,
      padding: '12px 10px',
      textAlign: 'center',
    }}>
      <div style={{
        fontSize: 32,
        fontWeight: 500,
        color: color ?? 'var(--text-primary)',
        lineHeight: 1.1,
      }}>
        {value}
      </div>
      <div style={{
        fontSize: 9,
        color: 'var(--text-secondary)',
        letterSpacing: '0.1em',
        textTransform: 'uppercase',
        marginTop: 4,
      }}>
        {label}
      </div>
      {sub && (
        <div style={{ fontSize: 10, color: 'var(--text-secondary)', marginTop: 2 }}>
          {sub}
        </div>
      )}
    </div>
  )
}
