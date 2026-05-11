import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { FaPlus, FaBookOpen, FaEdit, FaTrash, FaGraduationCap, FaSchool } from 'react-icons/fa'
import apiService from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import Sidebar from '../components/Sidebar'
import MobileNavigation from '../components/MobileNavigation'
import AddChildModal from '../components/AddChildModal'
import ConsentModal from '../components/ConsentModal'
import DeleteChildConfirmModal from '../components/DeleteChildConfirmModal'
import type { ChildProfile, ChildTopic, ConsentStatusResponse, ChildProfileListResponse } from '../types/children'
import { getErrorMessage } from '../utils/errors'
import { useConsentGate } from '../hooks/useConsentGate'

// ── File-scope subcomponent ───────────────────────────────────────────────
// Defined outside ParentDashboardPage so React sees a stable component
// reference across renders, preventing unnecessary unmount/remount cycles.
// AWD-H-66
interface EmptyStateProps {
  firstName?: string
  onAddChild: () => void
}

const EmptyState: React.FC<EmptyStateProps> = ({ firstName, onAddChild }) => (
  <div className="flex-1 flex items-center justify-center">
    <div className="text-center max-w-md px-4">
      <div className="w-20 h-20 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-6">
        <FaGraduationCap className="w-10 h-10 text-primary-600" />
      </div>
      <h2 className="text-2xl font-bold text-primary-800 mb-3">
        Welcome to Awade, {firstName}!
      </h2>
      <p className="text-gray-600 mb-6">
        Add your first child to start exploring their curriculum and get personalised guides for helping them at home.
      </p>
      <button
        onClick={onAddChild}
        className="bg-accent-700 hover:bg-accent-800 text-white font-semibold py-3 px-8 rounded-xl transition-colors inline-flex items-center gap-2 shadow-md"
      >
        <FaPlus className="w-4 h-4" />
        Add Your Child
      </button>
    </div>
  </div>
)

const ParentDashboardPage: React.FC = () => {
  const navigate = useNavigate()
  const { user } = useAuth()
  const queryClient = useQueryClient()

  const [showAddChild, setShowAddChild] = useState(false)
  const [editingChild, setEditingChild] = useState<ChildProfile | null>(null)
  const [selectedChild, setSelectedChild] = useState<ChildProfile | null>(null)
  const [selectedSubjectId, setSelectedSubjectId] = useState<number | null>(null)
  const [deletingChildId, setDeletingChildId] = useState<number | null>(null)
  // AWD-H-80: surface delete failures inline instead of silently swallowing them
  const [deleteError, setDeleteError] = useState<string | null>(null)
  // AWD-M-80: replace blocking, inaccessible window.confirm() with an
  // in-app modal — `pendingDeleteChild` is non-null while the confirmation
  // dialog is open.
  const [pendingDeleteChild, setPendingDeleteChild] = useState<ChildProfile | null>(null)

  // Fetch consent status once on mount so we know whether to gate "Add Child"
  const { data: consentStatus, refetch: refetchConsent } = useQuery<ConsentStatusResponse, Error>({
    queryKey: ['consentStatus'],
    queryFn: async () => {
      const res = await apiService.getConsentStatus()
      if (res.error) throw new Error(res.error)
      return res.data!
    },
  })

  // ── COPPA consent gate (AWD-M-132) ───────────────────────────────────
  // Extracts showConsentModal / consentSubmitting / consentError + their
  // handlers into a dedicated hook, reducing this component's useState count.
  const consentGate = useConsentGate(consentStatus, refetchConsent, () => setShowAddChild(true))

  // Fetch children
  const {
    data: childrenData,
    isLoading: loadingChildren,
    isError: childrenFetchFailed,
    refetch: refetchChildren,
  } = useQuery<ChildProfileListResponse, Error>({
    queryKey: ['children'],
    queryFn: async () => {
      const res = await apiService.getChildren()
      if (res.error) throw new Error(res.error)
      return res.data!
    },
  })

  const children: ChildProfile[] = childrenData?.children ?? []

  // Auto-select first child.
  // AWD-M-131: use functional-updater form so `selectedChild` is not read
  // inside the effect body, eliminating the react-hooks/exhaustive-deps warning
  // without adding `selectedChild` to the dep array (which would cause a loop).
  useEffect(() => {
    if (children.length > 0) {
      setSelectedChild(prev => prev ?? children[0])
    }
  }, [children])

  // Fetch topics for selected child
  const {
    data: topics,
    isLoading: loadingTopics,
    isError: topicsFetchFailed,
    refetch: refetchTopics,
  } = useQuery<ChildTopic[], Error>({
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

  /**
   * AWD-M-80: open the in-app confirmation modal. The actual API call is
   * deferred to `confirmDeleteChild` once the parent presses "Remove" inside
   * the modal.
   */
  const requestDeleteChild = (child: ChildProfile) => {
    setDeleteError(null)
    setPendingDeleteChild(child)
  }

  /**
   * AWD-M-80: invoked from DeleteChildConfirmModal's "Remove" button.
   * Performs the actual delete and surfaces any error inline (AWD-H-80).
   */
  const confirmDeleteChild = async () => {
    if (!pendingDeleteChild) return
    const childId = pendingDeleteChild.child_id
    setDeletingChildId(childId)
    setDeleteError(null)
    try {
      await apiService.deleteChild(childId)
      if (selectedChild?.child_id === childId) setSelectedChild(null)
      queryClient.invalidateQueries({ queryKey: ['children'] })
      setPendingDeleteChild(null)
    } catch (err) {
      // AWD-H-80: surface the error inline rather than absorbing it silently.
      // Close the modal so the inline banner is visible above the cards.
      setDeleteError(getErrorMessage(err, 'Failed to remove child profile. Please try again.'))
      setPendingDeleteChild(null)
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

  /**
   * Called when the parent clicks any "Add Child" button.
   * AWD-M-132: delegates consent-gate logic to useConsentGate hook.
   * If consent has not yet been given, the hook opens ConsentModal;
   * otherwise it calls onConsentGranted (setShowAddChild) directly.
   */
  const handleAddChildIntent = (child: ChildProfile | null = null) => {
    setEditingChild(child)
    consentGate.openConsentGate()
  }

  return (
    <div className="flex min-h-screen bg-background-50">
      <Sidebar currentPage="dashboard" />

      <main id="main-content" tabIndex={-1} className="flex-1 lg:ml-64 pb-20 lg:pb-0 outline-none">
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
              onClick={() => handleAddChildIntent(null)}
              className="bg-accent-700 hover:bg-accent-800 text-white font-medium py-2 px-4 rounded-xl transition-colors inline-flex items-center gap-2 text-sm"
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
          <EmptyState
            firstName={user?.full_name?.split(' ')[0]}
            onAddChild={() => handleAddChildIntent(null)}
          />
        ) : (
          <div className="px-4 sm:px-6 lg:px-8 py-6">
            {/* AWD-H-80: inline delete error — shown when deleteChild API call fails */}
            {deleteError && (
              <p role="alert" className="text-red-500 text-sm font-medium mb-4">
                {deleteError}
              </p>
            )}
            {/* Child selector cards */}
            <div className="flex gap-3 overflow-x-auto pb-4 mb-6 scrollbar-hide">
              {children.map(child => (
                <div
                  key={child.child_id}
                  role="group"
                  aria-label={child.name}
                  tabIndex={0}
                  onClick={() => {
                    setSelectedChild(child)
                    setSelectedSubjectId(null)
                    // AWD-L-26: clear any stale delete-error banner so it
                    // doesn't persist while the parent is viewing a different
                    // child than the one whose delete attempt failed.
                    setDeleteError(null)
                  }}
                  onKeyDown={e => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault()
                      setSelectedChild(child)
                      setSelectedSubjectId(null)
                      // AWD-L-26: keyboard-activated card switch must also
                      // clear the delete-error banner.
                      setDeleteError(null)
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
                  <div className="flex items-center gap-1 mt-2">
                    <button
                      onClick={e => { e.stopPropagation(); handleAddChildIntent(child) }}
                      className="p-2 rounded-lg text-gray-500 hover:text-primary-600 hover:bg-primary-50 transition-colors"
                      title="Edit"
                      aria-label={`Edit ${child.name}'s profile`}
                    >
                      <FaEdit className="w-4 h-4" />
                    </button>
                    <button
                      onClick={e => { e.stopPropagation(); requestDeleteChild(child) }}
                      className="p-2 rounded-lg text-gray-500 hover:text-red-500 hover:bg-red-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      title="Remove"
                      aria-label={`Remove ${child.name}'s profile`}
                      disabled={deletingChildId === child.child_id}
                    >
                      <FaTrash className="w-4 h-4" />
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
                    {/* AI pre-generation notice — EU AI Act Art. 52 / AWD-GRC-07 */}
                    <p className="text-xs text-gray-400 leading-relaxed">
                      Tap a topic to generate an AI-powered "How to Help" guide. Guides are
                      created by AI and may contain inaccuracies.{' '}
                      <a
                        href="/disclaimer"
                        className="underline hover:text-gray-600 transition-colors"
                      >
                        Learn more
                      </a>
                    </p>
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
                              aria-label={`Generate "How to Help" guide for ${topic.topic_title}`}
                              className="bg-white border border-gray-200 rounded-xl px-5 py-4 text-left hover:border-primary-400 hover:shadow-md transition-all group"
                            >
                              <p className="font-medium text-gray-800 group-hover:text-primary-700 text-sm leading-snug">
                                {topic.topic_title}
                              </p>
                              <p className="text-xs text-accent-600 mt-2 font-medium opacity-0 group-hover:opacity-100 group-focus-within:opacity-100 transition-opacity">
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

      {/* COPPA Consent Modal (AWD-GRC-01) — shown before the first "Add Child" */}
      {/* AWD-M-132: state + handlers managed by useConsentGate hook */}
      {consentGate.showConsentModal && (
        <ConsentModal
          onConsented={consentGate.handleConsentConfirmed}
          onCancel={() => { consentGate.handleCancel(); setEditingChild(null) }}
          isSubmitting={consentGate.consentSubmitting}
          error={consentGate.consentError}
        />
      )}

      {/* Add/Edit Child Modal */}
      <AddChildModal
        isOpen={showAddChild}
        onClose={() => { setShowAddChild(false); setEditingChild(null) }}
        onSuccess={onChildAdded}
        editData={editingChild}
      />

      {/* AWD-M-80: Delete-child confirmation modal — replaces window.confirm() */}
      {pendingDeleteChild && (
        <DeleteChildConfirmModal
          childName={pendingDeleteChild.name}
          onConfirm={confirmDeleteChild}
          onCancel={() => setPendingDeleteChild(null)}
          isSubmitting={deletingChildId === pendingDeleteChild.child_id}
        />
      )}
    </div>
  )
}

export default ParentDashboardPage
