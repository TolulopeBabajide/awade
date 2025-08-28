import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import LandingPage from './pages/LandingPage'
import SignupPage from './pages/SignupPage'
import LoginPage from './pages/LoginPage'
import ResetPasswordPage from './pages/ResetPasswordPage'
import DashboardPage from './pages/DashboardPage'
import LessonPlansPage from './pages/LessonPlansPage'
import LessonPlanDetailPage from './pages/LessonPlanDetailPage'
import EditLessonPlanPage from './pages/EditLessonPlanPage'
import EditLessonResourcePage from './pages/EditLessonResourcePage'
import LessonResourcesPage from './pages/LessonResourcesPage'
import SettingsPage from './pages/SettingsPage'
import TestPage from './pages/TestPage'
import EnvironmentDebug from './components/EnvironmentDebug'

function App() {
  return (
    <AuthProvider>
      <div className="App">
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />
          
          {/* Protected routes */}
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          } />
          <Route path="/lesson-plans" element={
            <ProtectedRoute>
              <LessonPlansPage />
            </ProtectedRoute>
          } />
          <Route path="/lesson-plans/:id" element={
            <ProtectedRoute>
              <LessonPlanDetailPage />
            </ProtectedRoute>
          } />
          <Route path="/lesson-plans/:id/edit" element={
            <ProtectedRoute>
              <EditLessonPlanPage />
            </ProtectedRoute>
          } />
          <Route path="/lesson-plans/:lessonPlanId/resources/edit" element={
            <ProtectedRoute>
              <EditLessonResourcePage />
            </ProtectedRoute>
          } />
          <Route path="/lesson-resources" element={
            <ProtectedRoute>
              <LessonResourcesPage />
            </ProtectedRoute>
          } />
          <Route path="/settings" element={
            <ProtectedRoute>
              <SettingsPage />
            </ProtectedRoute>
          } />
          <Route path="/test" element={
            <ProtectedRoute>
              <TestPage />
            </ProtectedRoute>
          } />
          {/* Add more routes as needed */}
        </Routes>
        
        {/* Environment Debug Component - Remove after fixing */}
        <EnvironmentDebug />
      </div>
    </AuthProvider>
  )
}

export default App 