import React, { useState } from 'react'
import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/24/outline'

const TestimonialsSection: React.FC = () => {
  const [currentTestimonial, setCurrentTestimonial] = useState(0)

  const testimonials = [
    {
      name: 'Ada Eze',
      role: 'Primary School Teacher',
      location: 'Lagos',
      avatar: '👩‍🏫',
      content: 'Awade\'s personalized courses transformed my teaching in Nigeria\'s crowded classrooms. The AI-driven recommendations perfectly matched my needs, boosting my confidence. I\'m now engaging my students like never before!'
    },
    {
      name: 'Kwame Mensah',
      role: 'Secondary School Teacher',
      location: 'Accra',
      avatar: '👨‍🏫',
      content: 'The culturally relevant content made all the difference. I can now connect with my students using examples they understand and relate to their daily lives.'
    },
    {
      name: 'Fatima Hassan',
      role: 'Mathematics Teacher',
      location: 'Nairobi',
      avatar: '👩‍🏫',
      content: 'The AI-powered lesson planning has saved me hours of preparation time. The suggestions are always spot-on and culturally appropriate for my Kenyan students.'
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
              What Educators are saying
            </h2>
            <div className="flex-1 h-px bg-gray-300"></div>
          </div>
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
                    {testimonials[currentTestimonial].role} from {testimonials[currentTestimonial].location}
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