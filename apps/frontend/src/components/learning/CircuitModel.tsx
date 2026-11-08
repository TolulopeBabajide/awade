import { useId, useState } from 'react'
import Challenge from './Challenge'

export default function CircuitModel() {
  const [closed, setClosed] = useState(false)
  const [prediction, setPrediction] = useState('')
  const [testedPrediction, setTestedPrediction] = useState(false)
  const id = useId()
  return <>
    <div className="learning-model">
      <p className="learning-equation" aria-live="polite">{closed ? 'Closed path. The lamp is on.' : 'Open path. The lamp is off.'}</p>
      <svg className={`circuit-diagram ${closed ? 'is-closed' : ''}`} viewBox="0 0 360 190" role="img" aria-labelledby={`${id}-title ${id}-description`}>
        <title id={`${id}-title`}>Simple battery, switch and lamp circuit</title>
        <desc id={`${id}-description`}>{closed ? 'The switch joins both wires, completing a loop from the battery through the lamp and back.' : 'The switch leaves a gap in the wire. The loop is incomplete, so the lamp does not light.'}</desc>
        <path d="M65 150H25V35H140 M185 35H325V72 M325 116V150H105" fill="none" className="circuit-wire" />
        <circle cx="140" cy="35" r="4" fill="currentColor" /><circle cx="185" cy="35" r="4" fill="currentColor" />
        <line x1="140" y1="35" x2="185" y2={closed ? 35 : 10} className="circuit-switch" />
        <circle cx="325" cy="94" r="22" className="circuit-lamp" />
        <path d="M311 80L339 108M339 80L311 108" fill="none" stroke="currentColor" strokeWidth="2" />
        <line x1="65" x2="65" y1="128" y2="172" stroke="currentColor" strokeWidth="4" />
        <line x1="105" x2="105" y1="138" y2="162" stroke="currentColor" strokeWidth="4" />
        <text x="85" y="187" textAnchor="middle">Battery</text><text x="160" y="75" textAnchor="middle">Switch</text><text x="280" y="100" textAnchor="end">Lamp</text>
      </svg>
      <button type="button" className="learning-button-secondary" aria-pressed={closed} onClick={() => {
        setClosed(!closed)
        if (!closed && prediction === 'on') setTestedPrediction(true)
      }}>{closed ? 'Open the switch' : 'Close the switch'}</button>
    </div>
    <p className="mt-4 text-sm text-gray-600">A simplified working battery and lamp. A complete conducting path lets current flow; this model does not show current direction or measure voltage.</p>
    <Challenge conceptId="circuits" prompt="Predict what happens when you close the switch, then test your prediction." correct={prediction === 'on' && testedPrediction && closed}
      feedback={!prediction ? 'Choose a prediction before testing the switch.' : prediction !== 'on' ? 'A complete path lets current flow through a working lamp. Revisit your prediction, then test it.' : 'Open the switch, then close it to test your prediction.'}>
      <label className="learning-prediction" htmlFor={`${id}-prediction`}>My prediction<select id={`${id}-prediction`} value={prediction} onChange={event => { setPrediction(event.target.value); setTestedPrediction(false) }}><option value="">Choose a prediction</option><option value="on">The lamp will turn on</option><option value="off">The lamp will stay off</option></select></label>
    </Challenge>
  </>
}
