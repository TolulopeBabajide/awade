import React, { useState } from 'react'

const Footer: React.FC = () => {
  const [email, setEmail] = useState('')

  const handleSubscribe = (e: React.FormEvent) => {
    e.preventDefault()
    // Handle subscription logic here
    console.log('Subscribing email:', email)
    setEmail('')
  }

  return (
    <footer className="bg-primary-800 text-white">
      <div className="container-custom py-12">
        <div className="grid md:grid-cols-3 gap-8">
          {/* Left Section - Logo and Description */}
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <h3 className="text-2xl font-bold">Awade</h3>
              <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center">
                <span className="text-primary-800 text-lg">🤖</span>
              </div>
            </div>
            <p className="text-gray-300 leading-relaxed">
              AI-powered educator support platform designed specifically for African teachers. 
              Transform your teaching with culturally relevant, personalized training.
            </p>
            <p className="text-gray-400 text-sm">
              Awade 2025 | All rights reserved
            </p>
          </div>

          {/* Middle Section - Links */}
          <div className="grid grid-cols-2 gap-8">
            {/* Company Links */}
            <div>
              <h4 className="font-semibold text-lg mb-4">Company</h4>
              <ul className="space-y-2">
                <li>
                  <a href="#about" className="text-gray-300 hover:text-white transition-colors duration-200">
                    About Awade
                  </a>
                </li>
                <li>
                  <a href="#contact" className="text-gray-300 hover:text-white transition-colors duration-200">
                    Contact Us
                  </a>
                </li>
                <li>
                  <a href="#testimonials" className="text-gray-300 hover:text-white transition-colors duration-200">
                    Testimonies
                  </a>
                </li>
              </ul>
            </div>

            {/* Resources Links */}
            <div>
              <h4 className="font-semibold text-lg mb-4">Resources</h4>
              <ul className="space-y-2">
                <li>
                  <a href="#about" className="text-gray-300 hover:text-white transition-colors duration-200">
                    About Us
                  </a>
                </li>
                <li>
                  <a href="#courses" className="text-gray-300 hover:text-white transition-colors duration-200">
                    Courses
                  </a>
                </li>
                <li>
                  <a href="#classroom" className="text-gray-300 hover:text-white transition-colors duration-200">
                    My Classroom
                  </a>
                </li>
              </ul>
            </div>
          </div>

          {/* Right Section - Social Media and Newsletter */}
          <div className="space-y-6">
            {/* Social Media */}
            <div>
              <h4 className="font-semibold text-lg mb-4">Follow Us</h4>
              <div className="flex space-x-4">
                <a href="#" className="w-10 h-10 bg-primary-700 rounded-full flex items-center justify-center hover:bg-primary-600 transition-colors duration-200">
                  <span className="text-white">📘</span>
                </a>
                <a href="#" className="w-10 h-10 bg-primary-700 rounded-full flex items-center justify-center hover:bg-primary-600 transition-colors duration-200">
                  <span className="text-white">🐦</span>
                </a>
                <a href="#" className="w-10 h-10 bg-primary-700 rounded-full flex items-center justify-center hover:bg-primary-600 transition-colors duration-200">
                  <span className="text-white">📷</span>
                </a>
                <a href="#" className="w-10 h-10 bg-primary-700 rounded-full flex items-center justify-center hover:bg-primary-600 transition-colors duration-200">
                  <span className="text-white">💼</span>
                </a>
              </div>
            </div>

            {/* Newsletter */}
            <div>
              <h4 className="font-semibold text-lg mb-4">Join Our Community</h4>
              <form onSubmit={handleSubscribe} className="space-y-3">
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email"
                  className="w-full px-4 py-3 bg-primary-700 border border-primary-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-transparent"
                  required
                />
                <button
                  type="submit"
                  className="w-full bg-accent-500 hover:bg-accent-600 text-white font-medium py-3 px-6 rounded-lg transition-colors duration-200"
                >
                  Subscribe
                </button>
              </form>
            </div>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="border-t border-primary-700 mt-8 pt-8 text-center">
          <a href="#terms" className="text-gray-400 hover:text-white transition-colors duration-200">
            Terms & Conditions
          </a>
        </div>
      </div>
    </footer>
  )
}

export default Footer 