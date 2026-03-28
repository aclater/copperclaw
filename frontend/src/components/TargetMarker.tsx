import type { TargetConfig } from '../config/targets'
import type { TargetState, CyclePhase } from '../types'

interface TargetMarkerProps {
  config: TargetConfig
  state?: TargetState
}

const PHASE_COLOR: Record<CyclePhase, string> = {
  HOLD:     '#d29922',
  FIND:     '#f85149',
  FIX:      '#f85149',
  FINISH:   '#d29922',
  EXPLOIT:  '#d29922',
  ASSESS:   '#58a6ff',
  DEVELOP:  '#58a6ff',
  COMPLETE: '#3fb950',
  IDLE:     '#30363d',
}

export function TargetMarker({ config, state }: TargetMarkerProps) {
  const phase: CyclePhase = state?.phase ?? 'FIND'
  const color = PHASE_COLOR[phase]
  const isHold = phase === 'HOLD'
  const codename = config.codename

  // Badge width based on codename length
  const badgeW = 52
  const badgeH = 16

  return (
    <g>
      {/* Badge */}
      <rect
        x={-badgeW / 2}
        y={-badgeH - 14}
        width={badgeW}
        height={badgeH}
        rx={2}
        fill={isHold ? '#2d1e00' : '#0d1117'}
        stroke={color}
        strokeWidth={1}
      />
      <text
        x={0}
        y={-14 - badgeH / 2 + 5}
        textAnchor="middle"
        fill={color}
        fontSize={8}
        fontFamily="var(--font-mono)"
        fontWeight={500}
      >
        {codename}
      </text>

      {/* Outer ring */}
      <circle
        r={10}
        fill="none"
        stroke={color}
        strokeWidth={1.5}
        style={isHold ? { animation: 'pulse-amber 2s infinite' } : undefined}
      />

      {/* Inner dot */}
      <circle r={3.5} fill={color} />

      {/* Phase label */}
      <text
        x={0}
        y={20}
        textAnchor="middle"
        fill="var(--text-secondary)"
        fontSize={8}
        fontFamily="var(--font-mono)"
      >
        {phase}
      </text>
    </g>
  )
}
