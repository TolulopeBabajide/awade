import React, { useState } from 'react'
import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/24/outline'

const TestimonialsSection: React.FC = () => {
  const [currentTestimonial, setCurrentTestimonial] = useState(0)

  const testimonials = [
    {
      name: 'Ada Eze',
      role: 'Primary School Teacher',
      location: 'Lagos, Nigeria',
      avatar: '👩‍🏫',
      content: 'Awade has revolutionized my lesson planning! I used to spend hours creating lessons, but now I generate comprehensive plans in minutes. The AI understands our Nigerian curriculum perfectly and includes local examples my students can relate to.'
    },
    {
      name: 'Kwame Mensah',
      role: 'Secondary School Teacher',
      location: 'Accra, Ghana',
      avatar: '👨‍🏫',
      content: 'The curriculum alignment feature is incredible. I no longer worry about missing key learning objectives. Awade automatically ensures my lessons cover everything required by the Ghanaian education standards.'
    },
    {
      name: 'Fatima Hassan',
      role: 'Mathematics Teacher',
      location: 'Nairobi, Kenya',
      avatar: '👩‍🏫',
      content: 'What I love most is how Awade adapts to my local context. It suggests activities using resources available in my community and examples from Kenyan culture. My students are much more engaged now!'
    }
  ]

  const nextTestimonial = () => {
    setCurrentTestimonial((prev) => (prev + 1) % testimonials.length)
  }

  const prevTestimonial = () => {
    setCurrentTestimonial((prev) => (prev - 1 + testimonials.length) % testimonials.length)
  }

  return (
    <section id="testimonials" className="section-padding bg-gray-50">
      <div className="container-custom">
        {/* Section Heading */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-8">
            <div className="flex-1 h-px bg-gray-300"></div>
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 px-8">
              What Teachers Are Saying
            </h2>
            <div className="flex-1 h-px bg-gray-300"></div>
          </div>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Hear from educators across Africa who are using Awade to transform their lesson planning
          </p>
        </div>

        {/* Testimonial Card */}
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-2xl shadow-xl p-8 md:p-12 relative">
            {/* Quote Icon */}
            <div className="absolute top-6 left-6 text-6xl text-primary-200">
              "
            </div>

            <div className="flex flex-col md:flex-row items-center md:items-start gap-8">
              {/* Avatar */}
              <div className="flex-shrink-0">
                <div className="w-20 h-20 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full flex items-center justify-center text-3xl text-white">
                  {testimonials[currentTestimonial].avatar}
                </div>
              </div>

              {/* Content */}
              <div className="flex-1 text-center md:text-left">
                <p className="text-lg md:text-xl text-gray-700 leading-relaxed mb-6">
                  {testimonials[currentTestimonial].content}
                </p>
                
                <div className="text-center md:text-left">
                  <h4 className="font-bold text-gray-900 text-lg">
                    {testimonials[currentTestimonial].name}
                  </h4>
                  <p className="text-gray-600">
                    {testimonials[currentTestimonial].role} • {testimonials[currentTestimonial].location}
                  </p>
                </div>
              </div>
            </div>

            {/* Navigation Arrows */}
            <div className="absolute top-1/2 -translate-y-1/2 left-4 md:left-8">
              <button
                onClick={prevTestimonial}
                className="w-10 h-10 bg-white rounded-full shadow-lg flex items-center justify-center text-gray-600 hover:text-primary-600 transition-colors duration-200"
              >
                <ChevronLeftIcon className="w-6 h-6" />
              </button>
            </div>

            <div className="absolute top-1/2 -translate-y-1/2 right-4 md:right-8">
              <button
                onClick={nextTestimonial}
                className="w-10 h-10 bg-white rounded-full shadow-lg flex items-center justify-center text-gray-600 hover:text-primary-600 transition-colors duration-200"
              >
                <ChevronRightIcon className="w-6 h-6" />
              </button>
            </div>

            {/* Dots Indicator */}
            <div className="flex justify-center mt-8 space-x-2">
              {testimonials.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentTestimonial(index)}
                  className={`w-3 h-3 rounded-full transition-colors duration-200 ${
                    index === currentTestimonial ? 'bg-primary-600' : 'bg-gray-300'
                  }`}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

export default TestimonialsSection 