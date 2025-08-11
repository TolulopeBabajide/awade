import React from 'react'

const WhyAwadeSection: React.FC = () => {
  return (
    <section 
      id="about" 
      className="section-padding bg-gray-50"
      aria-labelledby="why-awade-heading"
    >
      <div className="container-custom">
        <div className="text-center max-w-4xl mx-auto">
          {/* Section Heading */}
          <div className="flex items-center justify-center mb-6 lg:mb-8">
            <div className="flex-1 h-px bg-gray-300"></div>
            <h2 
              id="why-awade-heading"
              className="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900 px-4 sm:px-8"
            >
              Why Choose Awade?
            </h2>
            <div className="flex-1 h-px bg-gray-300"></div>
          </div>

          {/* Description */}
          <p className="text-base lg:text-lg md:text-xl text-gray-600 leading-relaxed mb-8 px-4">
            Awade is an AI-powered lesson planning platform designed specifically for African educators. 
            We understand the unique challenges you face in the classroom and provide intelligent tools 
            that save time while creating culturally relevant, curriculum-aligned lessons.
          </p>

          {/* Key Benefits Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8 mt-8 lg:mt-12">
            <div className="text-center">
              <div className="w-12 h-12 lg:w-16 lg:h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-3 lg:mb-4">
                <span className="text-xl lg:text-2xl" role="img" aria-label="Save time">⏰</span>
              </div>
              <h3 className="text-base lg:text-lg font-semibold text-gray-900 mb-2">Save Time</h3>
              <p className="text-sm lg:text-base text-gray-600 px-2">
                Generate complete lesson plans in minutes, not hours
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 lg:w-16 lg:h-16 bg-accent-100 rounded-full flex items-center justify-center mx-auto mb-3 lg:mb-4">
                <span className="text-xl lg:text-2xl" role="img" aria-label="Stay aligned">🎯</span>
              </div>
              <h3 className="text-base lg:text-lg font-semibold text-gray-900 mb-2">Stay Aligned</h3>
              <p className="text-sm lg:text-base text-gray-600 px-2">
                Automatically match national curriculum standards
              </p>
            </div>
            
            <div className="text-center sm:col-span-2 lg:col-span-1">
              <div className="w-12 h-12 lg:w-16 lg:h-16 bg-success-100 rounded-full flex items-center justify-center mx-auto mb-3 lg:mb-4">
                <span className="text-xl lg:text-2xl" role="img" aria-label="Local context">🌍</span>
              </div>
              <h3 className="text-base lg:text-lg font-semibold text-gray-900 mb-2">Local Context</h3>
              <p className="text-sm lg:text-base text-gray-600 px-2">
                Lessons that reflect your community and resources
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

export default WhyAwadeSection 