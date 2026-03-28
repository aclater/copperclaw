interface CycleTimerProps {
  elapsed_seconds: number
}

const BASELINE = 10800  // 3 hours in seconds

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}:${String(s).padStart(2, '0')}`
}

export function CycleTimer({ elapsed_seconds }: CycleTimerProps) {
  const improvement = Math.min(99, Math.round((1 - elapsed_seconds / BASELINE) * 100))

  return (
    <div style={{
      background: 'var(--bg-panel)',
      border: '1px solid var(--border)',
      borderRadius: 6,
      padding: '10px',
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      gap: 8,
    }}>
      {/* Elapsed time */}
      <div>
        <div style={{ fontSize: 22, fontWeight: 500, color: 'var(--green)', lineHeight: 1 }}>
          {formatTime(elapsed_seconds)}
        </div>
        <div style={{ fontSize: 9, color: 'var(--text-secondary)', marginTop: 4 }}>
          Find → legal cleared
        </div>
      </div>

      {/* Improvement vs baseline */}
      <div style={{ textAlign: 'right' }}>
        <div style={{ fontSize: 9, color: 'var(--text-dim)', marginBottom: 2 }}>
          vs baseline
        </div>
        <div style={{ fontSize: 14, color: 'var(--green)', fontWeight: 500 }}>
          {improvement > 0 ? '+' : ''}{improvement}%
        </div>
        <div style={{ fontSize: 8, color: 'var(--text-dim)' }}>
          faster
        </div>
      </div>
    </div>
  )
}
