import React from 'react'

const StatsSection: React.FC = () => {
  const stats = [
    {
      number: '2000+',
      label: 'AI Powered Courses',
      icon: '📚'
    },
    {
      number: '10',
      label: 'African Countries',
      icon: '🌍'
    },
    {
      number: '20',
      label: 'African Languages',
      icon: '🗣️'
    },
    {
      number: '150+',
      label: 'Enrollments',
      icon: '👥'
    }
  ]

  return (
    <section className="section-padding bg-white">
      <div className="container-custom">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          {stats.map((stat, index) => (
            <div 
              key={index} 
              className="text-center animate-fade-in"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="text-4xl mb-2">{stat.icon}</div>
              <div className="text-3xl md:text-4xl font-bold text-primary-600 mb-2">
                {stat.number}
              </div>
              <div className="text-gray-600 font-medium">
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