import React from 'react'
import { useIntersectionObserver } from '../hooks/useIntersectionObserver'

// ─── Phone-frame SVG wrapper ────────────────────────────────────────────────
// Renders a mobile screen frame with clipped content inside.
// viewBox is 200 × 380; content slot starts at y=20 (below notch).
interface PhoneFrameProps {
  children: React.ReactNode
  screenColor?: string
}

const CLIP_ID_PREFIX = 'phone-screen-clip'

const PhoneFrame: React.FC<PhoneFrameProps & { clipId: string }> = ({
  children,
  screenColor = 'white',
  clipId,
}) => (
  <svg
    viewBox="0 0 200 380"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
    className="w-full h-full drop-shadow-md"
  >
    <defs>
      {/* Clip path so screen content never bleeds outside the phone body */}
      <clipPath id={clipId}>
        <rect x="8" y="18" width="184" height="346" rx="16" ry="16" />
      </clipPath>
    </defs>

    {/* Phone body */}
    <rect x="1" y="1" width="198" height="378" rx="26" ry="26" fill="#f5f4f3" stroke="#c9c5c2" strokeWidth="1.5" />

    {/* Side buttons */}
    <rect x="0" y="90" width="2" height="28" rx="1" fill="#c9c5c2" />
    <rect x="0" y="124" width="2" height="28" rx="1" fill="#c9c5c2" />
    <rect x="198" y="110" width="2" height="44" rx="1" fill="#c9c5c2" />

    {/* Camera notch */}
    <rect x="76" y="5" width="48" height="10" rx="5" fill="#c9c5c2" />
    <circle cx="152" cy="10" r="4" fill="#d1cdc9" />

    {/* Screen background */}
    <rect x="8" y="18" width="184" height="346" rx="16" ry="16" fill={screenColor} />

    {/* Screen content (clipped) */}
    <g clipPath={`url(#${clipId})`}>{children}</g>

    {/* Home indicator bar */}
    <rect x="76" y="366" width="48" height="5" rx="2.5" fill="#c9c5c2" />
  </svg>
)

// ─── Step 1: Add Child form ──────────────────────────────────────────────────
const AddChildMockup: React.FC = () => (
  <PhoneFrame clipId={`${CLIP_ID_PREFIX}-1`} screenColor="white">
    {/* Header */}
    <rect x="8" y="18" width="184" height="44" fill="#3d5029" />
    <text x="100" y="45" textAnchor="middle" fill="white" fontSize="11" fontFamily="sans-serif" fontWeight="700">Add Child</text>

    {/* Progress dots */}
    <circle cx="88" cy="70" r="5" fill="#5f7e3a" />
    <circle cx="100" cy="70" r="3" fill="#c3d4a8" />
    <circle cx="112" cy="70" r="3" fill="#c3d4a8" />

    {/* Name field */}
    <text x="20" y="92" fill="#6b7280" fontSize="7.5" fontFamily="sans-serif" fontWeight="600">Child's name *</text>
    <rect x="20" y="96" width="160" height="20" rx="5" fill="#f9fafb" stroke="#d1d5db" strokeWidth="1" />
    <text x="28" y="110" fill="#374151" fontSize="8" fontFamily="sans-serif">Kofi Mensah</text>

    {/* Grade field */}
    <text x="20" y="130" fill="#6b7280" fontSize="7.5" fontFamily="sans-serif" fontWeight="600">Grade Level *</text>
    <rect x="20" y="134" width="160" height="20" rx="5" fill="#f9fafb" stroke="#d1d5db" strokeWidth="1" />
    <text x="28" y="148" fill="#374151" fontSize="8" fontFamily="sans-serif">Grade 5 (Primary 5)</text>
    <text x="170" y="148" fill="#9ca3af" fontSize="10" fontFamily="sans-serif">▾</text>

    {/* Country field */}
    <text x="20" y="168" fill="#6b7280" fontSize="7.5" fontFamily="sans-serif" fontWeight="600">Country *</text>
    <rect x="20" y="172" width="160" height="20" rx="5" fill="#f9fafb" stroke="#d1d5db" strokeWidth="1" />
    <text x="28" y="186" fill="#374151" fontSize="8" fontFamily="sans-serif">Ghana</text>
    <text x="170" y="186" fill="#9ca3af" fontSize="10" fontFamily="sans-serif">▾</text>

    {/* Subjects label */}
    <text x="20" y="208" fill="#6b7280" fontSize="7.5" fontFamily="sans-serif" fontWeight="600">Subjects</text>

    {/* Subject checkboxes */}
    <rect x="20" y="214" width="12" height="12" rx="3" fill="#5f7e3a" />
    <text x="26" y="224" textAnchor="middle" fill="white" fontSize="9" fontFamily="sans-serif" fontWeight="700">✓</text>
    <text x="38" y="224" fill="#374151" fontSize="8" fontFamily="sans-serif">Mathematics</text>

    <rect x="20" y="230" width="12" height="12" rx="3" fill="#5f7e3a" />
    <text x="26" y="240" textAnchor="middle" fill="white" fontSize="9" fontFamily="sans-serif" fontWeight="700">✓</text>
    <text x="38" y="240" fill="#374151" fontSize="8" fontFamily="sans-serif">English Language</text>

    <rect x="20" y="246" width="12" height="12" rx="3" fill="white" stroke="#d1d5db" strokeWidth="1" />
    <text x="38" y="256" fill="#374151" fontSize="8" fontFamily="sans-serif">Science</text>

    <rect x="20" y="262" width="12" height="12" rx="3" fill="white" stroke="#d1d5db" strokeWidth="1" />
    <text x="38" y="272" fill="#374151" fontSize="8" fontFamily="sans-serif">Social Studies</text>

    {/* CTA button */}
    <rect x="20" y="310" width="160" height="28" rx="8" fill="#a55a42" />
    <text x="100" y="329" textAnchor="middle" fill="white" fontSize="10" fontFamily="sans-serif" fontWeight="700">Continue →</text>
  </PhoneFrame>
)

// ─── Step 2: Topics browser ──────────────────────────────────────────────────
const TopicsBrowserMockup: React.FC = () => (
  <PhoneFrame clipId={`${CLIP_ID_PREFIX}-2`} screenColor="#f5f5f4">
    {/* Header */}
    <rect x="8" y="18" width="184" height="52" fill="#3d5029" />
    <circle cx="26" cy="43" r="12" fill="#5f7e3a" />
    <text x="26" y="47" textAnchor="middle" fill="white" fontSize="9" fontFamily="sans-serif" fontWeight="700">K</text>
    <text x="108" y="38" textAnchor="middle" fill="white" fontSize="9" fontFamily="sans-serif" fontWeight="700">Kofi Mensah</text>
    <text x="108" y="52" textAnchor="middle" fill="#c3d4a8" fontSize="7.5" fontFamily="sans-serif">Grade 5 · Ghana</text>

    {/* Subject filter tabs */}
    <rect x="8" y="70" width="184" height="28" fill="#edf2e7" />
    <rect x="14" y="74" width="62" height="20" rx="10" fill="#a55a42" />
    <text x="45" y="88" textAnchor="middle" fill="white" fontSize="7.5" fontFamily="sans-serif" fontWeight="700">Mathematics</text>
    <text x="110" y="88" textAnchor="middle" fill="#5f7e3a" fontSize="7.5" fontFamily="sans-serif" fontWeight="600">English</text>
    <text x="163" y="88" textAnchor="middle" fill="#5f7e3a" fontSize="7.5" fontFamily="sans-serif" fontWeight="600">Science</text>

    {/* Topic list */}
    {([
      ['Fractions', true],
      ['Decimals', false],
      ['Percentages', true],
      ['Algebra Basics', false],
      ['Number Patterns', true],
      ['Geometry', false],
    ] as [string, boolean][]).map(([label, shaded], i) => (
      <g key={label}>
        <rect x="12" y={104 + i * 30} width="176" height="26" rx="6" fill={shaded ? 'white' : '#f5f5f4'} />
        <rect x="12" y={104 + i * 30} width="4" height="26" rx="2" fill="#5f7e3a" />
        <text x="24" y={104 + i * 30 + 17} fill="#3d5029" fontSize="8.5" fontFamily="sans-serif" fontWeight="500">{label}</text>
        <text x="178" y={104 + i * 30 + 18} fill="#a55a42" fontSize="14" fontFamily="sans-serif">›</text>
      </g>
    ))}
  </PhoneFrame>
)

// ─── Step 3: Guide view ──────────────────────────────────────────────────────
const GuideMockup: React.FC = () => (
  <PhoneFrame clipId={`${CLIP_ID_PREFIX}-3`} screenColor="#f5f5f4">
    {/* Header */}
    <rect x="8" y="18" width="184" height="62" fill="#3d5029" />
    <text x="100" y="36" textAnchor="middle" fill="#c3d4a8" fontSize="7.5" fontFamily="sans-serif">How to Help</text>
    <text x="100" y="52" textAnchor="middle" fill="white" fontSize="13" fontFamily="sans-serif" fontWeight="700">Fractions</text>
    <text x="100" y="67" textAnchor="middle" fill="#a3c068" fontSize="7.5" fontFamily="sans-serif">Mathematics · Grade 5</text>

    {/* Action icons row */}
    <rect x="8" y="80" width="184" height="26" fill="#4a6330" />
    <text x="50" y="97" textAnchor="middle" fill="#c3d4a8" fontSize="7" fontFamily="sans-serif">🔖 Save</text>
    <text x="100" y="97" textAnchor="middle" fill="#c3d4a8" fontSize="7" fontFamily="sans-serif">📤 Share</text>
    <text x="150" y="97" textAnchor="middle" fill="#c3d4a8" fontSize="7" fontFamily="sans-serif">📥 Export</text>

    {/* Simple Explanation card */}
    <rect x="12" y="114" width="176" height="64" rx="6" fill="white" />
    <rect x="12" y="114" width="4" height="64" rx="2" fill="#5f7e3a" />
    <text x="24" y="128" fill="#3d5029" fontSize="8" fontFamily="sans-serif" fontWeight="700">Simple Explanation</text>
    <rect x="22" y="134" width="130" height="5" rx="2" fill="#e5e7eb" />
    <rect x="22" y="143" width="150" height="5" rx="2" fill="#e5e7eb" />
    <rect x="22" y="152" width="110" height="5" rx="2" fill="#e5e7eb" />
    <rect x="22" y="161" width="90" height="5" rx="2" fill="#e5e7eb" />

    {/* Try This at Home card */}
    <rect x="12" y="186" width="176" height="64" rx="6" fill="white" />
    <rect x="12" y="186" width="4" height="64" rx="2" fill="#a55a42" />
    <text x="24" y="200" fill="#3d5029" fontSize="8" fontFamily="sans-serif" fontWeight="700">Try This at Home 🏠</text>
    <rect x="22" y="206" width="140" height="5" rx="2" fill="#e5e7eb" />
    <rect x="22" y="215" width="120" height="5" rx="2" fill="#e5e7eb" />
    <rect x="22" y="224" width="100" height="5" rx="2" fill="#e5e7eb" />
    <rect x="22" y="233" width="130" height="5" rx="2" fill="#e5e7eb" />

    {/* Common Mistakes card */}
    <rect x="12" y="258" width="176" height="54" rx="6" fill="white" />
    <rect x="12" y="258" width="4" height="54" rx="2" fill="#f59e0b" />
    <text x="24" y="272" fill="#3d5029" fontSize="8" fontFamily="sans-serif" fontWeight="700">Common Mistakes ⚠️</text>
    <rect x="22" y="278" width="130" height="5" rx="2" fill="#e5e7eb" />
    <rect x="22" y="287" width="100" height="5" rx="2" fill="#e5e7eb" />
    <rect x="22" y="296" width="115" height="5" rx="2" fill="#e5e7eb" />
  </PhoneFrame>
)

// ─── Section ─────────────────────────────────────────────────────────────────
const steps = [
  {
    number: '1',
    title: 'Add your child',
    description:
      "Enter their name, school, grade level, and the subjects they need help with. Takes less than a minute.",
    mockup: <AddChildMockup />,
    mockupAlt: 'Screenshot of the Add Child form showing name, grade, country and subject fields',
  },
  {
    number: '2',
    title: 'Browse their topics',
    description:
      "See the exact topics in your child's curriculum this term — organised by subject, matching what they're learning in class.",
    mockup: <TopicsBrowserMockup />,
    mockupAlt: 'Screenshot of the topics browser showing Mathematics topics for Grade 5',
  },
  {
    number: '3',
    title: 'Get your guide',
    description:
      'Tap a topic and get a personalised "How to Help" guide — with simple explanations, a home activity, and tips for common mistakes.',
    mockup: <GuideMockup />,
    mockupAlt: 'Screenshot of a How to Help guide for Fractions showing three sections',
  },
]

const HowItWorksSection: React.FC = () => {
  const { ref, isVisible } = useIntersectionObserver({
    threshold: 0.1,
    freezeOnceVisible: true,
  })

  return (
    <section id="how-it-works" className="py-16 lg:py-24 bg-background-50" ref={ref}>
      <div className="container-custom px-4 sm:px-6 lg:px-8">
        {/* Heading */}
        <div
          className={`text-center max-w-2xl mx-auto mb-12 lg:mb-16 transition-opacity duration-700 ${
            isVisible ? 'opacity-100' : 'opacity-0'
          }`}
        >
          <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-primary-800 mb-4">
            How it works
          </h2>
          <p className="text-gray-600 text-base lg:text-lg">
            Three steps from "I don't know what they're studying" to "I can actually help."
          </p>
        </div>

        {/* Step cards */}
        <div className="grid md:grid-cols-3 gap-10 lg:gap-14 max-w-5xl mx-auto">
          {steps.map((step, index) => (
            <div
              key={step.number}
              className={`flex flex-col items-center transition-all duration-500 ${
                isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'
              }`}
              style={{ transitionDelay: `${index * 180}ms` }}
            >
              {/* Phone mockup */}
              <div
                className="w-40 sm:w-44 lg:w-48 mb-6"
                role="img"
                aria-label={step.mockupAlt}
              >
                {step.mockup}
              </div>

              {/* Step badge + text */}
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-9 h-9 bg-accent-700 text-white rounded-full text-sm font-bold mb-3 shadow">
                  {step.number}
                </div>
                <h3 className="text-lg font-semibold text-primary-800 mb-2">
                  {step.title}
                </h3>
                <p className="text-gray-600 text-sm leading-relaxed">
                  {step.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default HowItWorksSection
