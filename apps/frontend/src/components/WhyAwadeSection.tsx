import React from 'react'

const WhyAwadeSection: React.FC = () => {
  return (
    <section id="about" className="section-padding bg-gray-50">
      <div className="container-custom">
        <div className="text-center max-w-4xl mx-auto">
          {/* Section Heading */}
          <div className="flex items-center justify-center mb-8">
            <div className="flex-1 h-px bg-gray-300"></div>
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 px-8">
              Why Awade?
            </h2>
            <div className="flex-1 h-px bg-gray-300"></div>
          </div>

          {/* Description */}
          <p className="text-lg md:text-xl text-gray-600 leading-relaxed">
            Awade is an AI-driven platform offering personalized, culturally relevant training to empower African educators. 
            It addresses local classroom challenges, fostering continuous growth through adaptive modules and a robust dashboard.
          </p>
        </div>
      </div>
    </section>
  )
}

export default WhyAwadeSection 