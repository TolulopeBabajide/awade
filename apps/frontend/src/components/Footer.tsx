import React, { useState } from 'react'
import { FaFacebook, FaTwitter, FaInstagram, FaLinkedin } from 'react-icons/fa'

const Footer: React.FC = () => {
  const [email, setEmail] = useState('')

  const handleSubscribe = (e: React.FormEvent) => {
    e.preventDefault()
    // Handle subscription logic here
    console.log('Subscribing email:', email)
    setEmail('')
  }

  return (
    <footer className="bg-primary-800 text-white" role="contentinfo">
      <div className="container-custom py-6 lg:py-12 px-4 sm:px-6 lg:px-8">
        {/* Mobile Layout - Essential Elements Only */}
        <div className="md:hidden">
          <div className="flex flex-col items-center space-y-6 text-center">
            {/* Logo and Description */}
            <div className="space-y-3">
              <div className="flex items-center justify-center space-x-2">
                {/* <h3 className="text-lg text-white font-bold">
                  <a href="#home" className="text-lg text-white font-bold" aria-label="Awade - Go to homepage">
                    Awade
                  </a>
                </h3> */}
              </div>
              <p className="text-sm text-white leading-relaxed max-w-xs">
                AI-powered lesson planning platform for African teachers.
              </p>
            </div>

            {/* Essential Links */}
            <div className="flex flex-wrap justify-center gap-6">
              <a 
                href="#about" 
                className="text-sm text-white hover:text-white transition-colors duration-200"
              >
                About
              </a>
              <a 
                href="#contact" 
                className="text-sm text-white hover:text-white transition-colors duration-200"
              >
                Contact
              </a>
              <a 
                href="#features" 
                className="text-sm text-white hover:text-white transition-colors duration-200"
              >
                Features
              </a>
            </div>

            {/* Copyright */}
            <p className="text-xs text-white">
              Awade 2025 | All rights reserved
            </p>
          </div>
        </div>

        {/* Desktop Layout - Full Content */}
        <div className="hidden md:grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {/* Left Section - Logo and Description */}
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <h3 className="text-xl lg:text-2xl font-bold">
                <a href="#home" aria-label="Awade - Go to homepage">
                  Awade
                </a>
              </h3>
              
            </div>
            <p className="text-sm lg:text-base text-white leading-relaxed">
              AI-powered lesson planning platform designed specifically for African teachers. 
              Transform your teaching with intelligent, curriculum-aligned lesson plans.
            </p>
            <p className="text-xs lg:text-sm text-white">
              Awade 2025 | All rights reserved
            </p>
          </div>

          {/* Middle Section - Links */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 lg:gap-8">
            {/* Company Links */}
            <div>
              <h4 className="font-semibold text-base lg:text-lg mb-3 lg:mb-4 text-white">Company</h4>
              <ul className="space-y-2" role="list">
                <li>
                  <a 
                    href="#about" 
                    className="text-sm lg:text-base text-white hover:text-white transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-primary-800 rounded"
                  >
                    About Awade
                  </a>
                </li>
                <li>
                  <a 
                    href="#contact" 
                    className="text-sm lg:text-base text-white hover:text-white transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-primary-800 rounded"
                  >
                    Contact Us
                  </a>
                </li>
                <li>
                  <a 
                    href="#features" 
                    className="text-sm lg:text-base text-white hover:text-white transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-primary-800 rounded"
                  >
                    Features
                  </a>
                </li>
              </ul>
            </div>
          </div>

          {/* Right Section - Social Media and Newsletter */}
          <div className="space-y-6">
            {/* Social Media */}
            <div>
              <h4 className="font-semibold text-base lg:text-lg mb-3 lg:mb-4 text-white">Follow Us</h4>
              <div className="flex space-x-3 lg:space-x-4">
                <a 
                  href="#" 
                  className="w-8 h-8 lg:w-10 lg:h-10 flex items-center justify-center hover:text-accent-400 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-primary-800"
                  aria-label="Follow us on Facebook"
                >
                  <FaFacebook className="w-5 h-5 lg:w-6 lg:h-6" />
                </a>
                <a 
                  href="#" 
                  className="w-8 h-8 lg:w-10 lg:h-10 flex items-center justify-center hover:text-accent-400 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-primary-800"
                  aria-label="Follow us on Twitter"
                >
                  <FaTwitter className="w-5 h-5 lg:w-6 lg:h-6" />
                </a>
                <a 
                  href="#" 
                  className="w-8 h-8 lg:w-10 lg:h-10 flex items-center justify-center hover:text-accent-400 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-primary-800"
                  aria-label="Follow us on Instagram"
                >
                  <FaInstagram className="w-5 h-5 lg:w-6 lg:h-6" />
                </a>
                <a 
                  href="#" 
                  className="w-8 h-8 lg:w-10 lg:h-10 flex items-center justify-center hover:text-accent-400 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-primary-800"
                  aria-label="Follow us on LinkedIn"
                >
                  <FaLinkedin className="w-5 h-5 lg:w-6 lg:h-6" />
                </a>
              </div>
            </div>

            {/* Newsletter */}
            <div>
              <h4 className="font-semibold text-base lg:text-lg mb-3 lg:mb-4 text-white">Join Our Community</h4>
              <form onSubmit={handleSubscribe} className="space-y-3">
                <label htmlFor="newsletter-email" className="sr-only">
                  Email address for newsletter subscription
                </label>
                <input
                  id="newsletter-email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email"
                  className="w-full px-3 lg:px-4 py-2 lg:py-3 bg-primary-700 border border-primary-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-transparent text-sm lg:text-base"
                  required
                  aria-describedby="newsletter-description"
                />
                <p id="newsletter-description" className="sr-only">
                  Subscribe to our newsletter for updates and tips
                </p>
                <button
                  type="submit"
                  className="w-full bg-accent-500 hover:bg-accent-600 text-white font-medium py-2 lg:py-3 px-4 lg:px-6 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:ring-offset-2 focus:ring-offset-primary-800 text-sm lg:text-base"
                >
                  Subscribe
                </button>
              </form>
            </div>
          </div>
        </div>

        {/* Bottom Section - Desktop Only */}
        <div className="hidden md:block border-t border-primary-700 mt-6 lg:mt-8 pt-6 lg:pt-8 text-center">
          <a 
            href="#terms" 
            className="text-xs lg:text-sm text-white hover:text-white transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-primary-800 rounded"
          >
            Terms & Conditions
          </a>
        </div>
      </div>
    </footer>
  )
}

export default Footer 