import React from 'react'
import Header from '../components/Header'
import HeroSectionParent from '../components/HeroSectionParent'
import FeaturesSectionParent from '../components/FeaturesSectionParent'
import HowItWorksSection from '../components/HowItWorksSection'
import Footer from '../components/Footer'

const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-white">
      <main>
        <Header />
        <HeroSectionParent />
        <FeaturesSectionParent />
        <HowItWorksSection />
      </main>
      <Footer />
    </div>
  )
}

export default LandingPage 