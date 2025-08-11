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
        <section id="contact" className="section-padding bg-gray-50">
          <div className="container-custom text-center">
            <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Get in Touch
            </h2>
            <p className="text-base lg:text-lg text-gray-600 max-w-2xl mx-auto">
              Have questions about Awade? We'd love to hear from you.
            </p>
            <div className="mt-6">
              <a 
                href="mailto:contact@awade.com" 
                className="btn-accent inline-block"
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