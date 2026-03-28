import { useCycleState } from './hooks/useCycleState'
import { useOperator } from './hooks/useOperator'
import { Shell } from './components/Shell'

export default function App() {
  const { state, connected } = useCycleState()
  const { input, setInput, transmit, sending, messages } = useOperator()

  return (
    <Shell
      state={state}
      connected={connected}
      operatorInput={input}
      setOperatorInput={setInput}
      transmit={transmit}
      sending={sending}
      messages={messages}
    />
  )
}
