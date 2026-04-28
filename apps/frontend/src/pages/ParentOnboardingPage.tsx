import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { FaChild, FaArrowRight, FaCheckCircle } from 'react-icons/fa'
import apiService from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import type { ChildProfileCreate } from '../types/children'

const ParentOnboardingPage: React.FC = () => {
  const navigate = useNavigate()
  const { user } = useAuth()

  const [form, setForm] = useState<ChildProfileCreate>({
    name: '',
    age: null,
    school_name: null,
    country_id: null,
    curricula_id: null,
    grade_level_id: null,
    subjects: null,
  })
  const [countries, setCountries] = useState<Array<{ country_id: number; country_name: string }>>([])
  const [curriculums, setCurriculums] = useState<Array<{ curricula_id: number; curricula_title: string }>>([])
  const [gradeLevels, setGradeLevels] = useState<Array<{ grade_level_id: number; name: string }>>([])
  const [subjectOptions, setSubjectOptions] = useState<Array<{ subject_id: number; name: string }>>([])
  const [selectedSubjects, setSelectedSubjects] = useState<number[]>([])
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [done, setDone] = useState(false)

  // Check if parent already has children — if so, skip onboarding
  const { data: childrenData, isLoading: checkingChildren } = useQuery({
    queryKey: ['children'],
    queryFn: async () => {
      const res = await apiService.getChildren()
      if (res.error) throw new Error(res.error)
      return res.data
    },
  })

  useEffect(() => {
    if (!checkingChildren && childrenData?.children && childrenData.children.length > 0) {
      navigate('/dashboard', { replace: true })
    }
  }, [checkingChildren, childrenData, navigate])

  // Load reference data (countries, grades, subjects) on mount
  useEffect(() => {
    const loadRefData = async () => {
      try {
        const [countriesRes, gradesRes, subjectsRes] = await Promise.all([
          apiService.getCountries(),
          apiService.getGradeLevels(),
          apiService.getSubjects(),
        ])
        if (countriesRes.data) setCountries(countriesRes.data)
        if (gradesRes.data) setGradeLevels(gradesRes.data)
        if (subjectsRes.data) setSubjectOptions(subjectsRes.data)
      } catch {
        setError('Failed to load options. Please refresh.')
      }
    }
    loadRefData()
  }, [])

  // Load curriculums when country changes
  useEffect(() => {
    if (!form.country_id) {
      setCurriculums([])
      setForm(f => ({ ...f, curricula_id: null }))
      return
    }
    const loadCurriculums = async () => {
      try {
        const res = await apiService.getCurriculums(form.country_id!)
        if (res.data) setCurriculums(res.data)
      } catch {
        setError('Failed to load options. Please refresh.')
      }
    }
    loadCurriculums()
  }, [form.country_id])

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
    try {
      const payload: ChildProfileCreate = {
        ...form,
        name: form.name.trim(),
        subjects: selectedSubjects.length > 0 ? selectedSubjects : null,
      }
      const res = await apiService.createChild(payload)
      if (res.error) {
        setError(res.error)
      } else {
        setDone(true)
        setTimeout(() => navigate('/dashboard', { replace: true }), 1500)
      }
    } catch {
      setError('Something went wrong. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (checkingChildren) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600" />
      </div>
    )
  }

  if (done) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100">
        <div className="text-center">
          <FaCheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-primary-800 mb-2">All set!</h2>
          <p className="text-gray-600">Taking you to your dashboard…</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex flex-col items-center justify-start py-10 px-4">
      {/* Header */}
      <div className="text-center mb-8 max-w-md">
        <div className="w-16 h-16 bg-accent-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <FaChild className="w-8 h-8 text-accent-600" />
        </div>
        <h1 className="text-3xl font-bold text-primary-800 mb-2">
          Welcome, {user?.full_name?.split(' ')[0]}!
        </h1>
        <p className="text-gray-600 text-base leading-relaxed">
          Let's add your first child's profile so we can show you the right curriculum topics and personalised "How to Help" guides.
        </p>
      </div>

      {/* Card */}
      <div className="w-full max-w-lg bg-white rounded-2xl shadow-xl p-6 sm:p-8">
        <h2 className="text-xl font-semibold text-primary-800 mb-6 flex items-center gap-2">
          <span className="w-7 h-7 rounded-full bg-primary-600 text-white text-sm flex items-center justify-center font-bold">1</span>
          Add your child's profile
        </h2>

        <form onSubmit={handleSubmit} className="space-y-5" noValidate>
          {error && (
            <div role="alert" className="bg-red-50 text-red-600 px-4 py-3 rounded-lg text-sm">{error}</div>
          )}

          {/* Name */}
          <div>
            <label htmlFor="onboarding-name" className="block text-sm font-medium text-gray-700 mb-1">
              Child's Name{' '}
              <span className="text-red-500" aria-hidden="true">*</span>
              <span className="sr-only">(required)</span>
            </label>
            <input
              id="onboarding-name"
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
              onChange={e => setForm(f => ({
                ...f,
                country_id: e.target.value ? parseInt(e.target.value) : null,
                curricula_id: null,
              }))}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition bg-white"
            >
              <option value="">Select country</option>
              {countries.map(c => (
                <option key={c.country_id} value={c.country_id}>{c.country_name}</option>
              ))}
            </select>
          </div>

          {/* Curriculum — shown only after country selected */}
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
          {subjectOptions.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Subjects they need help with
              </label>
              <div className="flex flex-wrap gap-2">
                {subjectOptions.map(s => {
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
            className="w-full bg-accent-700 hover:bg-accent-800 text-white font-semibold py-3 rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 mt-2"
          >
            {isSubmitting ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                Adding…
              </>
            ) : (
              <>
                Get Started
                <FaArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        {/* Skip */}
        <p className="text-center mt-4">
          <button
            type="button"
            onClick={() => navigate('/dashboard', { replace: true })}
            className="text-sm text-gray-400 hover:text-gray-600 underline transition-colors"
          >
            Skip for now
          </button>
        </p>
      </div>
    </div>
  )
}

export default ParentOnboardingPage
