import type { TargetAction, SelectedTarget, CycleState } from '../types'

export async function executeTargetAction(
  action: TargetAction,
  target: SelectedTarget,
  _cycleState: CycleState,
  reason?: string,
): Promise<{ success: boolean; message: string }> {
  const { codename, targetId } = target
  const reasonSuffix = reason?.trim() ? ` — ${reason.trim()}` : ''

  let message: string

  switch (action) {
    case 'authorize_capture':
      message = `authorize capture operation ${codename} (${targetId}) — ${reason?.trim() || 'legal review cleared, proceed'}`
      break
    case 'authorize_strike':
      message = `authorize kinetic strike on ${codename} (${targetId})${reasonSuffix}`
      break
    case 'hold_target':
      message = `hold ${codename} (${targetId})${reasonSuffix}`
      break
    case 'retask_isr':
      message = `retask RAVEN-1 to ${codename} (${targetId}) collection, priority immediate`
      break
    case 'request_bda':
      message = `request BDA on ${codename} (${targetId}), priority immediate`
      break
    case 'view_tnp':
      console.log(`[Phase 8] TNP detail panel requested for ${codename} (${targetId})`)
      return { success: true, message: 'TNP view requested' }
    case 'view_intel':
      message = `summarize current intelligence on ${codename} (${targetId})`
      break
    case 'escalate_urgent':
      message = `URGENT — escalate ${codename} (${targetId}) to COMKJTF immediate action${reasonSuffix}`
      break
    default:
      return { success: false, message: 'Unknown action' }
  }

  try {
    const res = await fetch('/api/operator/message', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message }),
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return { success: true, message }
  } catch {
    return { success: false, message }
  }
}
