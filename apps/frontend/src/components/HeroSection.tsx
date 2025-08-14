import React from 'react'
import { Link } from 'react-router-dom'

const HeroSection: React.FC = () => {
  return (
    <section 
      id="home" 
      className="hero-gradient pb-16 px-4 sm:px-6 lg:px-8 h-[50vh] lg:h-auto"
      aria-labelledby="hero-heading"
    >
      <div className="container-custom h-full">
        <div className="grid lg:grid-cols-2 gap-8 lg:gap-12 items-end lg:items-center h-full">
          {/* Left Content */}
          <div className="space-y-4 lg:space-y-8 animate-fade-in order-2 lg:order-1 px-4 sm:px-6 lg:px-8 w-full lg:w-full flex flex-col justify-end h-full lg:h-auto">
            {/* Badge */}
            <div className="hidden w-1/2 text-center sm:inline-flex items-center px-2 py-1 lg:px-4 lg:py-2 bg-primary-100 text-primary-600 rounded-lg text-xs lg:text-sm font-medium">
              <span className="w-1 h-1 lg:w-2 lg:h-2 bg-primary-600 rounded-full mr-1 lg:mr-2" aria-hidden="true"></span>
              AI-Powered Lesson Planning
            </div>

            {/* Headline */}
            <h1 
              id="hero-heading"
              className="text-xl sm:text-2xl md:text-3xl lg:text-5xl font-bold text-primary-700 leading-tight"
            >
              Transform Your Teaching with Awade
            </h1>

            {/* Description */}
            <p className="text-sm sm:text-base md:text-lg lg:text-xl text-black/90 leading-relaxed max-w-2xl">
              Unlock AI-Powered, locally contextual lesson planning for African educators.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-3 lg:gap-4 w-[35%] sm:w-[35%]">
              <Link 
                to="/signup" 
                className="bg-accent-600 hover:bg-accent-700 text-white font-medium py-2 px-3 lg:py-3 lg:px-6 rounded-lg transition-all duration-200 transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:ring-offset-2 text-sm lg:text-lg text-center"
                aria-label="Sign up to start planning lessons"
              >
                Get Started
              </Link>
            </div>
          </div>

          {/* Right Content - Image Only */}
          <div className="hidden md:block relative animate-slide-up order-1 lg:order-2">
            <div className="relative w-full h-64 sm:h-80 md:h-96 lg:h-[500px] flex items-center justify-center">
              {/* Central Image */}
              <div className="relative z-20">
                <div className="w-64 h-64 sm:w-80 sm:h-80 md:w-96 md:h-96 lg:w-[32rem] lg:h-[32rem] xl:w-[36rem] xl:h-[36rem] relative">
                  <img 
                    src="/src/assets/ChatGPT Image Aug 12, 2025, 12_54_32 AM.png" 
                    alt="AI-powered educator training visualization" 
                    className="w-full h-full object-contain relative z-10"
                  />
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