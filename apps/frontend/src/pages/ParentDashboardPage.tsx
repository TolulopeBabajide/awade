import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { FaPlus, FaBookOpen, FaEdit, FaTrash, FaGraduationCap, FaSchool } from 'react-icons/fa'
import apiService from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import Sidebar from '../components/Sidebar'
import MobileNavigation from '../components/MobileNavigation'
import AddChildModal from '../components/AddChildModal'
import type { ChildProfile, ChildTopic } from '../types/children'

const ParentDashboardPage: React.FC = () => {
  const navigate = useNavigate()
  const { user } = useAuth()
  const queryClient = useQueryClient()

  const [showAddChild, setShowAddChild] = useState(false)
  const [editingChild, setEditingChild] = useState<ChildProfile | null>(null)
  const [selectedChild, setSelectedChild] = useState<ChildProfile | null>(null)
  const [selectedSubjectId, setSelectedSubjectId] = useState<number | null>(null)
  const [deletingChildId, setDeletingChildId] = useState<number | null>(null)

  // Fetch children
  const {
    data: childrenData,
    isLoading: loadingChildren,
    isError: childrenFetchFailed,
    refetch: refetchChildren,
  } = useQuery({
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
    if (children.length > 0 && !selectedChild) {
      setSelectedChild(children[0])
    }
  }, [children])

  // Fetch topics for selected child
  const {
    data: topics,
    isLoading: loadingTopics,
    isError: topicsFetchFailed,
    refetch: refetchTopics,
  } = useQuery({
    queryKey: ['childTopics', selectedChild?.child_id, selectedSubjectId],
    queryFn: async () => {
      if (!selectedChild) return []
      const res = await apiService.getChildTopics(selectedChild.child_id, selectedSubjectId ?? undefined)
      if (res.error) throw new Error(res.error)
      return res.data ?? []
    },
    enabled: !!selectedChild,
  })

  // Group topics by subject
  const topicsBySubject = (topics ?? []).reduce<Record<string, ChildTopic[]>>((acc, topic) => {
    const key = topic.subject_name || 'Other'
    if (!acc[key]) acc[key] = []
    acc[key].push(topic)
    return acc
  }, {})

  const handleDeleteChild = async (childId: number) => {
    if (!confirm('Are you sure you want to remove this child profile? All saved guides will be deleted.')) return
    setDeletingChildId(childId)
    try {
      await apiService.deleteChild(childId)
      if (selectedChild?.child_id === childId) setSelectedChild(null)
      queryClient.invalidateQueries({ queryKey: ['children'] })
    } finally {
      setDeletingChildId(null)
    }
  }

  const handleTopicClick = (topic: ChildTopic) => {
    if (!selectedChild) return
    navigate(`/guides/generate?child=${selectedChild.child_id}&topic=${topic.topic_id}`)
  }

  const onChildAdded = () => {
    queryClient.invalidateQueries({ queryKey: ['children'] })
  }

  // ── Empty state: no children yet ─────────────────────────────────
  const EmptyState = () => (
    <div className="flex-1 flex items-center justify-center">
      <div className="text-center max-w-md px-4">
        <div className="w-20 h-20 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <FaGraduationCap className="w-10 h-10 text-primary-600" />
        </div>
        <h2 className="text-2xl font-bold text-primary-800 mb-3">
          Welcome to Awade, {user?.full_name?.split(' ')[0]}!
        </h2>
        <p className="text-gray-600 mb-6">
          Add your first child to start exploring their curriculum and get personalised guides for helping them at home.
        </p>
        <button
          onClick={() => setShowAddChild(true)}
          className="bg-accent-600 hover:bg-accent-700 text-white font-semibold py-3 px-8 rounded-xl transition-colors inline-flex items-center gap-2 shadow-md"
        >
          <FaPlus className="w-4 h-4" />
          Add Your Child
        </button>
      </div>
    </div>
  )

  return (
    <div className="flex min-h-screen bg-background-50">
      <Sidebar currentPage="dashboard" />

      <main className="flex-1 lg:ml-64 pb-20 lg:pb-0">
        {/* Top bar */}
        <div className="bg-white border-b border-gray-200 px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl lg:text-2xl font-bold text-primary-800">
                {selectedChild ? `${selectedChild.name}'s Learning` : 'Dashboard'}
              </h1>
              {selectedChild && selectedChild.grade_level_name && (
                <p className="text-sm text-gray-500 mt-0.5">
                  {selectedChild.grade_level_name} • {selectedChild.curricula_title ?? 'Curriculum not set'}
                </p>
              )}
            </div>
            <button
              onClick={() => { setEditingChild(null); setShowAddChild(true) }}
              className="bg-accent-600 hover:bg-accent-700 text-white font-medium py-2 px-4 rounded-xl transition-colors inline-flex items-center gap-2 text-sm"
            >
              <FaPlus className="w-3 h-3" />
              <span className="hidden sm:inline">Add Child</span>
            </button>
          </div>
        </div>

        {loadingChildren ? (
          <div className="flex-1 flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600" />
          </div>
        ) : childrenFetchFailed ? (
          <div className="flex-1 flex items-center justify-center py-20">
            <div className="text-center max-w-sm px-4">
              <p className="text-red-500 font-medium mb-3">Failed to load your children's profiles.</p>
              <button
                onClick={() => refetchChildren()}
                className="text-primary-600 hover:text-primary-700 font-medium text-sm"
              >
                Try again
              </button>
            </div>
          </div>
        ) : children.length === 0 ? (
          <EmptyState />
        ) : (
          <div className="px-4 sm:px-6 lg:px-8 py-6">
            {/* Child selector cards */}
            <div className="flex gap-3 overflow-x-auto pb-4 mb-6 scrollbar-hide">
              {children.map(child => (
                <div
                  key={child.child_id}
                  role="group"
                  aria-label={child.name}
                  tabIndex={0}
                  onClick={() => { setSelectedChild(child); setSelectedSubjectId(null) }}
                  onKeyDown={e => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault()
                      setSelectedChild(child)
                      setSelectedSubjectId(null)
                    }
                  }}
                  className={`flex-shrink-0 px-5 py-3 rounded-xl border-2 transition-all text-left min-w-[160px] cursor-pointer ${
                    selectedChild?.child_id === child.child_id
                      ? 'border-primary-600 bg-primary-50 shadow-sm'
                      : 'border-gray-200 bg-white hover:border-primary-300'
                  }`}
                >
                  <p className={`font-semibold text-sm ${
                    selectedChild?.child_id === child.child_id ? 'text-primary-800' : 'text-gray-800'
                  }`}>
                    {child.name}
                  </p>
                  <p className="text-xs text-gray-500 mt-0.5">
                    {child.grade_level_name || 'Grade not set'}
                  </p>
                  {/* Edit / Delete */}
                  <div className="flex gap-2 mt-2">
                    <button
                      onClick={e => { e.stopPropagation(); setEditingChild(child); setShowAddChild(true) }}
                      className="text-gray-400 hover:text-primary-600 transition-colors"
                      title="Edit"
                    >
                      <FaEdit className="w-3 h-3" />
                    </button>
                    <button
                      onClick={e => { e.stopPropagation(); handleDeleteChild(child.child_id) }}
                      className="text-gray-400 hover:text-red-500 transition-colors"
                      title="Remove"
                      disabled={deletingChildId === child.child_id}
                    >
                      <FaTrash className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* Topics grid */}
            {selectedChild && (
              <>
                {!selectedChild.curricula_id || !selectedChild.grade_level_id ? (
                  <div className="bg-white rounded-2xl p-8 text-center border border-gray-200">
                    <FaSchool className="w-10 h-10 text-gray-300 mx-auto mb-3" />
                    <h3 className="font-semibold text-gray-700 mb-2">Set up {selectedChild.name}'s curriculum</h3>
                    <p className="text-gray-500 text-sm mb-4">
                      Add their country, curriculum, and grade level so we can show the right topics.
                    </p>
                    <button
                      onClick={() => { setEditingChild(selectedChild); setShowAddChild(true) }}
                      className="bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-6 rounded-xl transition-colors text-sm"
                    >
                      Complete Profile
                    </button>
                  </div>
                ) : loadingTopics ? (
                  <div className="flex items-center justify-center py-12">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
                  </div>
                ) : topicsFetchFailed ? (
                  <div className="bg-white rounded-2xl p-8 text-center border border-gray-200">
                    <p className="text-red-500 font-medium mb-3">Failed to load topics. Please check your connection.</p>
                    <button
                      onClick={() => refetchTopics()}
                      className="text-primary-600 hover:text-primary-700 font-medium text-sm"
                    >
                      Try again
                    </button>
                  </div>
                ) : Object.keys(topicsBySubject).length === 0 ? (
                  <div className="bg-white rounded-2xl p-8 text-center border border-gray-200">
                    <FaBookOpen className="w-10 h-10 text-gray-300 mx-auto mb-3" />
                    <h3 className="font-semibold text-gray-700 mb-2">No topics found</h3>
                    <p className="text-gray-500 text-sm">
                      No curriculum topics are available for this grade and curriculum yet. Check back later or contact support.
                    </p>
                  </div>
                ) : (
                  <div className="space-y-8">
                    {Object.entries(topicsBySubject).map(([subjectName, subjectTopics]) => (
                      <div key={subjectName}>
                        <h2 className="text-lg font-semibold text-primary-800 mb-3 flex items-center gap-2">
                          <FaBookOpen className="w-4 h-4 text-primary-500" />
                          {subjectName}
                        </h2>
                        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
                          {subjectTopics.map(topic => (
                            <button
                              key={topic.topic_id}
                              onClick={() => handleTopicClick(topic)}
                              className="bg-white border border-gray-200 rounded-xl px-5 py-4 text-left hover:border-primary-400 hover:shadow-md transition-all group"
                            >
                              <p className="font-medium text-gray-800 group-hover:text-primary-700 text-sm leading-snug">
                                {topic.topic_title}
                              </p>
                              <p className="text-xs text-accent-600 mt-2 font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                                Get "How to Help" guide →
                              </p>
                            </button>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </main>

      <MobileNavigation currentPage="dashboard" />

      {/* Add/Edit Child Modal */}
      <AddChildModal
        isOpen={showAddChild}
        onClose={() => { setShowAddChild(false); setEditingChild(null) }}
        onSuccess={onChildAdded}
        editData={editingChild}
      />
    </div>
  )
}

export default ParentDashboardPage
