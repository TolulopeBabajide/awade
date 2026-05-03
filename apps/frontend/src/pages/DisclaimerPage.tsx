import React from 'react'
import { useNavigate } from 'react-router-dom'
import { FaArrowLeft, FaRobot, FaExclamationTriangle, FaShieldAlt, FaEnvelope } from 'react-icons/fa'

/**
 * DisclaimerPage — AI content disclaimer
 *
 * Required by:
 * - EU AI Act Art. 52 (transparency obligation for AI-generated content)
 * - GDPR Art. 5(1)(a) (transparency principle)
 *
 * Linked from the educator resource editor (EditLessonResourcePage) and
 * the parent guide viewer (GuideViewPage) via the "/disclaimer" route.
 *
 * AWD-GRC-07
 */
const DisclaimerPage: React.FC = () => {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-background-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        {/* Back navigation */}
        <button
          onClick={() => navigate(-1)}
          className="inline-flex items-center gap-2 text-sm font-medium text-gray-500 hover:text-primary-600 transition-colors mb-8"
        >
          <FaArrowLeft className="w-3 h-3" />
          Back
        </button>

        {/* Page header */}
        <div className="flex items-center gap-3 mb-8">
          <div className="w-10 h-10 bg-accent-100 rounded-full flex items-center justify-center flex-shrink-0">
            <FaRobot className="w-5 h-5 text-accent-700" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-primary-800">AI Content Disclaimer</h1>
            <p className="text-sm text-gray-500 mt-0.5">
              How Awade uses artificial intelligence
            </p>
          </div>
        </div>

        <div className="space-y-6">
          {/* What is AI-generated content */}
          <Card
            icon={<FaRobot className="w-5 h-5 text-accent-600" />}
            title="What is AI-generated content?"
          >
            <p className="text-gray-700 text-sm leading-relaxed">
              Awade uses large language models (AI) to generate parent guides and educator resources.
              The AI creates personalised content based on your child's curriculum, grade level, and
              subject — but it does not have access to your child's individual school records,
              teacher assessments, or real-time classroom data.
            </p>
          </Card>

          {/* Accuracy and limitations */}
          <Card
            icon={<FaExclamationTriangle className="w-5 h-5 text-orange-500" />}
            title="Accuracy and limitations"
          >
            <p className="text-gray-700 text-sm leading-relaxed mb-3">
              AI-generated content may contain inaccuracies, outdated information, or suggestions
              that are not suitable for your child's specific learning needs. You should:
            </p>
            <ul className="space-y-2 text-sm text-gray-700">
              <li className="flex items-start gap-2">
                <span className="text-accent-600 mt-0.5 flex-shrink-0">•</span>
                Review all content before relying on it for educational decisions.
              </li>
              <li className="flex items-start gap-2">
                <span className="text-accent-600 mt-0.5 flex-shrink-0">•</span>
                Cross-reference with your child's teacher if you have specific concerns.
              </li>
              <li className="flex items-start gap-2">
                <span className="text-accent-600 mt-0.5 flex-shrink-0">•</span>
                Use your own judgement — you know your child best.
              </li>
            </ul>
          </Card>

          {/* EU AI Act transparency notice */}
          <Card
            icon={<FaShieldAlt className="w-5 h-5 text-blue-500" />}
            title="Transparency notice (EU AI Act Art. 52)"
          >
            <p className="text-gray-700 text-sm leading-relaxed">
              In accordance with Article 52 of the EU AI Act, Awade discloses that content marked
              as "AI-generated" was created by an automated system, not a human expert. This
              disclosure applies to all parent guides and educator resources produced by the Awade
              platform.
            </p>
            <p className="text-gray-700 text-sm leading-relaxed mt-3">
              Awade does not use AI for any automated decision-making that produces legal or
              similarly significant effects on individuals.
            </p>
          </Card>

          {/* Data and privacy */}
          <Card
            icon={<FaShieldAlt className="w-5 h-5 text-primary-600" />}
            title="Your data and privacy"
          >
            <p className="text-gray-700 text-sm leading-relaxed">
              When generating content, Awade sends your child's grade level, curriculum, and subject
              to our AI provider. We do not send your child's name, personal details, or any
              identifying information. Our AI provider processes this data in accordance with our
              data processing agreement.
            </p>
            <p className="text-gray-700 text-sm leading-relaxed mt-3">
              For full details, see our{' '}
              <a
                href="/privacy-policy"
                className="text-primary-600 underline hover:text-primary-700 font-medium"
              >
                Privacy Policy
              </a>
              .
            </p>
          </Card>

          {/* Contact */}
          <div className="bg-gray-50 border border-gray-200 rounded-2xl px-5 py-4 flex items-start gap-3">
            <FaEnvelope className="w-4 h-4 text-gray-500 mt-0.5 flex-shrink-0" />
            <p className="text-sm text-gray-600">
              Questions about how Awade uses AI?{' '}
              <a
                href="mailto:hello@awade.app"
                className="text-primary-600 underline hover:text-primary-700 font-medium"
              >
                Contact us
              </a>
              .
            </p>
          </div>
        </div>

        {/* Footer note */}
        <p className="text-xs text-gray-400 text-center mt-8">
          Last updated: May 2026 · Awade AI Disclaimer v1.0
        </p>
      </div>
    </div>
  )
}

// ── Reusable card ──────────────────────────────────────────────────

interface CardProps {
  icon: React.ReactNode
  title: string
  children: React.ReactNode
}

const Card: React.FC<CardProps> = ({ icon, title, children }) => (
  <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden">
    <div className="px-5 py-4 border-b border-gray-100 flex items-center gap-3">
      {icon}
      <h2 className="font-semibold text-gray-800">{title}</h2>
    </div>
    <div className="px-5 py-4">{children}</div>
  </div>
)

export default DisclaimerPage
