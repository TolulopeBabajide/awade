import React, { useState } from 'react'

const FeaturesSection: React.FC = () => {
  const [currentSlide, setCurrentSlide] = useState(0)

  const features = [
    {
      title: 'AI Powered Learning',
      description: "Awade's AI generates lesson plans tailored to your curriculum and local context. Get personalized lesson structures that adapt to your teaching style.",
      image: '/src/assets/ChatGPT Image Aug 12, 2025, 12_14_16 PM.png',
      alt: 'AI robot with human hand interaction'
    },
    {
      title: 'Locally Relevant Content',
      description: 'Create lessons that reflect African classroom realities - large class sizes, limited resources, and cultural context. AI adapts content to your local environment.',
      image: '/src/assets/ChatGPT Image Aug 12, 2025, 12_19_01 PM.png',
      alt: 'Hand writing on chalkboard'
    },
    {
      title: 'Monitor Your Growth',
      description: 'Track your lesson planning progress and teaching effectiveness. Awade provides insights on curriculum coverage and helps you improve your lesson creation skills.',
      image: '/src/assets/ChatGPT Image Aug 12, 2025, 12_14_13 PM.png',
      alt: 'Laptop with education icons overlay'
    }
  ]

  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % features.length)
  }

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + features.length) % features.length)
  }

  return (
    <section 
      id="features"
      className="section-padding bg-white px-4 sm:px-6 lg:px-8"
      aria-labelledby="features-heading"
    >
      <div className="container-custom">
        {/* Section Header */}
        <div className="text-center mb-6 lg:mb-12">
        <div className="flex items-center justify-center mb-6 lg:mb-8">
            <div className="flex-1 h-px bg-background-300"></div>
            <h2 
              id="why-awade-heading"
              className="text-2xl sm:text-3xl md:text-4xl font-bold text-primary-900 px-4 sm:px-6 lg:px-8"
            >
              Why Awade?
            </h2>
            <div className="flex-1 h-px bg-background-300"></div>
          </div>
          <p className="text-sm sm:text-base md:text-lg text-background-600 max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
            Awade is an AI-powered lesson planning platform designed specifically for African educators. 
            We understand the unique challenges you face in the classroom and provide intelligent tools that save time while creating culturally relevant, curriculum-aligned lessons.
          </p>
        </div>

        {/* Mobile Carousel */}
        <div className="md:hidden">
          <div className="relative max-w-sm mx-auto">
            <div className="overflow-hidden rounded-xl">
              <div 
                className="flex transition-transform duration-300 ease-in-out"
                style={{ transform: `translateX(-${currentSlide * 100}%)` }}
              >
                {features.map((feature, index) => (
                  <div key={index} className="w-full flex-shrink-0">
                    <div className="bg-white rounded-xl p-4 text-center">
                      {/* Feature Image */}
                      <div className="mb-4">
                        <div className="w-full h-40 rounded-lg overflow-hidden mb-3">
                          <img 
                            src={feature.image}
                            alt={feature.alt}
                            className="w-full h-full object-cover"
                          />
                        </div>
                      </div>

                      {/* Feature Content */}
                      <h3 className="text-lg font-bold text-primary-900 mb-2">
                        {feature.title}
                      </h3>
                      <p className="text-xs text-background-600 leading-relaxed">
                        {feature.description}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Carousel Navigation */}
            <div className="flex justify-center items-center mt-6 space-x-2">
              <button
                onClick={prevSlide}
                className="p-2 rounded-full bg-primary-100 text-primary-600 hover:bg-primary-200 transition-colors"
                aria-label="Previous feature"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              
              {/* Dots Indicator */}
              <div className="flex space-x-1">
                {features.map((_, index) => (
                  <button
                    key={index}
                    onClick={() => setCurrentSlide(index)}
                    className={`w-2 h-2 rounded-full transition-colors ${
                      index === currentSlide ? 'bg-primary-600' : 'bg-primary-200'
                    }`}
                    aria-label={`Go to slide ${index + 1}`}
                  />
                ))}
              </div>

              <button
                onClick={nextSlide}
                className="p-2 rounded-full bg-primary-100 text-primary-600 hover:bg-primary-200 transition-colors"
                aria-label="Next feature"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        {/* Desktop Grid Layout */}
        <div className="hidden md:grid grid-cols-1 md:grid-cols-3 gap-4 lg:gap-8 max-w-6xl mx-auto">
          {features.map((feature, index) => (
            <div 
              key={index} 
              className={`bg-white rounded-xl p-4 lg:p-8 text-center animate-fade-in ${
                index === 1 ? 'md:translate-y-8' : index === 2 ? 'md:translate-y-16' : ''
              }`}
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              {/* Feature Image */}
              <div className="mb-4 lg:mb-8">
                <div className="w-full h-40 lg:h-56 rounded-lg overflow-hidden mb-3 lg:mb-4">
                  <img 
                    src={feature.image}
                    alt={feature.alt}
                    className="w-full h-full object-cover"
                  />
                </div>
              </div>

              {/* Feature Content */}
              <h3 className="text-lg sm:text-xl lg:text-2xl font-bold text-primary-900 mb-2 lg:mb-4">
                {feature.title}
              </h3>
              <p className="text-xs sm:text-sm lg:text-base text-background-600 leading-relaxed">
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