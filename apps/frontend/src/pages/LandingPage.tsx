import React from 'react'
import Header from '../components/Header'
import HeroSectionParent from '../components/HeroSectionParent'
import FeaturesSectionParent from '../components/FeaturesSectionParent'
import HowItWorksSection from '../components/HowItWorksSection'
import ConceptExplorer from '../components/learning/ConceptExplorer'
import Footer from '../components/Footer'

const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-white">
      <main>
        <Header />
        <HeroSectionParent />
        <section id="explore-concepts" className="bg-primary-50 py-12 sm:py-20 px-4 scroll-mt-6">
          <div className="max-w-5xl mx-auto grid lg:grid-cols-2 gap-8 items-start">
            <div className="lg:pt-8"><h2 className="text-3xl font-semibold mb-4">A little discovery goes a long way.</h2><p className="text-gray-600 leading-relaxed">Move beyond reading an explanation. Change the parts of a fraction, see what happens, and talk about why. Parents and teachers can explore ideas alongside the people they help learn.</p><p className="text-sm text-primary-700 mt-4">Try this activity. No account needed.</p></div>
            <ConceptExplorer conceptId="fractions" />
          </div>
        </section>
        <FeaturesSectionParent />
        <HowItWorksSection />
      </main>
      <Footer />
    </div>
  )
}

export default LandingPage 