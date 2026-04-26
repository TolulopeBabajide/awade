import { Routes, Route } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import LandingPage from './pages/LandingPage'
import SignupPage from './pages/SignupPage'
import LoginPage from './pages/LoginPage'
import ResetPasswordPage from './pages/ResetPasswordPage'
import RoleDashboard from './components/RoleDashboard'
import LessonPlansPage from './pages/LessonPlansPage'
import LessonPlanDetailPage from './pages/LessonPlanDetailPage'
import EditLessonPlanPage from './pages/EditLessonPlanPage'
import EditLessonResourcePage from './pages/EditLessonResourcePage'
import LessonResourcesPage from './pages/LessonResourcesPage'
import SettingsPage from './pages/SettingsPage'
import TestPage from './pages/TestPage'
import GuideViewPage from './pages/GuideViewPage'
import SavedGuidesPage from './pages/SavedGuidesPage'
import ChildrenPage from './pages/ChildrenPage'
import AdminRoute from './components/AdminRoute'
import ParentRoute from './components/ParentRoute'
import ParentOnboardingPage from './pages/ParentOnboardingPage'
import AdminLayout from './components/AdminLayout'
import AdminDashboard from './pages/admin/Dashboard'
import UserList from './pages/admin/UserList'
import AuditLogs from './pages/admin/AuditLogs'
import ModerationList from './pages/admin/ModerationList'
import CurriculumManager from './pages/admin/CurriculumManager'
import TemplateManager from './pages/admin/TemplateManager'
import AdminSettings from './pages/admin/Settings'
import ChildProfileList from './pages/admin/ChildProfileList'

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

          {/* Protected routes — role-aware dashboard */}
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <RoleDashboard />
            </ProtectedRoute>
          } />

          {/* Parent routes — PARENT role only */}
          <Route path="/onboarding" element={
            <ParentRoute>
              <ParentOnboardingPage />
            </ParentRoute>
          } />
          <Route path="/children" element={
            <ParentRoute>
              <ChildrenPage />
            </ParentRoute>
          } />
          <Route path="/guides/generate" element={
            <ParentRoute>
              <GuideViewPage />
            </ParentRoute>
          } />
          <Route path="/saved-guides" element={
            <ParentRoute>
              <SavedGuidesPage />
            </ParentRoute>
          } />

          {/* Educator routes (kept for EDUCATOR role) */}
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

          {/* Admin routes */}
          <Route path="/admin" element={
            <AdminRoute>
              <AdminLayout />
            </AdminRoute>
          }>
            <Route index element={<AdminDashboard />} />
            <Route path="users" element={<UserList />} />
            <Route path="resources" element={<ModerationList />} />
            <Route path="moderation" element={<ModerationList />} />
            <Route path="curriculum" element={<CurriculumManager />} />
            <Route path="templates" element={<TemplateManager />} />
            <Route path="logs" element={<AuditLogs />} />
            <Route path="children" element={<ChildProfileList />} />
            <Route path="settings" element={<AdminSettings />} />
          </Route>
        </Routes>
      </div>
    </AuthProvider>
  )
}

export default App
