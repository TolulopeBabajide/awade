import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { FaBookmark, FaBookOpen, FaRegBookmark } from 'react-icons/fa'
import apiService from '../services/api'
import Sidebar from '../components/Sidebar'
import MobileNavigation from '../components/MobileNavigation'
import type { ChildProfile, ParentGuide } from '../types/children'

const SavedGuidesPage: React.FC = () => {
  const navigate = useNavigate()
  const [selectedChildId, setSelectedChildId] = useState<number | null>(null)
  const [showBookmarkedOnly, setShowBookmarkedOnly] = useState(false)

  // Fetch children
  const { data: childrenData } = useQuery({
    queryKey: ['children'],
    queryFn: async () => {
      const res = await apiService.getChildren()
      if (res.error) throw new Error(res.error)
      return res.data
    },
  })

  const children: ChildProfile[] = childrenData?.children ?? []

  // Auto-select first child
  useEffect(() => {
    if (children.length > 0 && !selectedChildId) {
      setSelectedChildId(children[0].child_id)
    }
  }, [children])

  // Fetch guides for selected child
  const { data: guidesData, isLoading } = useQuery({
    queryKey: ['childGuides', selectedChildId, showBookmarkedOnly],
    queryFn: async () => {
      if (!selectedChildId) return { guides: [], total: 0 }
      const res = await apiService.getChildGuides(selectedChildId, showBookmarkedOnly || undefined)
      if (res.error) throw new Error(res.error)
      return res.data
    },
    enabled: !!selectedChildId,
  })

  const guides: ParentGuide[] = guidesData?.guides ?? []

  const handleGuideClick = (guide: ParentGuide) => {
    navigate(`/guides/generate?child=${guide.child_id}&topic=${guide.topic_id}&guide=${guide.guide_id}`)
  }

  return (
    <div className="flex min-h-screen bg-background-50">
      <Sidebar currentPage="lesson-resources" />

      <main className="flex-1 lg:ml-64 pb-20 lg:pb-0">
        {/* Top bar */}
        <div className="bg-white border-b border-gray-200 px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-xl lg:text-2xl font-bold text-primary-800">Saved Guides</h1>
            <button
              onClick={() => setShowBookmarkedOnly(!showBookmarkedOnly)}
              className={`inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-colors ${
                showBookmarkedOnly
                  ? 'bg-accent-100 text-accent-700 border border-accent-300'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {showBookmarkedOnly ? <FaBookmark className="w-3 h-3" /> : <FaRegBookmark className="w-3 h-3" />}
              Bookmarked
            </button>
          </div>
        </div>

        <div className="px-4 sm:px-6 lg:px-8 py-6">
          {/* Child selector */}
          {children.length > 1 && (
            <div className="flex gap-2 overflow-x-auto pb-4 mb-6 scrollbar-hide">
              {children.map(child => (
                <button
                  key={child.child_id}
                  onClick={() => setSelectedChildId(child.child_id)}
                  className={`flex-shrink-0 px-4 py-2 rounded-xl text-sm font-medium transition-colors ${
                    selectedChildId === child.child_id
                      ? 'bg-primary-600 text-white'
                      : 'bg-white border border-gray-200 text-gray-600 hover:border-primary-300'
                  }`}
                >
                  {child.name}
                </button>
              ))}
            </div>
          )}

          {/* Guides list */}
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
            </div>
          ) : guides.length === 0 ? (
            <div className="text-center py-16">
              <FaBookOpen className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-600 mb-2">
                {showBookmarkedOnly ? 'No bookmarked guides yet' : 'No guides yet'}
              </h3>
              <p className="text-gray-400 text-sm mb-4">
                {showBookmarkedOnly
                  ? 'Bookmark guides you want to revisit later.'
                  : 'Go to the dashboard, pick a topic, and generate your first guide.'}
              </p>
              {!showBookmarkedOnly && (
                <button
                  onClick={() => navigate('/dashboard')}
                  className="text-primary-600 hover:text-primary-700 font-medium text-sm"
                >
                  Go to Dashboard →
                </button>
              )}
            </div>
          ) : (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {guides.map(guide => (
                <button
                  key={guide.guide_id}
                  onClick={() => handleGuideClick(guide)}
                  className="bg-white border border-gray-200 rounded-xl p-5 text-left hover:border-primary-400 hover:shadow-md transition-all group"
                >
                  <div className="flex items-start justify-between mb-2">
                    <p className="font-medium text-gray-800 group-hover:text-primary-700 text-sm leading-snug flex-1">
                      {guide.topic_title || 'Untitled Topic'}
                    </p>
                    {guide.is_bookmarked && (
                      <FaBookmark className="w-3 h-3 text-accent-500 flex-shrink-0 ml-2 mt-0.5" />
                    )}
                  </div>
                  <p className="text-xs text-gray-400">
                    {guide.subject_name} • {new Date(guide.created_at).toLocaleDateString()}
                  </p>
                </button>
              ))}
            </div>
          )}
        </div>
      </main>

      <MobileNavigation currentPage="lesson-resources" />
    </div>
  )
}

export default SavedGuidesPage
