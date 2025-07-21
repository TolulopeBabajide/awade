import React from 'react'
import { Routes, Route } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import SignupPage from './pages/SignupPage'
import LoginPage from './pages/LoginPage'
import ResetPasswordPage from './pages/ResetPasswordPage'
import DashboardPage from './pages/DashboardPage'
import LessonPlansPage from './pages/LessonPlansPage'
import LessonPlanDetailPage from './pages/LessonPlanDetailPage'
import EditLessonPlanPage from './pages/EditLessonPlanPage'

function App() {
  return (
    <div className="App">
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/lesson-plans" element={<LessonPlansPage />} />
        <Route path="/lesson-plans/:id" element={<LessonPlanDetailPage />} />
        <Route path="/lesson-plans/:id/edit" element={<EditLessonPlanPage />} />
        {/* Add more routes as needed */}
      </Routes>
    </div>
  )
}

export default App 