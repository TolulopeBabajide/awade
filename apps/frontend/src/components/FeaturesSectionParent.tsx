import React from 'react'
import { useIntersectionObserver } from '../hooks/useIntersectionObserver'

interface Feature {
  icon: string;
  title: string;
  description: string;
}

const features: Feature[] = [
  {
    icon: '📚',
    title: 'Know Their Curriculum',
    description:
      'Add your child\'s school, grade, and subjects — Awade maps their exact curriculum so you always know what they\'re studying this term.',
  },
  {
    icon: '💡',
    title: 'Get "How to Help" Guides',
    description:
      'Tap any topic and get a plain-language explanation, a home activity using household items, and conversation starters — all tailored to your child\'s level.',
  },
  {
    icon: '🏠',
    title: 'Help with Homework',
    description:
      'No need to re-learn the textbook. Each guide tells you the common mistakes kids make and exactly what to say to help — without doing it for them.',
  },
  {
    icon: '📈',
    title: 'Track What You\'ve Covered',
    description:
      'Bookmark guides, see which topics you\'ve explored together, and know what\'s coming next in the curriculum — so you stay one step ahead.',
  },
]

const FeaturesSectionParent: React.FC = () => {
  const { ref, isVisible } = useIntersectionObserver({
    threshold: 0.1,
    freezeOnceVisible: true,
  })

  return (
    <section id="features" className="py-16 lg:py-24 bg-white" ref={ref}>
      <div className="container-custom px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <div className={`text-center max-w-2xl mx-auto mb-12 lg:mb-16 transition-opacity duration-700 ${isVisible ? 'opacity-100' : 'opacity-0'}`}>
          <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-primary-800 mb-4">
            Everything you need to support your child
          </h2>
          <p className="text-gray-600 text-base lg:text-lg">
            No teaching degree required — just a parent who cares.
          </p>
        </div>

        {/* Feature cards */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8">
          {features.map((feature, index) => (
            <div
              key={feature.title}
              className={`bg-background-50 rounded-2xl p-6 lg:p-8 transition-all duration-500 hover:shadow-lg hover:-translate-y-1 ${
                isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
              }`}
              style={{ transitionDelay: `${index * 150}ms` }}
            >
              <div className="text-3xl mb-4">{feature.icon}</div>
              <h3 className="text-lg font-semibold text-primary-800 mb-2">
                {feature.title}
              </h3>
              <p className="text-gray-600 text-sm leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default FeaturesSectionParent
