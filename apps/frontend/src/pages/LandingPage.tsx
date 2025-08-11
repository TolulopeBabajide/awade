import React from 'react'
import Header from '../components/Header'
import HeroSection from '../components/HeroSection'
import WhyAwadeSection from '../components/WhyAwadeSection'
import FeaturesSection from '../components/FeaturesSection'
import Footer from '../components/Footer'

const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-white">
      <Header />
      <main>
        <HeroSection />
        <WhyAwadeSection />
        <FeaturesSection />
        {/* Contact section placeholder for navigation */}
        <section id="contact" className="section-padding bg-white">
          <div className="container-custom text-center">
            <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold text-primary-900 mb-4">
              Get in Touch
            </h2>
            <p className="text-base lg:text-lg text-background-600 max-w-2xl mx-auto">
              Have questions about Awade? We'd love to hear from you.
            </p>
            <div className="mt-6">
              <a 
                href="mailto:contact@awade.com" 
                className="bg-accent-500 hover:bg-accent-600 text-white font-medium py-3 px-6 rounded-lg transition-all duration-200 transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:ring-offset-2 inline-block"
                aria-label="Send us an email"
              >
                Contact Us
              </a>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  )
}

export default LandingPage 