import React from 'react'

const StatsSection: React.FC = () => {
  const stats = [
    {
      number: '500+',
      label: 'Lesson Plans Generated',
      icon: '📝'
    },
    {
      number: '15+',
      label: 'African Countries',
      icon: '🌍'
    },
    {
      number: '25+',
      label: 'Subjects Covered',
      icon: '📚'
    },
    {
      number: '100+',
      label: 'Active Teachers',
      icon: '👨‍🏫'
    }
  ]

  return (
    <section className="section-padding bg-white">
      <div className="container-custom">
        {/* Section Header */}
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Awade by the Numbers
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            See how educators across Africa are using Awade to transform their lesson planning
          </p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          {stats.map((stat, index) => (
            <div 
              key={index} 
              className="text-center animate-fade-in"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="text-4xl mb-3">{stat.icon}</div>
              <div className="text-3xl md:text-4xl font-bold text-primary-600 mb-2">
                {stat.number}
              </div>
              <div className="text-gray-600 font-medium text-sm">
                {stat.label}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default StatsSection 