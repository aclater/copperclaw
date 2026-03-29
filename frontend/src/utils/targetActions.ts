import type { TargetState, TargetActionDef, CycleState } from '../types'

const ECHO_CAPTURE_PREFERRED = new Set(['TGT-ECHO-001', 'TGT-ECHO-002'])
const ECHO_CALLSIGNS = new Set(['VARNAK', 'KAZMER'])

const GROUP_ORDER: Record<string, number> = { cycle: 0, isr: 1, info: 2, escalate: 3 }

export function getAvailableActions(
  state: TargetState | undefined,
  cycleState: CycleState,
): TargetActionDef[] {
  const actions: TargetActionDef[] = []
  const phase = state?.phase ?? 'FIND'
  const legalCleared = state?.legal_cleared ?? false
  const targetId = state?.target_id
  const codename = state?.codename ?? ''
  const tnpId = cycleState.hold_tnp_id

  // Always available
  actions.push({
    id: 'retask_isr',
    label: `Retask ISR to ${codename}`,
    group: 'isr',
    color: 'blue',
    requiresConfirm: false,
    requiresReason: false,
  })
  actions.push({
    id: 'view_intel',
    label: 'View intel summary',
    group: 'info',
    color: 'gray',
    requiresConfirm: false,
    requiresReason: false,
  })

  // HOLD phase actions
  if (phase === 'HOLD' && legalCleared) {
    actions.push({
      id: 'authorize_capture',
      label: 'Authorize capture operation',
      group: 'cycle',
      color: 'green',
      requiresConfirm: true,
      requiresReason: false,
    })
    actions.push({
      id: 'hold_target',
      label: 'Hold — request more collection',
      group: 'cycle',
      color: 'amber',
      requiresConfirm: false,
      requiresReason: true,
    })

    const isEchoComponent = targetId != null
      ? ECHO_CAPTURE_PREFERRED.has(targetId)
      : ECHO_CALLSIGNS.has(codename)

    actions.push({
      id: 'authorize_strike',
      label: 'Authorize kinetic strike',
      group: 'cycle',
      color: 'red',
      requiresConfirm: true,
      requiresReason: true,
      ...(isEchoComponent
        ? { lockedReason: 'capture preferred — ROE Alpha-7' }
        : {}),
    })
  }

  // HOLD phase with TNP
  if (phase === 'HOLD' && tnpId) {
    actions.push({
      id: 'view_tnp',
      label: `View ${tnpId}`,
      group: 'info',
      color: 'gray',
      requiresConfirm: false,
      requiresReason: false,
    })
  }

  // ASSESS or DEVELOP
  if (phase === 'ASSESS' || phase === 'DEVELOP') {
    actions.push({
      id: 'request_bda',
      label: 'Request immediate BDA',
      group: 'isr',
      color: 'blue',
      requiresConfirm: false,
      requiresReason: false,
    })
  }

  // FIND or FIX
  if (phase === 'FIND' || phase === 'FIX') {
    actions.push({
      id: 'hold_target',
      label: 'Hold — insufficient collection',
      group: 'cycle',
      color: 'amber',
      requiresConfirm: false,
      requiresReason: true,
    })
  }

  // Escalate — awaiting commander and this is the hold target
  if (
    cycleState.awaiting_commander &&
    targetId != null &&
    targetId === cycleState.hold_target_id
  ) {
    actions.push({
      id: 'escalate_urgent',
      label: 'Escalate to COMKJTF urgent',
      group: 'escalate',
      color: 'red',
      requiresConfirm: true,
      requiresReason: true,
    })
  }

  return actions.sort((a, b) => GROUP_ORDER[a.group] - GROUP_ORDER[b.group])
}
