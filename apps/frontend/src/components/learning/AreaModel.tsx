import { useId, useState } from 'react'
import Challenge from './Challenge'

export default function AreaModel() {
  const id = useId()
  const [width, setWidth] = useState(4)
  const [height, setHeight] = useState(3)
  const area = width * height
  const perimeter = 2 * (width + height)
  return <>
    <div className="learning-controls">
      <label htmlFor={`${id}-width`}>Width: {width} units<input id={`${id}-width`} type="range" min={1} max={6} value={width} onChange={event => setWidth(Number(event.target.value))} /></label>
      <label htmlFor={`${id}-height`}>Height: {height} units<input id={`${id}-height`} type="range" min={1} max={6} value={height} onChange={event => setHeight(Number(event.target.value))} /></label>
    </div>
    <div className="learning-model">
      <p className="learning-equation" aria-live="polite">Area: {area} square units · Perimeter: {perimeter} units</p>
      <div className="area-stage"><div className="area-grid" role="img" aria-label={`Rectangle ${width} units wide and ${height} units high, with ${area} unit squares`} style={{ width: `${width / 6 * 100}%`, aspectRatio: `${width} / ${height}`, gridTemplateColumns: `repeat(${width}, 1fr)` }}>
        {Array.from({ length: area }, (_, index) => <span key={index} aria-hidden="true" />)}
      </div></div>
      <p className="text-sm mt-3">Each square is 1 square unit. The outline traces the perimeter.</p>
    </div>
    <p className="mt-4 text-sm text-gray-600">Area = width × height. Perimeter = 2 × (width + height). This model covers rectangles.</p>
    <Challenge conceptId="area-perimeter" prompt="The starting 4 × 3 rectangle has area 12 and perimeter 14. Find a rectangle with the same area and a different perimeter." correct={area === 12 && perimeter !== 14}
      feedback={area !== 12 ? `Your area is ${area}. Try dimensions that multiply to 12.` : 'The area matches. Try another pair of sides to change the perimeter.'} />
  </>
}
