import React, { useMemo, useState } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  FaArrowLeft,
  FaBookmark,
  FaRegBookmark,
  FaLightbulb,
  FaComments,
  FaExclamationTriangle,
  FaChalkboardTeacher,
  FaHeart,
  FaHome,
  FaWhatsapp,
  FaDownload,
} from 'react-icons/fa'
import apiService from '../services/api'
import Sidebar from '../components/Sidebar'
import MobileNavigation from '../components/MobileNavigation'
import type { ParentGuide, ParentGuideContent } from '../types/children'

const GuideViewPage: React.FC = () => {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const childId = Number(searchParams.get('child'))
  const topicId = Number(searchParams.get('topic'))
  const guideIdParam = searchParams.get('guide')

  // Generate guide (if navigating from topic browser)
  const {
    data: guide,
    isLoading,
    error,
  } = useQuery<ParentGuide>({
    queryKey: ['parentGuide', childId, topicId, guideIdParam],
    queryFn: async () => {
      if (guideIdParam) {
        const res = await apiService.getGuide(Number(guideIdParam))
        if (res.error) throw new Error(res.error)
        if (!res.data) throw new Error('No guide data returned')
        return res.data
      }
      // Generate new guide
      const res = await apiService.generateGuide(childId, topicId)
      if (res.error) throw new Error(res.error)
      if (!res.data) throw new Error('No guide data returned')
      return res.data
    },
    enabled: !!(childId && topicId) || !!guideIdParam,
  })

  // Parse guide content
  const content = useMemo<ParentGuideContent | null>(() => {
    if (!guide?.ai_generated_content) return null
    try {
      return JSON.parse(guide.ai_generated_content)
    } catch {
      return null
    }
  }, [guide?.ai_generated_content])

  // Bookmark mutation
  const bookmarkMutation = useMutation({
    mutationFn: () => apiService.toggleGuideBookmark(guide!.guide_id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['parentGuide'] })
      queryClient.invalidateQueries({ queryKey: ['childGuides'] })
    },
  })

  // PDF download state
  const [isDownloading, setIsDownloading] = useState(false)

  const handleDownloadPdf = async () => {
    if (!guide || isDownloading) return
    setIsDownloading(true)
    try {
      const result = await apiService.exportGuidePdf(guide.guide_id)
      if ('error' in result) {
        // Non-blocking — show a brief alert rather than a full error page
        alert(`Could not download PDF: ${result.error}`)
        return
      }
      const url = URL.createObjectURL(result.blob)
      const anchor = document.createElement('a')
      anchor.href = url
      anchor.download = result.filename
      anchor.click()
      URL.revokeObjectURL(url)
    } finally {
      setIsDownloading(false)
    }
  }

  // ── Loading state ─────────────────────────────────────────────────
  if (isLoading) {
    return (
      <div className="flex min-h-screen bg-background-50">
        <Sidebar currentPage="dashboard" />
        <main className="flex-1 lg:ml-64 flex items-center justify-center">
          <div role="status" aria-live="polite" className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4" />
            <p className="text-gray-600 font-medium">Generating your guide...</p>
            <p className="text-gray-400 text-sm mt-1">This may take a few seconds</p>
          </div>
        </main>
        <MobileNavigation currentPage="dashboard" />
      </div>
    )
  }

  // ── Error state ───────────────────────────────────────────────────
  if (error || !content) {
    return (
      <div className="flex min-h-screen bg-background-50">
        <Sidebar currentPage="dashboard" />
        <main className="flex-1 lg:ml-64 flex items-center justify-center">
          <div className="text-center max-w-md px-4">
            <p className="text-red-500 font-medium mb-4">
              {error instanceof Error ? error.message : 'Could not load guide'}
            </p>
            <button
              onClick={() => navigate(-1)}
              className="text-primary-600 hover:text-primary-700 font-medium"
            >
              ← Go back
            </button>
          </div>
        </main>
        <MobileNavigation currentPage="dashboard" />
      </div>
    )
  }

  // ── WhatsApp share ─────────────────────────────────────────────────
  const handleWhatsAppShare = () => {
    if (!content) return
    const { topic, subject, grade_level } = content.topic_header
    const explanation = content.simple_explanation.what_it_is
    const truncatedExplanation =
      explanation.length > 180 ? explanation.slice(0, 180) + '…' : explanation

    const text = [
      `📚 *${topic}* (${subject} · ${grade_level})`,
      '',
      truncatedExplanation,
      '',
      `💡 *Home activity:* ${content.home_activity.title}`,
      '',
      '_Guide generated by Awade — awade.app_',
    ].join('\n')

    window.open(
      `https://wa.me/?text=${encodeURIComponent(text)}`,
      '_blank',
      'noopener,noreferrer',
    )
  }

  // ── Guide content ─────────────────────────────────────────────────
  return (
    <div className="flex min-h-screen bg-background-50">
      <Sidebar currentPage="dashboard" />

      <main className="flex-1 lg:ml-64 pb-20 lg:pb-0">
        {/* Top bar */}
        <div className="bg-white border-b border-gray-200 px-4 sm:px-6 lg:px-8 py-4 sticky top-0 z-10">
          <div className="flex items-center justify-between max-w-3xl mx-auto">
            <button
              onClick={() => navigate(-1)}
              className="text-gray-500 hover:text-primary-600 transition-colors inline-flex items-center gap-2 text-sm font-medium"
            >
              <FaArrowLeft className="w-3 h-3" />
              Back
            </button>
            <div className="flex items-center gap-1">
              <button
                onClick={handleDownloadPdf}
                disabled={isDownloading}
                className="text-gray-500 hover:text-primary-600 transition-colors p-2 disabled:opacity-50"
                title="Download as PDF"
                aria-label="Download this guide as a PDF"
              >
                {isDownloading ? (
                  <span className="inline-block w-5 h-5 animate-spin rounded-full border-2 border-gray-300 border-t-primary-600" />
                ) : (
                  <FaDownload className="w-5 h-5" />
                )}
              </button>
              <button
                onClick={handleWhatsAppShare}
                className="text-gray-500 hover:text-green-600 transition-colors p-2"
                title="Share on WhatsApp"
                aria-label="Share this guide on WhatsApp"
              >
                <FaWhatsapp className="w-5 h-5" />
              </button>
              <button
                onClick={() => bookmarkMutation.mutate()}
                className="text-gray-500 hover:text-accent-600 transition-colors p-2"
                title={guide?.is_bookmarked ? 'Remove bookmark' : 'Bookmark this guide'}
              >
                {guide?.is_bookmarked ? (
                  <FaBookmark className="w-5 h-5 text-accent-600" />
                ) : (
                  <FaRegBookmark className="w-5 h-5" />
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Guide content */}
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-8">
          {/* Header */}
          <div>
            <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
              <span>{content.topic_header.subject}</span>
              <span>•</span>
              <span>{content.topic_header.grade_level}</span>
            </div>
            <h1 className="text-2xl lg:text-3xl font-bold text-primary-800">
              {content.topic_header.topic}
            </h1>
          </div>

          {/* Simple Explanation */}
          <Section
            icon={<FaLightbulb className="w-5 h-5 text-amber-500" />}
            title="What is this topic about?"
          >
            <p className="text-gray-700 leading-relaxed">{content.simple_explanation.what_it_is}</p>
            <p className="text-gray-600 text-sm mt-3 italic">{content.simple_explanation.why_it_matters}</p>
          </Section>

          {/* Home Activity */}
          <Section
            icon={<FaHome className="w-5 h-5 text-primary-600" />}
            title={content.home_activity.title}
            subtitle="Home activity (15-30 min)"
          >
            <p className="text-gray-700 leading-relaxed mb-4">{content.home_activity.description}</p>

            {content.home_activity.materials_needed.length > 0 && (
              <div className="mb-4">
                <p className="text-sm font-medium text-gray-600 mb-1">You'll need:</p>
                <div className="flex flex-wrap gap-2">
                  {content.home_activity.materials_needed.map((m, i) => (
                    <span key={i} className="bg-primary-50 text-primary-700 px-3 py-1 rounded-full text-sm">
                      {m}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <ol className="space-y-2">
              {content.home_activity.steps.map((step, i) => (
                <li key={i} className="text-gray-700 text-sm leading-relaxed pl-1">
                  {step}
                </li>
              ))}
            </ol>

            <div className="mt-4 bg-green-50 border border-green-200 rounded-xl px-4 py-3">
              <p className="text-green-800 text-sm">
                <span className="font-semibold">What to look for: </span>
                {content.home_activity.what_to_look_for}
              </p>
            </div>
          </Section>

          {/* Conversation Starters */}
          <Section
            icon={<FaComments className="w-5 h-5 text-blue-500" />}
            title="Conversation starters"
            subtitle="Questions to ask naturally"
          >
            <div className="space-y-3">
              {content.conversation_starters.map((q, i) => (
                <div key={i} className="bg-blue-50 border border-blue-100 rounded-xl px-4 py-3">
                  <p className="text-blue-900 text-sm leading-relaxed">"{q}"</p>
                </div>
              ))}
            </div>
          </Section>

          {/* Common Mistakes */}
          <Section
            icon={<FaExclamationTriangle className="w-5 h-5 text-orange-500" />}
            title="Common mistakes to watch for"
          >
            <div className="space-y-4">
              {content.common_mistakes.map((m, i) => (
                <div key={i} className="border border-gray-200 rounded-xl p-4">
                  <p className="font-medium text-gray-800 text-sm mb-1">{m.mistake}</p>
                  <p className="text-gray-500 text-xs mb-2">{m.why_it_happens}</p>
                  <div className="bg-amber-50 border border-amber-100 rounded-lg px-3 py-2">
                    <p className="text-amber-900 text-sm">
                      <span className="font-medium">How to help: </span>{m.how_to_help}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </Section>

          {/* Curriculum Context */}
          <Section
            icon={<FaChalkboardTeacher className="w-5 h-5 text-purple-500" />}
            title="Where this fits in the curriculum"
          >
            <div className="grid sm:grid-cols-3 gap-4">
              <InfoCard label="Before this topic" value={content.curriculum_context.what_came_before} />
              <InfoCard label="After this topic" value={content.curriculum_context.what_comes_next} />
              <InfoCard label="Time in school" value={content.curriculum_context.how_long_in_school} />
            </div>
          </Section>

          {/* Encouragement Tips */}
          <Section
            icon={<FaHeart className="w-5 h-5 text-red-400" />}
            title="Encouragement tips"
          >
            <div className="space-y-3">
              {content.encouragement_tips.map((tip, i) => (
                <div key={i} className="bg-red-50 border border-red-100 rounded-xl px-4 py-3">
                  <p className="text-red-900 text-sm leading-relaxed">{tip}</p>
                </div>
              ))}
            </div>
          </Section>
        </div>
      </main>

      <MobileNavigation currentPage="dashboard" />
    </div>
  )
}

// ── Reusable sub-components ─────────────────────────────────────────

interface SectionProps {
  icon: React.ReactNode
  title: string
  subtitle?: string
  children: React.ReactNode
}

const Section: React.FC<SectionProps> = ({ icon, title, subtitle, children }) => (
  <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden">
    <div className="px-5 py-4 border-b border-gray-100 flex items-center gap-3">
      {icon}
      <div>
        <h2 className="font-semibold text-gray-800">{title}</h2>
        {subtitle && <p className="text-xs text-gray-400">{subtitle}</p>}
      </div>
    </div>
    <div className="px-5 py-4">{children}</div>
  </div>
)

const InfoCard: React.FC<{ label: string; value: string }> = ({ label, value }) => (
  <div className="bg-background-50 rounded-xl p-3">
    <p className="text-xs font-medium text-gray-500 mb-1">{label}</p>
    <p className="text-gray-700 text-sm leading-relaxed">{value}</p>
  </div>
)

export default GuideViewPage
