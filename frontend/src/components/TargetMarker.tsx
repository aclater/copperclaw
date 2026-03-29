import type { TargetConfig } from '../config/targets'
import type { TargetState } from '../types'
import type { TargetPosition } from '../hooks/useTargetPositions'

export interface TargetMarkerProps {
  config: TargetConfig
  state?: TargetState
  position: TargetPosition
  isSelected?: boolean
}

// Badge width — sized to codename, min 52px
const badgeW = (name: string) => Math.max(52, name.length * 6 + 14)
const badgeH = 16

// ── Visual state machine ────────────────────────────────────────────────────
type VisualState =
  | 'NEUTRALIZED'
  | 'CAPTURED'
  | 'PARTIAL_EFFECT'
  | 'REENGAGEMENT_REQUIRED'
  | 'EXECUTING'
  | 'BDA_IN_PROGRESS'
  | 'CONFIRMED'
  | 'HOLD'
  | 'MOVING'
  | 'DEFAULT'

function resolveVisualState(
  state: TargetState | undefined,
  config: TargetConfig,
  position: TargetPosition,
): VisualState {
  const outcome = state?.outcome
  const phase = state?.phase ?? 'FIND'
  const isMoving = config.mobility === 'HIGH' && position.uncertainty > 0.3

  if (outcome === 'NEUTRALIZED')            return 'NEUTRALIZED'
  if (outcome === 'CAPTURED')               return 'CAPTURED'
  if (outcome === 'PARTIAL_EFFECT')         return 'PARTIAL_EFFECT'
  if (outcome === 'REENGAGEMENT_REQUIRED')  return 'REENGAGEMENT_REQUIRED'
  if (phase === 'FINISH')                   return 'EXECUTING'
  if (phase === 'ASSESS')                   return 'BDA_IN_PROGRESS'
  if (position.isConfirmed)                 return 'CONFIRMED'
  if (phase === 'HOLD')                     return 'HOLD'
  if (isMoving)                             return 'MOVING'
  return 'DEFAULT'
}

// ── Sub-components ──────────────────────────────────────────────────────────

function Badge({
  codename,
  color,
  bg,
  italic = false,
  opacity = 1,
}: {
  codename: string
  color: string
  bg: string
  italic?: boolean
  opacity?: number
}) {
  const bw = badgeW(codename)
  return (
    <g opacity={opacity}>
      <rect
        x={-bw / 2}
        y={-badgeH - 14}
        width={bw}
        height={badgeH}
        rx={2}
        fill={bg}
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
        fontStyle={italic ? 'italic' : 'normal'}
      >
        {codename}
      </text>
    </g>
  )
}

function PhaseLabel({ label, color }: { label: string; color: string }) {
  return (
    <text
      x={0}
      y={20}
      textAnchor="middle"
      fill={color}
      fontSize={8}
      fontFamily="var(--font-mono)"
    >
      {label}
    </text>
  )
}

// ── Main component ──────────────────────────────────────────────────────────
export function TargetMarker({ config, state, position, isSelected = false }: TargetMarkerProps) {
  const vs = resolveVisualState(state, config, position)
  const { trail } = position
  const codename = config.codename

  // ── Selection ring overlay ─────────────────────────────────────────────
  const selectionRing = isSelected ? (
    <circle
      r={14}
      fill="none"
      stroke="#58a6ff"
      strokeWidth={2.5}
      className="tgt-selected-ring"
      style={{ filter: 'drop-shadow(0 0 3px rgba(88,166,255,0.25))' }}
    />
  ) : null

  // ── NEUTRALIZED ghost ─────────────────────────────────────────────────
  if (vs === 'NEUTRALIZED') {
    return (
      <g opacity={0.4}>
        {selectionRing}
        <Badge codename={codename} color="#484f57" bg="#161b22" />
        <circle r={10} fill="none" stroke="#484f57" strokeWidth={1.5} strokeDasharray="3 3" />
        <line x1={-4} y1={-4} x2={4} y2={4} stroke="#484f57" strokeWidth={1.5} />
        <line x1={4} y1={-4} x2={-4} y2={4} stroke="#484f57" strokeWidth={1.5} />
        <PhaseLabel label="NEUTRALIZED" color="#484f57" />
      </g>
    )
  }

  // ── CAPTURED — DOMEX pulse ────────────────────────────────────────────
  if (vs === 'CAPTURED') {
    return (
      <g>
        {selectionRing}
        <Badge codename={codename} color="#d29922" bg="#2d1e00" />
        {/* Expanding DOMEX ring */}
        <circle fill="none" stroke="#d29922" strokeWidth={1.5}>
          <animate attributeName="r" values="10;28" dur="1.8s" repeatCount="indefinite" />
          <animate attributeName="opacity" values="0.8;0" dur="1.8s" repeatCount="indefinite" />
        </circle>
        {/* Static base ring */}
        <circle r={10} fill="none" stroke="#d29922" strokeWidth={2} />
        <circle r={3.5} fill="#d29922" />
        <text
          x={0}
          y={-6}
          textAnchor="middle"
          fill="#d29922"
          fontSize={6}
          fontFamily="var(--font-mono)"
          fontWeight={700}
        >
          DOMEX
        </text>
        <PhaseLabel label="CAPTURED" color="#d29922" />
      </g>
    )
  }

  // ── PARTIAL_EFFECT — dimmed amber, half-arc ring ──────────────────────
  if (vs === 'PARTIAL_EFFECT') {
    // Half circumference ≈ 31.4 of total ≈ 62.8
    return (
      <g opacity={0.65}>
        {selectionRing}
        <Badge codename={codename} color="#d29922" bg="#2d1e00" />
        <circle r={10} fill="none" stroke="#d29922" strokeWidth={2} strokeDasharray="31 32" />
        <circle r={3.5} fill="#d29922" opacity={0.5} />
        <PhaseLabel label="PARTIAL" color="#d29922" />
      </g>
    )
  }

  // ── REENGAGEMENT_REQUIRED — rapid red blink ───────────────────────────
  if (vs === 'REENGAGEMENT_REQUIRED') {
    return (
      <g>
        {selectionRing}
        <Badge codename={codename} color="#f85149" bg="#2d0e0d" />
        <circle r={10} fill="none" stroke="#f85149" strokeWidth={2}>
          <animate attributeName="opacity" values="1;0;1" dur="0.5s" repeatCount="indefinite" />
        </circle>
        <circle r={3.5} fill="#f85149">
          <animate attributeName="opacity" values="1;0;1" dur="0.5s" repeatCount="indefinite" />
        </circle>
        <PhaseLabel label="REENGAGEMENT" color="#f85149" />
      </g>
    )
  }

  // ── EXECUTING — expanding ring, blinking dot, × glyph ────────────────
  if (vs === 'EXECUTING') {
    return (
      <g>
        {selectionRing}
        <Badge codename={codename} color="#f85149" bg="#2d0e0d" />
        <circle r={14} fill="none" stroke="#f85149" strokeWidth={2} />
        <circle r={3.5} fill="#f85149">
          <animate attributeName="opacity" values="1;0;1" dur="0.3s" repeatCount="indefinite" />
        </circle>
        {/* × glyph */}
        <line x1={-3} y1={-3} x2={3} y2={3} stroke="#f85149" strokeWidth={1.5} />
        <line x1={3} y1={-3} x2={-3} y2={3} stroke="#f85149" strokeWidth={1.5} />
        <PhaseLabel label="EXECUTING" color="#f85149" />
      </g>
    )
  }

  // ── BDA_IN_PROGRESS — blue pulsing ring ───────────────────────────────
  if (vs === 'BDA_IN_PROGRESS') {
    return (
      <g>
        {selectionRing}
        <Badge codename={codename} color="#58a6ff" bg="#0d1f3c" />
        <circle r={10} fill="none" stroke="#58a6ff" strokeWidth={2}>
          <animate attributeName="opacity" values="1;0.3;1" dur="1.5s" repeatCount="indefinite" />
        </circle>
        <circle r={3.5} fill="#58a6ff" />
        <PhaseLabel label="BDA" color="#58a6ff" />
      </g>
    )
  }

  // ── CONFIRMED snap — ring at r=14, green tint, "CONFIRMED" label ──────
  if (vs === 'CONFIRMED') {
    return (
      <g>
        {selectionRing}
        <Badge codename={codename} color="#3fb950" bg="#0d2010" />
        {/* Ring animates from 14 back to 10 over 400ms */}
        <circle
          fill="none"
          stroke="#3fb950"
          strokeWidth={2}
          style={{ transition: 'r 0.4s ease-out' } as React.CSSProperties}
        >
          <animate attributeName="r" values="14;10" dur="0.4s" fill="freeze" />
        </circle>
        <circle r={3.5} fill="#3fb950" />
        <PhaseLabel label="CONFIRMED" color="#3fb950" />
      </g>
    )
  }

  // ── HOLD — amber ring with SVG pulse ─────────────────────────────────
  if (vs === 'HOLD') {
    return (
      <g>
        {selectionRing}
        <Badge codename={codename} color="#d29922" bg="#2d1e00" />
        <circle r={10} fill="none" stroke="#d29922" strokeWidth={2}>
          <animate attributeName="r" values="10;14;10" dur="2s" repeatCount="indefinite" />
          <animate attributeName="opacity" values="1;0.3;1" dur="2s" repeatCount="indefinite" />
        </circle>
        <circle r={3.5} fill="#d29922" />
        <PhaseLabel label="HOLD" color="#d29922" />
      </g>
    )
  }

  // ── MOVING — dashed ring, reduced opacity, trail, italic badge ────────
  if (vs === 'MOVING') {
    const { uncertainty } = position
    const ringOpacity = 1 - uncertainty * 0.5
    const trailSizes  = [5, 4, 3]
    const trailAlphas = [0.25, 0.15, 0.08]

    return (
      <g>
        {selectionRing}
        {/* Trail dots (rendered behind marker) */}
        {trail.map((pt, i) => (
          <circle
            key={i}
            cx={pt.dx}
            cy={pt.dy}
            r={trailSizes[i] ?? 3}
            fill="#f85149"
            opacity={trailAlphas[i] ?? 0.08}
          />
        ))}
        <Badge codename={codename} color="#f85149" bg="#2d0e0d" italic opacity={ringOpacity} />
        <circle
          r={10}
          fill="none"
          stroke="#f85149"
          strokeWidth={2}
          strokeDasharray="4 3"
          opacity={ringOpacity}
        />
        <circle r={3.5} fill="#f85149" opacity={ringOpacity} />
        <PhaseLabel label="MOVING" color="#8b949e" />
      </g>
    )
  }

  // ── DEFAULT — FIND / FIX active tracking ─────────────────────────────
  const phase = state?.phase ?? 'FIND'
  const PHASE_COLOR: Record<string, string> = {
    FIND:    '#f85149',
    FIX:     '#f85149',
    FINISH:  '#d29922',
    EXPLOIT: '#d29922',
    ASSESS:  '#58a6ff',
    DEVELOP: '#58a6ff',
    COMPLETE:'#3fb950',
    IDLE:    '#30363d',
    HOLD:    '#d29922',
  }
  const color  = PHASE_COLOR[phase] ?? '#f85149'
  const badgeBg = phase === 'FIND' || phase === 'FIX' ? '#2d0e0d' : '#0d1117'

  return (
    <g>
      {selectionRing}
      <Badge codename={codename} color={color} bg={badgeBg} />
      <circle r={10} fill="none" stroke={color} strokeWidth={2} />
      <circle r={3.5} fill={color} />
      <PhaseLabel label={phase} color="#8b949e" />
    </g>
  )
}
