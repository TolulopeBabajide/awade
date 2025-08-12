import React from 'react'
import Header from '../components/Header'
import HeroSection from '../components/HeroSection'
import FeaturesSection from '../components/FeaturesSection'
import Footer from '../components/Footer'

const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-white">
      <Header />
      <main>
        <HeroSection />
        <FeaturesSection />
      </main>
      <Footer />
    </div>
  )
}

export default LandingPage 