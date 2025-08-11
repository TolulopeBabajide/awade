import React from 'react'

const FeaturesSection: React.FC = () => {
  const features = [
    {
      title: 'AI-Powered Lesson Generation',
      description: 'Generate comprehensive 6-section lesson plans with AI that understands your curriculum and local context.',
      icon: '🤖',
      color: 'from-blue-400 to-blue-600'
    },
    {
      title: 'Curriculum Alignment',
      description: 'Automatically align lessons with national curriculum standards and learning objectives for your country.',
      icon: '📚',
      color: 'from-accent-400 to-accent-600'
    },
    {
      title: 'Local Context Integration',
      description: 'Adapt lessons to your local environment, available resources, and community needs.',
      icon: '🌍',
      color: 'from-success-400 to-success-600'
    },
    {
      title: 'Professional Export',
      description: 'Export lesson plans as professional PDFs with proper formatting for classroom use.',
      icon: '📄',
      color: 'from-warning-400 to-warning-600'
    },
    {
      title: 'Offline Access',
      description: 'Access your lesson plans offline in the classroom, even without internet connectivity.',
      icon: '📱',
      color: 'from-error-400 to-error-600'
    },
    {
      title: 'Resource Generation',
      description: 'Create additional teaching resources, activities, and assessments for your lessons.',
      icon: '🎨',
      color: 'from-purple-400 to-purple-600'
    }
  ]

  return (
    <section 
      id="features"
      className="section-padding bg-white"
      aria-labelledby="features-heading"
    >
      <div className="container-custom">
        {/* Section Header */}
        <div className="text-center mb-8 lg:mb-12">
          <h2 
            id="features-heading"
            className="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900 mb-3 lg:mb-4"
          >
            Everything You Need for Effective Lesson Planning
          </h2>
          <p className="text-base lg:text-lg text-gray-600 max-w-3xl mx-auto px-4">
            Awade combines AI intelligence with curriculum expertise to help you create engaging, 
            culturally relevant lessons that work in your classroom.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
          {features.map((feature, index) => (
            <div 
              key={index} 
              className="card p-5 lg:p-6 text-center animate-fade-in hover:shadow-lg transition-shadow duration-300"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              {/* Feature Icon */}
              <div className="mb-4 lg:mb-6">
                <div className={`w-16 h-16 lg:w-20 lg:h-20 mx-auto bg-gradient-to-br ${feature.color} rounded-full flex items-center justify-center text-2xl lg:text-3xl mb-3 lg:mb-4`}>
                  <span role="img" aria-label={feature.title}>
                    {feature.icon}
                  </span>
                </div>
              </div>

              {/* Feature Content */}
              <h3 className="text-lg lg:text-xl font-bold text-gray-900 mb-2 lg:mb-3">
                {feature.title}
              </h3>
              <p className="text-sm lg:text-base text-gray-600 leading-relaxed">
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