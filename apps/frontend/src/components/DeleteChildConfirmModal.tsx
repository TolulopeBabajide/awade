/**
 * DeleteChildConfirmModal — AWD-M-80
 *
 * Accessible confirmation dialog shown before removing a child profile.
 * Replaces the browser-native `confirm()` previously used in
 * ParentDashboardPage.handleDeleteChild — `confirm()` blocks the main thread,
 * is not keyboard-focusable in a styleable way, and is suppressed in some
 * embedded/mobile contexts.
 *
 * Pattern follows the existing ConsentModal: backdrop + dialog with
 * `role="dialog"`, `aria-modal="true"`, focus trap, and Escape-to-close.
 */

import React, { useRef } from 'react'
import { FaExclamationTriangle } from 'react-icons/fa'
import { useFocusTrap } from '../hooks/useFocusTrap'

interface DeleteChildConfirmModalProps {
  /** The child's display name, used in the title. */
  childName: string
  /** Called when the parent clicks "Remove" — triggers the actual delete. */
  onConfirm: () => void
  /** Called when the parent clicks Cancel, presses Escape, or closes the modal. */
  onCancel: () => void
  /** Whether the delete API call is in flight — disables both buttons. */
  isSubmitting?: boolean
}

const DeleteChildConfirmModal: React.FC<DeleteChildConfirmModalProps> = ({
  childName,
  onConfirm,
  onCancel,
  isSubmitting = false,
}) => {
  const dialogRef = useRef<HTMLDivElement>(null)
  // Modal is always active while rendered; Escape closes it via onCancel.
  useFocusTrap(dialogRef, true, onCancel)

  return (
    <div
      ref={dialogRef}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="delete-child-modal-title"
      aria-describedby="delete-child-modal-body"
    >
      <div className="bg-white rounded-2xl shadow-2xl max-w-sm w-full p-6 sm:p-8">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center flex-shrink-0">
            <FaExclamationTriangle className="w-5 h-5 text-red-600" />
          </div>
          <h2
            id="delete-child-modal-title"
            className="text-lg font-bold text-primary-800"
          >
            Remove {childName}'s profile?
          </h2>
        </div>

        <p
          id="delete-child-modal-body"
          className="text-sm text-gray-700 mb-6"
        >
          This will permanently remove this child profile and all of their
          saved &ldquo;How to Help&rdquo; guides. This action cannot be undone.
        </p>

        <div className="flex flex-col sm:flex-row gap-3">
          <button
            onClick={onConfirm}
            disabled={isSubmitting}
            className="flex-1 bg-red-600 hover:bg-red-700 disabled:bg-red-300 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-xl transition-colors"
            aria-disabled={isSubmitting}
            autoFocus
          >
            {isSubmitting ? 'Removing…' : 'Remove'}
          </button>
          <button
            onClick={onCancel}
            disabled={isSubmitting}
            className="flex-1 sm:flex-none border border-gray-300 text-gray-700 hover:text-gray-900 font-medium py-3 px-6 rounded-xl transition-colors"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  )
}

export default DeleteChildConfirmModal
