import React from 'react'

const FeaturesSection: React.FC = () => {
  const features = [
    {
      title: 'AI Powered Learning',
      description: 'Awade\'s AI tailors training to unique teaching needs.',
      icon: '🤖',
      image: 'ai-robot-hand',
      color: 'from-blue-400 to-blue-600'
    },
    {
      title: 'Culturally Relevant Content',
      description: 'Training that reflects African classroom realities.',
      icon: '👨‍🏫',
      image: 'african-teacher',
      color: 'from-accent-400 to-accent-600'
    },
    {
      title: 'Monitor Your Growth',
      description: 'Insights into teaching skills and professional goals.',
      icon: '📊',
      image: 'dashboard',
      color: 'from-success-400 to-success-600'
    }
  ]

  return (
    <section className="section-padding bg-white">
      <div className="container-custom">
        <div className="grid md:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div 
              key={index} 
              className="card p-8 text-center animate-fade-in"
              style={{ animationDelay: `${index * 0.2}s` }}
            >
              {/* Feature Icon/Image */}
              <div className="mb-6">
                <div className={`w-24 h-24 mx-auto bg-gradient-to-br ${feature.color} rounded-full flex items-center justify-center text-4xl mb-4`}>
                  {feature.icon}
                </div>
                
                {/* Placeholder for feature image */}
                <div className={`w-full h-48 bg-gradient-to-br ${feature.color} rounded-lg flex items-center justify-center text-white text-6xl opacity-20`}>
                  {feature.icon}
                </div>
              </div>

              {/* Feature Content */}
              <h3 className="text-xl font-bold text-gray-900 mb-4">
                {feature.title}
              </h3>
              <p className="text-gray-600 leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default FeaturesSection 