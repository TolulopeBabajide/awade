import { useId, useState } from 'react'
import Challenge from './Challenge'

export default function PlaceValueModel() {
  const id = useId()
  const [number, setNumber] = useState(24)
  const [exchanged, setExchanged] = useState(false)
  const tens = Math.floor(number / 10) - (exchanged ? 1 : 0)
  const ones = number % 10 + (exchanged ? 10 : 0)
  return <>
    <div className="learning-controls"><label htmlFor={id}>Number to build: {number}<input id={id} type="range" min={10} max={49} step={1} value={number} onChange={event => { setNumber(Number(event.target.value)); setExchanged(false) }} /></label></div>
    <div className="learning-model">
      <p className="learning-equation" aria-live="polite">{tens} tens + {ones} ones = {number}</p>
      <div className="place-columns">
        <div><h3>Tens ({tens})</h3><div className="place-tens" role="img" aria-label={`${tens} bundles of ten units`}>
          {Array.from({ length: tens }, (_, index) => <div key={index} className="place-bundle" aria-hidden="true">{Array.from({ length: 10 }, (_, unit) => <span key={unit} />)}</div>)}
        </div></div>
        <div><h3>Ones ({ones})</h3><div className="place-ones" role="img" aria-label={`${ones} individual units`}>{Array.from({ length: ones }, (_, index) => <span key={index} aria-hidden="true" />)}</div></div>
      </div>
    </div>
    <button type="button" className="learning-button-secondary mt-4" onClick={() => setExchanged(!exchanged)}>{exchanged ? 'Bundle ten ones into one ten' : 'Exchange one ten for ten ones'}</button>
    <p className="mt-3 text-sm text-gray-600">Each small square is one unit. Exchanging changes the grouping, not the total.</p>
    <Challenge conceptId="place-value" prompt="Build 32, then exchange a ten. How many tens and ones do you have?" correct={number === 32 && exchanged}
      feedback={number !== 32 ? 'Move the number slider to 32 first.' : 'Exchange one ten for ten ones. The total should still be 32.'} />
  </>
}
