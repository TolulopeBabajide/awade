/**
 * ConsentModal — AWD-GRC-01
 *
 * COPPA-required parental consent modal. Shown once, before a parent adds
 * their first child profile. The parent must explicitly tick the checkbox and
 * press "I Agree" before the API call to POST /api/consent is made.
 *
 * Consent version: "1.0" — bump when the disclosure text changes materially.
 */

import React, { useState } from 'react'
import { FaShieldAlt, FaLock, FaChild } from 'react-icons/fa'

interface ConsentModalProps {
  /** Called after consent has been successfully recorded on the server. */
  onConsented: () => void
  /** Called if the parent closes/cancels the modal without consenting. */
  onCancel: () => void
  /** Whether the API call to record consent is in-flight. */
  isSubmitting: boolean
  /** Non-null error string if the consent API call failed. */
  error: string | null
}

const ConsentModal: React.FC<ConsentModalProps> = ({
  onConsented,
  onCancel,
  isSubmitting,
  error,
}) => {
  const [checked, setChecked] = useState(false)

  return (
    /* Backdrop */
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="consent-modal-title"
    >
      <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full p-6 sm:p-8 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center gap-3 mb-5">
          <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
            <FaShieldAlt className="w-5 h-5 text-primary-600" />
          </div>
          <h2
            id="consent-modal-title"
            className="text-xl font-bold text-primary-800"
          >
            Before you add a child
          </h2>
        </div>

        {/* Disclosure body */}
        <div className="text-sm text-gray-700 space-y-4 mb-6">
          <p>
            Awade collects limited information about your child to personalise
            their learning guides. We take your family's privacy seriously,
            especially when children are involved.
          </p>

          <div className="bg-background-50 rounded-xl p-4 space-y-3">
            <h3 className="font-semibold text-primary-800 flex items-center gap-2">
              <FaChild className="w-4 h-4" /> What we collect about your child
            </h3>
            <ul className="list-disc list-inside space-y-1 text-gray-600">
              <li>Child's first name (or nickname — never a surname)</li>
              <li>Age, school name (optional)</li>
              <li>Country, curriculum, grade level, and subjects</li>
            </ul>
          </div>

          <div className="bg-background-50 rounded-xl p-4 space-y-3">
            <h3 className="font-semibold text-primary-800 flex items-center gap-2">
              <FaLock className="w-4 h-4" /> How we use it
            </h3>
            <ul className="list-disc list-inside space-y-1 text-gray-600">
              <li>To generate personalised "How to Help" learning guides for you</li>
              <li>To match topics to your child's specific curriculum</li>
              <li>We do not sell or share your child's data with advertisers</li>
              <li>
                Data is stored securely and can be deleted at any time from{' '}
                <strong>Settings → Delete Account</strong>
              </li>
            </ul>
          </div>

          <p className="text-xs text-gray-500">
            Awade complies with the Children's Online Privacy Protection Act (COPPA)
            and applicable data protection laws. By consenting, you confirm you are
            the parent or legal guardian of the child(ren) you are adding, and you
            authorise Awade to store and process the information above on their behalf.
            Consent version 1.0 — 27 April 2026.
          </p>
        </div>

        {/* Checkbox */}
        <label className="flex items-start gap-3 cursor-pointer mb-5 select-none">
          <input
            type="checkbox"
            checked={checked}
            onChange={e => setChecked(e.target.checked)}
            className="mt-0.5 w-4 h-4 accent-accent-600 flex-shrink-0"
            aria-required="true"
          />
          <span className="text-sm text-gray-700">
            I have read the disclosure above. I am the parent or legal guardian
            of the child(ren) I am adding, and I consent to Awade collecting and
            using the information described.
          </span>
        </label>

        {/* Error */}
        {error && (
          <p className="text-red-500 text-sm mb-4" role="alert">
            {error}
          </p>
        )}

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-3">
          <button
            onClick={onConsented}
            disabled={!checked || isSubmitting}
            className="flex-1 bg-accent-700 hover:bg-accent-800 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-xl transition-colors"
            aria-disabled={!checked || isSubmitting}
          >
            {isSubmitting ? 'Saving…' : 'I Agree — Add a Child'}
          </button>
          <button
            onClick={onCancel}
            disabled={isSubmitting}
            className="flex-1 sm:flex-none border border-gray-300 text-gray-600 hover:text-gray-800 font-medium py-3 px-6 rounded-xl transition-colors"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  )
}

export default ConsentModal
