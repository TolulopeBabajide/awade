import React from 'react'
import { useIntersectionObserver } from '../hooks/useIntersectionObserver'

const steps = [
  {
    number: '1',
    title: 'Add your child',
    description: 'Enter their name, school, grade level, and the subjects they need help with. Takes less than a minute.',
  },
  {
    number: '2',
    title: 'Browse their topics',
    description: 'See the exact topics in your child\'s curriculum this term — organised by subject, matching what they\'re learning in class.',
  },
  {
    number: '3',
    title: 'Get your guide',
    description: 'Tap a topic and get a personalised "How to Help" guide — with simple explanations, a home activity, and tips for common mistakes.',
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
        <div className={`text-center max-w-2xl mx-auto mb-12 lg:mb-16 transition-opacity duration-700 ${isVisible ? 'opacity-100' : 'opacity-0'}`}>
          <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-primary-800 mb-4">
            How it works
          </h2>
          <p className="text-gray-600 text-base lg:text-lg">
            Three steps from "I don't know what they're studying" to "I can actually help."
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 lg:gap-12 max-w-4xl mx-auto">
          {steps.map((step, index) => (
            <div
              key={step.number}
              className={`text-center transition-all duration-500 ${
                isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
              }`}
              style={{ transitionDelay: `${index * 200}ms` }}
            >
              <div className="w-14 h-14 bg-accent-600 text-white rounded-full flex items-center justify-center text-xl font-bold mx-auto mb-4 shadow-md">
                {step.number}
              </div>
              <h3 className="text-lg font-semibold text-primary-800 mb-2">
                {step.title}
              </h3>
              <p className="text-gray-600 text-sm leading-relaxed">
                {step.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default HowItWorksSection
