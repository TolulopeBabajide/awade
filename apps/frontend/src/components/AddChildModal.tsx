import React, { useState, useEffect } from 'react'
import { FaTimes } from 'react-icons/fa'
import apiService from '../services/api'
import type { ChildProfileCreate } from '../types/children'

interface AddChildModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  editData?: any // If provided, we're editing
}

const AddChildModal: React.FC<AddChildModalProps> = ({ isOpen, onClose, onSuccess, editData }) => {
  const [form, setForm] = useState<ChildProfileCreate>({
    name: '',
    age: null,
    school_name: null,
    country_id: null,
    curricula_id: null,
    grade_level_id: null,
    subjects: null,
  })
  const [countries, setCountries] = useState<any[]>([])
  const [curriculums, setCurriculums] = useState<any[]>([])
  const [gradeLevels, setGradeLevels] = useState<any[]>([])
  const [subjects, setSubjects] = useState<any[]>([])
  const [selectedSubjects, setSelectedSubjects] = useState<number[]>([])
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')

  // Load reference data
  useEffect(() => {
    if (!isOpen) return
    const load = async () => {
      const [countriesRes, gradeLevelsRes, subjectsRes] = await Promise.all([
        apiService.getCountries(),
        apiService.getGradeLevels(),
        apiService.getSubjects(),
      ])
      if (countriesRes.data) setCountries(countriesRes.data)
      if (gradeLevelsRes.data) setGradeLevels(gradeLevelsRes.data)
      if (subjectsRes.data) setSubjects(subjectsRes.data)
    }
    load()
  }, [isOpen])

  // Load curriculums when country changes
  useEffect(() => {
    if (!form.country_id) {
      setCurriculums([])
      return
    }
    const load = async () => {
      const res = await apiService.getCurriculums(form.country_id!)
      if (res.data) setCurriculums(res.data)
    }
    load()
  }, [form.country_id])

  // Pre-fill for edit mode
  useEffect(() => {
    if (editData) {
      setForm({
        name: editData.name || '',
        age: editData.age,
        school_name: editData.school_name,
        country_id: editData.country_id,
        curricula_id: editData.curricula_id,
        grade_level_id: editData.grade_level_id,
        subjects: editData.subjects,
      })
      setSelectedSubjects(editData.subjects || [])
    } else {
      setForm({ name: '', age: null, school_name: null, country_id: null, curricula_id: null, grade_level_id: null, subjects: null })
      setSelectedSubjects([])
    }
    setError('')
  }, [editData, isOpen])

  const toggleSubject = (id: number) => {
    setSelectedSubjects(prev =>
      prev.includes(id) ? prev.filter(s => s !== id) : [...prev, id]
    )
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.name.trim()) {
      setError("Please enter your child's name")
      return
    }
    setIsSubmitting(true)
    setError('')

    const payload = {
      ...form,
      name: form.name.trim(),
      subjects: selectedSubjects.length > 0 ? selectedSubjects : null,
    }

    try {
      const res = editData
        ? await apiService.updateChild(editData.child_id, payload)
        : await apiService.createChild(payload)

      if (res.error) {
        setError(res.error)
      } else {
        onSuccess()
        onClose()
      }
    } catch {
      setError('Something went wrong. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (!isOpen) return null

  return (
    <div
      className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="add-child-modal-title"
    >
      <div
        className="bg-white rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto shadow-xl"
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <h2 id="add-child-modal-title" className="text-xl font-semibold text-primary-800">
            {editData ? 'Edit Child Profile' : 'Add Your Child'}
          </h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 p-1">
            <FaTimes className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-5" noValidate>
          {error && (
            <div role="alert" className="bg-red-50 text-red-600 px-4 py-3 rounded-lg text-sm">{error}</div>
          )}

          {/* Name */}
          <div>
            <label htmlFor="modal-child-name" className="block text-sm font-medium text-gray-700 mb-1">
              Child's Name{' '}
              <span className="text-red-500" aria-hidden="true">*</span>
              <span className="sr-only">(required)</span>
            </label>
            <input
              id="modal-child-name"
              type="text"
              value={form.name}
              onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition"
              placeholder="e.g. Amina"
              required
              aria-required="true"
              autoFocus
            />
          </div>

          {/* Age */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Age</label>
            <input
              type="number"
              min={3}
              max={25}
              value={form.age ?? ''}
              onChange={e => setForm(f => ({ ...f, age: e.target.value ? parseInt(e.target.value) : null }))}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition"
              placeholder="e.g. 12"
            />
          </div>

          {/* School */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">School Name</label>
            <input
              type="text"
              value={form.school_name ?? ''}
              onChange={e => setForm(f => ({ ...f, school_name: e.target.value || null }))}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition"
              placeholder="e.g. Federal Government College"
            />
          </div>

          {/* Country */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Country</label>
            <select
              value={form.country_id ?? ''}
              onChange={e => setForm(f => ({ ...f, country_id: e.target.value ? parseInt(e.target.value) : null, curricula_id: null }))}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition bg-white"
            >
              <option value="">Select country</option>
              {countries.map(c => (
                <option key={c.country_id} value={c.country_id}>{c.country_name}</option>
              ))}
            </select>
          </div>

          {/* Curriculum */}
          {form.country_id && curriculums.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Curriculum</label>
              <select
                value={form.curricula_id ?? ''}
                onChange={e => setForm(f => ({ ...f, curricula_id: e.target.value ? parseInt(e.target.value) : null }))}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition bg-white"
              >
                <option value="">Select curriculum</option>
                {curriculums.map(c => (
                  <option key={c.curricula_id} value={c.curricula_id}>{c.curricula_title}</option>
                ))}
              </select>
            </div>
          )}

          {/* Grade Level */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Grade Level</label>
            <select
              value={form.grade_level_id ?? ''}
              onChange={e => setForm(f => ({ ...f, grade_level_id: e.target.value ? parseInt(e.target.value) : null }))}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition bg-white"
            >
              <option value="">Select grade level</option>
              {gradeLevels.map(g => (
                <option key={g.grade_level_id} value={g.grade_level_id}>{g.name}</option>
              ))}
            </select>
          </div>

          {/* Subjects (multi-select chips) */}
          {subjects.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Subjects they need help with</label>
              <div className="flex flex-wrap gap-2">
                {subjects.map(s => {
                  const isSelected = selectedSubjects.includes(s.subject_id)
                  return (
                    <button
                      type="button"
                      key={s.subject_id}
                      onClick={() => toggleSubject(s.subject_id)}
                      className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                        isSelected
                          ? 'bg-primary-600 text-white'
                          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                      }`}
                    >
                      {s.name}
                    </button>
                  )
                })}
              </div>
            </div>
          )}

          {/* Submit */}
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-accent-700 hover:bg-accent-800 text-white font-semibold py-3 rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting
              ? (editData ? 'Saving...' : 'Adding...')
              : (editData ? 'Save Changes' : 'Add Child')}
          </button>
        </form>
      </div>
    </div>
  )
}

export default AddChildModal
