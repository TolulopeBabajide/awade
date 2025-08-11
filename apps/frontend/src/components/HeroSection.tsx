import React from 'react'
import { Link } from 'react-router-dom'

const HeroSection: React.FC = () => {
  return (
    <section 
      id="home" 
      className="section-padding gradient-bg"
      aria-labelledby="hero-heading"
    >
      <div className="container-custom">
        <div className="grid lg:grid-cols-2 gap-8 lg:gap-12 items-center">
          {/* Left Content */}
          <div className="space-y-6 lg:space-y-8 animate-fade-in order-2 lg:order-1">
            {/* Badge */}
            <div className="inline-flex items-center px-3 py-2 lg:px-4 lg:py-2 bg-primary-100 text-primary-700 rounded-full text-xs lg:text-sm font-medium">
              <span className="w-2 h-2 bg-primary-500 rounded-full mr-2" aria-hidden="true"></span>
              AI-Powered Lesson Planning
            </div>

            {/* Headline */}
            <h1 
              id="hero-heading"
              className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold text-primary-900 leading-tight"
            >
              Transform Your Teaching with{' '}
              <span className="text-gradient">Awade</span>
            </h1>

            {/* Description */}
            <p className="text-lg sm:text-xl text-background-600 leading-relaxed max-w-2xl">
              Generate AI-powered, curriculum-aligned lesson plans tailored to your local context. 
              Create engaging lessons that reflect African classroom realities and available resources.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4">
              <Link 
                to="/signup" 
                className="btn-accent text-base lg:text-lg px-6 lg:px-8 py-3 lg:py-4 text-center"
                aria-label="Sign up to start planning lessons"
              >
                Start Planning Lessons
              </Link>
              <button 
                className="btn-secondary text-base lg:text-lg px-6 lg:px-8 py-3 lg:py-4"
                aria-label="Learn more about how Awade works"
              >
                See How It Works
              </button>
            </div>
          </div>

          {/* Right Content - AI Lesson Planning Visualization */}
          <div className="relative animate-slide-up order-1 lg:order-2">
            <div className="relative w-full h-64 sm:h-80 md:h-96 lg:h-[500px] flex items-center justify-center">
              {/* Background Circle */}
              <div className="absolute inset-0 bg-gradient-to-br from-primary-100 to-accent-100 rounded-full opacity-50" aria-hidden="true"></div>
              
              {/* AI Brain with Lesson Plan */}
              <div className="relative z-10">
                <div className="w-32 h-32 sm:w-40 sm:h-40 md:w-48 md:h-48 lg:w-64 lg:h-64 bg-white rounded-full shadow-2xl flex items-center justify-center border-4 border-primary-200">
                  {/* AI Brain */}
                  <div className="w-20 h-20 sm:w-24 sm:h-24 md:w-32 md:h-32 lg:w-40 lg:h-40 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full flex items-center justify-center">
                    <div className="grid grid-cols-2 gap-1 sm:gap-2" aria-hidden="true">
                      <div className="w-2 h-2 sm:w-3 sm:h-3 bg-white rounded-full animate-pulse"></div>
                      <div className="w-2 h-2 sm:w-3 sm:h-3 bg-white rounded-full animate-pulse"></div>
                      <div className="w-2 h-2 sm:w-3 sm:h-3 bg-white rounded-full animate-pulse"></div>
                      <div className="w-2 h-2 sm:w-3 sm:h-3 bg-white rounded-full animate-pulse"></div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Lesson Plan Elements */}
              <div className="absolute inset-0" aria-hidden="true">
                {/* Connection Lines */}
                <svg className="absolute inset-0 w-full h-full" viewBox="0 0 400 400" aria-hidden="true">
                  {/* Lines connecting AI to lesson elements */}
                  <line x1="200" y1="200" x2="100" y2="100" stroke="#7a9d4a" strokeWidth="2" opacity="0.3"/>
                  <line x1="200" y1="200" x2="300" y2="100" stroke="#7a9d4a" strokeWidth="2" opacity="0.3"/>
                  <line x1="200" y1="200" x2="100" y2="300" stroke="#7a9d4a" strokeWidth="2" opacity="0.3"/>
                  <line x1="200" y1="200" x2="300" y2="300" stroke="#7a9d4a" strokeWidth="2" opacity="0.3"/>
                  <line x1="200" y1="200" x2="50" y2="200" stroke="#7a9d4a" strokeWidth="2" opacity="0.3"/>
                  <line x1="200" y1="200" x2="350" y2="200" stroke="#7a9d4a" strokeWidth="2" opacity="0.3"/>
                </svg>

                {/* Lesson Plan Components */}
                <div className="absolute top-4 left-4 sm:top-8 sm:left-8 w-8 h-8 sm:w-12 sm:h-12 bg-gradient-to-br from-accent-400 to-accent-600 rounded-full flex items-center justify-center text-white font-bold text-xs animate-bounce-gentle">
                  📚
                </div>
                <div className="absolute top-4 right-4 sm:top-8 sm:right-8 w-8 h-8 sm:w-12 sm:h-12 bg-gradient-to-br from-highlight-400 to-highlight-600 rounded-full flex items-center justify-center text-white font-bold text-xs animate-bounce-gentle" style={{animationDelay: '0.5s'}}>
                  🎯
                </div>
                <div className="absolute bottom-4 left-4 sm:bottom-8 sm:left-8 w-8 h-8 sm:w-12 sm:h-12 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full flex items-center justify-center text-white font-bold text-xs animate-bounce-gentle" style={{animationDelay: '1s'}}>
                  🌍
                </div>
                <div className="absolute bottom-4 right-4 sm:bottom-8 sm:right-8 w-8 h-8 sm:w-12 sm:h-12 bg-gradient-to-br from-accent-500 to-accent-700 rounded-full flex items-center justify-center text-white font-bold text-xs animate-bounce-gentle" style={{animationDelay: '1.5s'}}>
                  ✏️
                </div>
                <div className="absolute top-1/2 left-2 sm:left-4 transform -translate-y-1/2 w-8 h-8 sm:w-12 sm:h-12 bg-gradient-to-br from-warning-400 to-warning-600 rounded-full flex items-center justify-center text-white font-bold text-xs animate-bounce-gentle" style={{animationDelay: '0.75s'}}>
                  📊
                </div>
                <div className="absolute top-1/2 right-2 sm:right-4 transform -translate-y-1/2 w-8 h-8 sm:w-12 sm:h-12 bg-gradient-to-br from-error-400 to-error-600 rounded-full flex items-center justify-center text-white font-bold text-xs animate-bounce-gentle" style={{animationDelay: '1.25s'}}>
                  🎨
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

export default HeroSection 