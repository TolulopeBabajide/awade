import React from 'react'
import { Link } from 'react-router-dom'

const HeroSection: React.FC = () => {
  return (
    <section id="home" className="section-padding gradient-bg">
      <div className="container-custom">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left Content */}
          <div className="space-y-8 animate-fade-in">
            {/* Badge */}
            <div className="inline-flex items-center px-4 py-2 bg-primary-100 text-primary-700 rounded-full text-sm font-medium">
              <span className="w-2 h-2 bg-primary-500 rounded-full mr-2"></span>
              AI Powered Educator Training
            </div>

            {/* Headline */}
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 leading-tight">
              Transform Your Teaching with{' '}
              <span className="text-gradient">Awade</span>
            </h1>

            {/* Description */}
            <p className="text-xl text-gray-600 leading-relaxed">
              Unlock AI-Powered, Culturally Tailored Training to Elevate Your Teaching Journey as an African Educator.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4">
              <Link to="/signup" className="btn-accent text-lg px-8 py-4 text-center">
                Get Started
              </Link>
              <button className="btn-secondary text-lg px-8 py-4">
                Learn More
              </button>
            </div>
          </div>

          {/* Right Content - AI Robot with Network */}
          <div className="relative animate-slide-up">
            <div className="relative w-full h-96 lg:h-[500px] flex items-center justify-center">
              {/* Background Circle */}
              <div className="absolute inset-0 bg-gradient-to-br from-primary-100 to-accent-100 rounded-full opacity-50"></div>
              
              {/* AI Robot */}
              <div className="relative z-10">
                <div className="w-48 h-48 lg:w-64 lg:h-64 bg-white rounded-full shadow-2xl flex items-center justify-center border-4 border-primary-200">
                  {/* Robot Face */}
                  <div className="w-32 h-32 lg:w-40 lg:h-40 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center">
                    <div className="grid grid-cols-2 gap-2">
                      <div className="w-3 h-3 bg-white rounded-full animate-pulse"></div>
                      <div className="w-3 h-3 bg-white rounded-full animate-pulse"></div>
                      <div className="w-3 h-3 bg-white rounded-full animate-pulse"></div>
                      <div className="w-3 h-3 bg-white rounded-full animate-pulse"></div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Educator Network */}
              <div className="absolute inset-0">
                {/* Connection Lines */}
                <svg className="absolute inset-0 w-full h-full" viewBox="0 0 400 400">
                  {/* Lines connecting robot to educators */}
                  <line x1="200" y1="200" x2="100" y2="100" stroke="#3B82F6" strokeWidth="2" opacity="0.3"/>
                  <line x1="200" y1="200" x2="300" y2="100" stroke="#3B82F6" strokeWidth="2" opacity="0.3"/>
                  <line x1="200" y1="200" x2="100" y2="300" stroke="#3B82F6" strokeWidth="2" opacity="0.3"/>
                  <line x1="200" y1="200" x2="300" y2="300" stroke="#3B82F6" strokeWidth="2" opacity="0.3"/>
                  <line x1="200" y1="200" x2="50" y2="200" stroke="#3B82F6" strokeWidth="2" opacity="0.3"/>
                  <line x1="200" y1="200" x2="350" y2="200" stroke="#3B82F6" strokeWidth="2" opacity="0.3"/>
                </svg>

                {/* Educator Avatars */}
                <div className="absolute top-8 left-8 w-12 h-12 bg-gradient-to-br from-accent-400 to-accent-600 rounded-full flex items-center justify-center text-white font-bold text-sm animate-bounce-gentle">
                  A
                </div>
                <div className="absolute top-8 right-8 w-12 h-12 bg-gradient-to-br from-secondary-400 to-secondary-600 rounded-full flex items-center justify-center text-white font-bold text-sm animate-bounce-gentle" style={{animationDelay: '0.5s'}}>
                  B
                </div>
                <div className="absolute bottom-8 left-8 w-12 h-12 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full flex items-center justify-center text-white font-bold text-sm animate-bounce-gentle" style={{animationDelay: '1s'}}>
                  C
                </div>
                <div className="absolute bottom-8 right-8 w-12 h-12 bg-gradient-to-br from-success-400 to-success-600 rounded-full flex items-center justify-center text-white font-bold text-sm animate-bounce-gentle" style={{animationDelay: '1.5s'}}>
                  D
                </div>
                <div className="absolute top-1/2 left-4 transform -translate-y-1/2 w-12 h-12 bg-gradient-to-br from-warning-400 to-warning-600 rounded-full flex items-center justify-center text-white font-bold text-sm animate-bounce-gentle" style={{animationDelay: '0.75s'}}>
                  E
                </div>
                <div className="absolute top-1/2 right-4 transform -translate-y-1/2 w-12 h-12 bg-gradient-to-br from-error-400 to-error-600 rounded-full flex items-center justify-center text-white font-bold text-sm animate-bounce-gentle" style={{animationDelay: '1.25s'}}>
                  F
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