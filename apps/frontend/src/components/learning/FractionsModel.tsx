import { useId, useState } from 'react'
import Challenge from './Challenge'
import { simplifyFraction } from './concepts'

export default function FractionsModel() {
  const id = useId()
  const [parts, setParts] = useState({ numerator: 2, denominator: 4 })
  const [splitFrom, setSplitFrom] = useState<string | null>(null)
  const { numerator, denominator } = parts
  const fraction = `${numerator}/${denominator}`
  const amount = numerator / denominator * 100
  return (
    <>
      <div className="learning-controls">
        <label htmlFor={`${id}-parts`}>Equal parts in one whole
          <select id={`${id}-parts`} value={denominator} onChange={event => {
            const next = Number(event.target.value)
            setParts({ numerator: Math.min(numerator, next), denominator: next }); setSplitFrom(null)
          }}>{[2, 3, 4, 6, 8, 12].map(value => <option key={value} value={value}>{value} parts</option>)}</select>
        </label>
        <label htmlFor={`${id}-shaded`}>Shaded parts: {numerator} of {denominator}
          <input id={`${id}-shaded`} type="range" min={0} max={denominator} step={1} value={numerator} onChange={event => {
            setParts({ ...parts, numerator: Number(event.target.value) }); setSplitFrom(null)
          }} />
        </label>
      </div>
      <div className="learning-model">
        <p className="learning-equation" aria-live="polite">{fraction} = {simplifyFraction(numerator, denominator)} of one whole</p>
        <div className="fraction-whole" role="img" aria-label={`${numerator} of ${denominator} equal parts shaded`}>
          <div className="fraction-shade" style={{ width: `${amount}%` }} />
          <div className="fraction-parts" style={{ gridTemplateColumns: `repeat(${denominator}, minmax(0, 1fr))` }} aria-hidden="true">
            {Array.from({ length: denominator }, (_, index) => <span key={index}>{index < numerator ? '✓' : ''}</span>)}
          </div>
        </div>
        <div className="fraction-line" role="img" aria-label={`${fraction} is ${amount.toFixed(1)} percent of the distance from zero to one`}>
          <div className="fraction-axis"><span className="fraction-marker" style={{ left: `${amount}%` }} /></div>
          <div className="flex justify-between mt-3 text-sm"><span>0</span><span>1/2</span><span>1 whole</span></div>
        </div>
      </div>
      <div className="flex flex-wrap gap-3 items-center mt-4">
        <button type="button" className="learning-button-secondary" disabled={denominator > 6} onClick={() => {
          setSplitFrom(fraction); setParts({ numerator: numerator * 2, denominator: denominator * 2 })
        }}>Split every part in two</button>
        <p className="text-sm text-gray-600" aria-live="polite">{splitFrom ? `${splitFrom} = ${fraction}. The shaded amount stays the same.` : 'The whole stays the same size as you change the parts.'}</p>
      </div>
      <Challenge conceptId="fractions" prompt="Show one half using six equal parts. Then explain how you know." correct={denominator === 6 && numerator === 3}
        feedback={denominator !== 6 ? 'Choose six equal parts first, then shade half of them.' : numerator < 3 ? 'Less than half is shaded. Try shading more parts.' : 'More than half is shaded. Try shading fewer parts.'} />
    </>
  )
}
