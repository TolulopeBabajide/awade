/**
 * ConfirmRoleChangeModal — AWD-M-144
 *
 * Accessible confirmation dialog shown before changing a user's role in the
 * admin panel. Replaces the blocking `window.confirm()` previously used in
 * UserList.tsx — `confirm()` blocks the main thread, is not keyboard-focusable
 * in a styleable way, and cannot be tested without browser-global spies.
 *
 * Pattern mirrors DeleteChildConfirmModal: backdrop + dialog with
 * `role="dialog"`, `aria-modal="true"`, focus trap via useFocusTrap, and
 * Escape-to-close.
 */

import React, { useRef } from 'react'
import { FiShield } from 'react-icons/fi'
import { useFocusTrap } from '../hooks/useFocusTrap'

interface ConfirmRoleChangeModalProps {
  /** The user's display name, shown in the dialog title. */
  userName: string
  /** The new role being assigned (e.g. "ADMIN", "SUPER_ADMIN", "EDUCATOR"). */
  newRole: string
  /** Called when the admin clicks "Confirm" — triggers the actual role change. */
  onConfirm: () => void
  /** Called when the admin clicks Cancel, presses Escape, or closes the modal. */
  onCancel: () => void
}

const ConfirmRoleChangeModal: React.FC<ConfirmRoleChangeModalProps> = ({
  userName,
  newRole,
  onConfirm,
  onCancel,
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
      aria-labelledby="confirm-role-change-title"
      aria-describedby="confirm-role-change-body"
    >
      <div className="bg-white rounded-2xl shadow-2xl max-w-sm w-full p-6 sm:p-8">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-indigo-100 rounded-full flex items-center justify-center flex-shrink-0">
            <FiShield className="w-5 h-5 text-indigo-600" />
          </div>
          <h2
            id="confirm-role-change-title"
            className="text-lg font-bold text-gray-900"
          >
            Change role to {newRole}?
          </h2>
        </div>

        <p
          id="confirm-role-change-body"
          className="text-sm text-gray-700 mb-6"
        >
          You are about to change <strong>{userName}</strong>&rsquo;s role to{' '}
          <strong>{newRole}</strong>. This will immediately affect their access
          permissions. This action can be reversed by changing their role again.
        </p>

        <div className="flex flex-col sm:flex-row gap-3">
          <button
            onClick={onConfirm}
            className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-6 rounded-xl transition-colors"
            autoFocus
          >
            Confirm
          </button>
          <button
            onClick={onCancel}
            className="flex-1 sm:flex-none border border-gray-300 text-gray-700 hover:text-gray-900 font-medium py-3 px-6 rounded-xl transition-colors"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  )
}

export default ConfirmRoleChangeModal
