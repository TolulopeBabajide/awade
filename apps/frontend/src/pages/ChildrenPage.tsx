import React, { useState } from 'react'
import { useQueryClient, useQuery } from '@tanstack/react-query'
import {
  FaPlus,
  FaEdit,
  FaTrash,
  FaGraduationCap,
  FaSchool,
  FaUsers,
  FaBookOpen,
} from 'react-icons/fa'
import apiService from '../services/api'
import Sidebar from '../components/Sidebar'
import MobileNavigation from '../components/MobileNavigation'
import AddChildModal from '../components/AddChildModal'
import type { ChildProfile } from '../types/children'

const ChildrenPage: React.FC = () => {
  const queryClient = useQueryClient()
  const [showAddChild, setShowAddChild] = useState(false)
  const [editingChild, setEditingChild] = useState<ChildProfile | null>(null)
  const [deletingChildId, setDeletingChildId] = useState<number | null>(null)
  const [deleteError, setDeleteError] = useState<string | null>(null)

  const {
    data: childrenData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['children'],
    queryFn: async () => {
      const res = await apiService.getChildren()
      if (res.error) throw new Error(res.error)
      return res.data
    },
  })

  const children: ChildProfile[] = childrenData?.children ?? []

  const handleDeleteChild = async (childId: number) => {
    if (
      !confirm(
        'Are you sure you want to remove this child profile? All saved guides will also be deleted.'
      )
    )
      return

    setDeletingChildId(childId)
    setDeleteError(null)
    try {
      const res = await apiService.deleteChild(childId)
      if (res.error) {
        setDeleteError(res.error)
      } else {
        queryClient.invalidateQueries({ queryKey: ['children'] })
      }
    } catch {
      setDeleteError('Something went wrong. Please try again.')
    } finally {
      setDeletingChildId(null)
    }
  }

  const openAddModal = () => {
    setEditingChild(null)
    setShowAddChild(true)
  }

  const openEditModal = (child: ChildProfile) => {
    setEditingChild(child)
    setShowAddChild(true)
  }

  const onModalSuccess = () => {
    queryClient.invalidateQueries({ queryKey: ['children'] })
  }

  return (
    <div className="flex min-h-screen bg-background-50">
      <Sidebar currentPage="children" />

      <main id="main-content" tabIndex={-1} className="flex-1 lg:ml-64 pb-20 lg:pb-0 outline-none">
        {/* Top bar */}
        <div className="bg-white border-b border-gray-200 px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl lg:text-2xl font-bold text-primary-800">My Children</h1>
              <p className="text-sm text-gray-500 mt-0.5">
                Manage your children's profiles and curriculum settings
              </p>
            </div>
            <button
              onClick={openAddModal}
              className="bg-accent-700 hover:bg-accent-800 text-white font-medium py-2 px-4 rounded-xl transition-colors inline-flex items-center gap-2 text-sm"
            >
              <FaPlus className="w-3 h-3" />
              <span className="hidden sm:inline">Add Child</span>
            </button>
          </div>
        </div>

        <div className="px-4 sm:px-6 lg:px-8 py-6">
          {/* Delete error banner */}
          {deleteError && (
            <div role="alert" className="mb-4 bg-red-50 text-red-600 px-4 py-3 rounded-xl text-sm">
              {deleteError}
            </div>
          )}

          {/* Loading */}
          {isLoading ? (
            <div className="flex items-center justify-center py-20">
              <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600" />
            </div>
          ) : error ? (
            <div className="flex items-center justify-center py-20 text-center">
              <div>
                <p className="text-gray-500 mb-2">Unable to load children profiles.</p>
                <button
                  onClick={() => queryClient.invalidateQueries({ queryKey: ['children'] })}
                  className="text-primary-600 hover:text-primary-700 text-sm font-medium"
                >
                  Try again
                </button>
              </div>
            </div>
          ) : children.length === 0 ? (
            /* Empty state */
            <div className="flex items-center justify-center py-20">
              <div className="text-center max-w-sm px-4">
                <div className="w-20 h-20 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-6">
                  <FaUsers className="w-9 h-9 text-primary-600" />
                </div>
                <h2 className="text-xl font-bold text-primary-800 mb-3">No children added yet</h2>
                <p className="text-gray-500 text-sm mb-6">
                  Add your child's profile so Awade can show the right curriculum topics and
                  generate personalised "How to Help" guides.
                </p>
                <button
                  onClick={openAddModal}
                  className="bg-accent-700 hover:bg-accent-800 text-white font-semibold py-3 px-8 rounded-xl transition-colors inline-flex items-center gap-2 shadow-md"
                >
                  <FaPlus className="w-4 h-4" />
                  Add Your First Child
                </button>
              </div>
            </div>
          ) : (
            /* Children grid */
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {children.map(child => (
                <div
                  key={child.child_id}
                  className="bg-white border border-gray-200 rounded-2xl p-5 shadow-sm hover:shadow-md transition-shadow"
                >
                  {/* Header row */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-11 h-11 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
                        <FaGraduationCap className="w-5 h-5 text-primary-600" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900 leading-snug">{child.name}</h3>
                        {child.age != null && (
                          <p className="text-xs text-gray-400">Age {child.age}</p>
                        )}
                      </div>
                    </div>

                    {/* Action buttons */}
                    <div className="flex items-center gap-1 ml-2">
                      <button
                        onClick={() => openEditModal(child)}
                        className="p-2 rounded-lg text-gray-400 hover:text-primary-600 hover:bg-primary-50 transition-colors"
                        title="Edit profile"
                        aria-label={`Edit ${child.name}'s profile`}
                      >
                        <FaEdit className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDeleteChild(child.child_id)}
                        disabled={deletingChildId === child.child_id}
                        className="p-2 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        title="Remove profile"
                        aria-label={`Remove ${child.name}'s profile`}
                      >
                        <FaTrash className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {/* Details */}
                  <div className="space-y-2">
                    {child.school_name && (
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <FaSchool className="w-3.5 h-3.5 text-gray-400 flex-shrink-0" />
                        <span className="truncate">{child.school_name}</span>
                      </div>
                    )}
                    {child.grade_level_name && (
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <FaBookOpen className="w-3.5 h-3.5 text-gray-400 flex-shrink-0" />
                        <span>{child.grade_level_name}</span>
                      </div>
                    )}
                    {child.curricula_title && (
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <FaGraduationCap className="w-3.5 h-3.5 text-gray-400 flex-shrink-0" />
                        <span className="truncate">{child.curricula_title}</span>
                      </div>
                    )}
                  </div>

                  {/* Incomplete profile nudge */}
                  {(!child.curricula_id || !child.grade_level_id) && (
                    <div className="mt-4 pt-4 border-t border-gray-100">
                      <p className="text-xs text-amber-600 mb-2">
                        Curriculum not set — topics won't load until complete.
                      </p>
                      <button
                        onClick={() => openEditModal(child)}
                        className="text-xs font-medium text-primary-600 hover:text-primary-700 transition-colors"
                      >
                        Complete profile →
                      </button>
                    </div>
                  )}
                </div>
              ))}

              {/* "Add another" card */}
              <button
                onClick={openAddModal}
                className="border-2 border-dashed border-gray-200 rounded-2xl p-5 flex flex-col items-center justify-center gap-3 hover:border-primary-300 hover:bg-primary-50 transition-colors group min-h-[160px]"
                aria-label="Add another child"
              >
                <div className="w-11 h-11 bg-gray-100 group-hover:bg-primary-100 rounded-full flex items-center justify-center transition-colors">
                  <FaPlus className="w-4 h-4 text-gray-400 group-hover:text-primary-600 transition-colors" />
                </div>
                <span className="text-sm font-medium text-gray-400 group-hover:text-primary-600 transition-colors">
                  Add another child
                </span>
              </button>
            </div>
          )}
        </div>
      </main>

      <MobileNavigation currentPage="children" />

      <AddChildModal
        isOpen={showAddChild}
        onClose={() => {
          setShowAddChild(false)
          setEditingChild(null)
        }}
        onSuccess={onModalSuccess}
        editData={editingChild}
      />
    </div>
  )
}

export default ChildrenPage
