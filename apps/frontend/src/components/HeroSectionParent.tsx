import React from 'react'
import { Link } from 'react-router-dom'
import { useIntersectionObserver } from '../hooks/useIntersectionObserver'

const HeroSectionParent: React.FC = () => {
  const { ref, isVisible } = useIntersectionObserver({
    threshold: 0.1,
    freezeOnceVisible: true,
  })

  return (
    <section
      id="home"
      className="hero-gradient pb-16 px-4 sm:px-6 lg:px-8 min-h-[60vh] lg:min-h-[70vh] flex items-center"
      aria-labelledby="hero-heading"
      ref={ref}
    >
      <div className="container-custom w-full">
        <div className="grid lg:grid-cols-2 gap-8 lg:gap-12 items-center">
          {/* Left Content */}
          <div className={`space-y-6 lg:space-y-8 order-2 lg:order-1 transition-opacity duration-1000 ${isVisible ? 'opacity-100' : 'opacity-0'}`}>
            {/* Badge */}
            <div className={`inline-flex items-center px-3 py-1.5 bg-primary-100 text-primary-700 rounded-full text-sm font-medium ${isVisible ? 'animate-fade-in' : ''}`}>
              <span className="w-2 h-2 bg-primary-600 rounded-full mr-2" aria-hidden="true"></span>
              For Parents Who Want to Help
            </div>

            {/* Headline */}
            <h1
              id="hero-heading"
              className={`text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold text-primary-800 leading-tight ${isVisible ? 'animate-slide-up' : ''}`}
              style={{ animationDelay: '0.2s' }}
            >
              Understand what your child is learning.
              <span className="text-accent-600"> Help them at home.</span>
            </h1>

            {/* Description */}
            <p
              className={`text-base sm:text-lg lg:text-xl text-gray-700 leading-relaxed max-w-xl ${isVisible ? 'animate-slide-up' : ''}`}
              style={{ animationDelay: '0.4s' }}
            >
              Awade gives you simple, practical guides matched to your child's exact curriculum — so you can support their homework, even if you haven't studied the topic in years.
            </p>

            {/* CTA Buttons */}
            <div
              className={`flex flex-col sm:flex-row gap-3 lg:gap-4 ${isVisible ? 'animate-slide-up' : ''}`}
              style={{ animationDelay: '0.6s' }}
            >
              <Link
                to="/signup"
                className="bg-accent-600 hover:bg-accent-700 text-white font-semibold py-3 px-8 rounded-xl transition-all duration-200 transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:ring-offset-2 text-base lg:text-lg text-center shadow-md"
                aria-label="Sign up as a parent"
              >
                Get Started Free
              </Link>
              <a
                href="#how-it-works"
                className="border-2 border-primary-300 hover:border-primary-500 text-primary-700 font-medium py-3 px-8 rounded-xl transition-all duration-200 text-base lg:text-lg text-center"
              >
                See How It Works
              </a>
            </div>

            {/* Trust signal */}
            <p className={`text-sm text-gray-500 ${isVisible ? 'animate-fade-in' : ''}`} style={{ animationDelay: '1s' }}>
              Aligned with Nigerian, Ghanaian & Kenyan national curricula
            </p>
          </div>

          {/* Right Content */}
          <div className={`hidden md:block relative order-1 lg:order-2 ${isVisible ? 'animate-fade-in' : 'opacity-0'}`} style={{ animationDelay: '0.8s' }}>
            <div className="relative w-full flex items-center justify-center">
              <div className="w-80 lg:w-[28rem] xl:w-[32rem]">
                <img
                  src="/assets/ChatGPT Image Aug 12, 2025, 12_54_32 AM.png"
                  alt="Parent and child learning together"
                  className="w-full h-full object-contain"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

export default HeroSectionParent
