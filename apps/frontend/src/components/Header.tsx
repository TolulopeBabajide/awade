import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { ChevronDownIcon, Bars3Icon, XMarkIcon } from '@heroicons/react/24/outline'

const Header: React.FC = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  const navigation = [
    { name: 'Home', href: '#home' },
    { name: 'Features', href: '#features' },
  ]

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen)
  }

  const closeMenu = () => {
    setIsMenuOpen(false)
  }

  return (
    <header className="bg-white shadow-sm sticky top-0 z-50 border-b border-background-200">
      <div className="container-custom">
        <div className="flex items-center justify-between h-16 px-4 sm:px-6 lg:px-8">
          {/* Logo */}
          <div className="flex-shrink-0">
            <h1 className="text-xl sm:text-2xl font-bold text-primary-800">
              <a href="#home" aria-label="Awade - Go to homepage">
                Awade
              </a>
            </h1>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8 lg:space-x-12" role="navigation" aria-label="Main navigation">
            {navigation.map((item) => (
              <a
                key={item.name}
                href={item.href}
                className="text-background-700 hover:text-primary-600 px-3 py-2 text-sm font-medium transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 rounded-md"
              >
                {item.name}
              </a>
            ))}
          </nav>

          {/* CTA Button */}
          <div className="hidden md:block ml-8 lg:ml-12">
            <Link 
              to="/signup"
              className="btn-accent focus:outline-none focus:ring-2 focus:ring-accent-600 focus:ring-offset-2"
              aria-label="Get started with Awade"
            >
              Get Started
            </Link>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={toggleMenu}
              className="text-gray-700 hover:text-primary-600 p-2 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
              aria-expanded={isMenuOpen}
              aria-label={isMenuOpen ? 'Close menu' : 'Open menu'}
            >
              {isMenuOpen ? (
                <XMarkIcon className="h-6 w-6" aria-hidden="true" />
              ) : (
                <Bars3Icon className="h-6 w-6" aria-hidden="true" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden" role="navigation" aria-label="Mobile navigation">
            <div className="px-4 pt-4 pb-6 space-y-3 bg-white border-t border-gray-200">
              {navigation.map((item) => (
                <a
                  key={item.name}
                  href={item.href}
                  className="text-gray-700 hover:text-primary-600 block px-3 py-3 text-base font-medium transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 rounded-md"
                  onClick={closeMenu}
                >
                  {item.name}
                </a>
              ))}
              <div className="pt-4">
                <Link 
                  to="/signup"
                  className="btn-accent w-full focus:outline-none focus:ring-2 focus:ring-accent-500 focus:ring-offset-2"
                  onClick={closeMenu}
                  aria-label="Get started with Awade"
                >
                  Get Started
                </Link>
              </div>
            </div>
          </div>
        )}
      </div>
    </header>
  )
}

export default Header 