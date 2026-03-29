import { useState, useEffect, useRef } from 'react'
import type { TargetState, TargetId } from '../types'
import type { TargetConfig } from '../config/targets'

export interface TargetPosition {
  x: number
  y: number
  uncertainty: number    // 0-1
  isConfirmed: boolean
  lastConfirmedAt: number // Date.now() timestamp
  trail: Array<{ dx: number; dy: number }> // relative offsets from current x,y
}

/** Deterministic integer hash of a string — used to seed per-target drift. */
function hashStr(s: string): number {
  let h = 0
  for (let i = 0; i < s.length; i++) {
    h = (Math.imul(31, h) + s.charCodeAt(i)) | 0
  }
  return h >>> 0
}

export function useTargetPositions(
  targets: TargetState[],
  configs: TargetConfig[]
): Map<TargetId, TargetPosition> {
  // Absolute position store — mutated in place, never replaced
  const posRef = useRef<Map<TargetId, TargetPosition>>(new Map())
  // Absolute trail history — last 3 positions before the current one
  const trailAbsRef = useRef<Map<TargetId, Array<{ x: number; y: number }>>>(new Map())
  // Previous last_confirmed_zulu per target — for snap detection
  const prevZuluRef = useRef<Map<TargetId, string | undefined>>(new Map())
  // Keep latest targets/configs accessible inside intervals without re-creating them
  const targetsRef = useRef(targets)
  const configsRef = useRef(configs)
  const [, setTick] = useState(0)

  useEffect(() => { targetsRef.current = targets }, [targets])
  useEffect(() => { configsRef.current = configs }, [configs])

  // Lazy-initialize positions for any config not yet in the map
  configs.forEach(cfg => {
    if (!posRef.current.has(cfg.id)) {
      posRef.current.set(cfg.id, {
        x: cfg.x, y: cfg.y,
        uncertainty: 0,
        isConfirmed: false,
        lastConfirmedAt: 0,
        trail: [],
      })
    }
    if (!trailAbsRef.current.has(cfg.id)) {
      trailAbsRef.current.set(cfg.id, [])
    }
  })

  // ── Snap on new collection report ──────────────────────────────────────
  useEffect(() => {
    targets.forEach(tgt => {
      const prev = prevZuluRef.current.get(tgt.target_id)
      const curr = tgt.last_confirmed_zulu
      if (curr && curr !== prev) {
        const cfg = configsRef.current.find(c => c.id === tgt.target_id)
        if (cfg) {
          posRef.current.set(tgt.target_id, {
            x: cfg.x, y: cfg.y,
            uncertainty: 0,
            isConfirmed: true,
            lastConfirmedAt: Date.now(),
            trail: [],
          })
          trailAbsRef.current.set(tgt.target_id, [])
          setTick(t => t + 1)

          // Clear isConfirmed flag after 2 seconds
          setTimeout(() => {
            const pos = posRef.current.get(tgt.target_id)
            if (pos?.isConfirmed) {
              posRef.current.set(tgt.target_id, { ...pos, isConfirmed: false })
              setTick(t => t + 1)
            }
          }, 2000)
        }
      }
      prevZuluRef.current.set(tgt.target_id, curr)
    })
  }, [targets])

  // ── Drift timer — 2000ms tick ───────────────────────────────────────────
  useEffect(() => {
    const id = setInterval(() => {
      const now = Date.now()
      configsRef.current.forEach(cfg => {
        if (cfg.mobility === 'STATIC') return

        const pos = posRef.current.get(cfg.id)
        if (!pos) return

        // Stop drifting for destroyed/captured targets
        const tgt = targetsRef.current.find(t => t.target_id === cfg.id)
        const outcome = tgt?.outcome
        if (outcome === 'NEUTRALIZED' || outcome === 'CAPTURED') return

        // Push current position to absolute trail before updating
        const absTrail = trailAbsRef.current.get(cfg.id) ?? []
        absTrail.push({ x: pos.x, y: pos.y })
        if (absTrail.length > 3) absTrail.shift()
        trailAbsRef.current.set(cfg.id, absTrail)

        let newX = pos.x
        let newY = pos.y
        let newUncertainty = pos.uncertainty

        if (cfg.mobility === 'LOW') {
          if (pos.uncertainty < 0.3) {
            const dx = (Math.random() - 0.5) * 4  // ±2px
            const dy = (Math.random() - 0.5) * 4
            newX = Math.max(cfg.x - 8, Math.min(cfg.x + 8, pos.x + dx))
            newY = Math.max(cfg.y - 8, Math.min(cfg.y + 8, pos.y + dy))
            newUncertainty = Math.min(0.4, pos.uncertainty + 0.02)
          }
          // At or above 0.3 uncertainty, stop drifting but continue uncertainty growth
          newUncertainty = Math.min(0.4, newUncertainty)
        } else if (cfg.mobility === 'HIGH') {
          const hash = hashStr(cfg.id)
          // Derive per-target seeds as phase offsets in radians
          const seedX = ((hash & 0xffff) / 65535) * Math.PI * 2
          const seedY = (((hash >>> 16) & 0xffff) / 65535) * Math.PI * 2
          const dx = Math.sin(now / 3000 + seedX) * 4
          const dy = Math.cos(now / 4500 + seedY) * 4
          newX = Math.max(cfg.x - 20, Math.min(cfg.x + 20, pos.x + dx))
          newY = Math.max(cfg.y - 20, Math.min(cfg.y + 20, pos.y + dy))
          newUncertainty = Math.min(0.85, pos.uncertainty + 0.04)
        }

        // Build trail as relative offsets from new position
        const trail = absTrail.map(p => ({
          dx: p.x - newX,
          dy: p.y - newY,
        }))

        posRef.current.set(cfg.id, {
          ...pos,
          x: newX,
          y: newY,
          uncertainty: newUncertainty,
          trail,
        })
      })
      setTick(t => t + 1)
    }, 2000)

    return () => clearInterval(id)
  }, []) // intentionally empty — uses refs for live data

  return posRef.current
}
