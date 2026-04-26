import React from 'react'
import { useAuth } from '../contexts/AuthContext'
import ParentDashboardPage from '../pages/ParentDashboardPage'
import DashboardPage from '../pages/DashboardPage'

/**
 * Routes the user to the correct dashboard based on their role.
 * - PARENT → ParentDashboardPage (child-selector + topic browser)
 * - EDUCATOR / ADMIN → Original DashboardPage (lesson plan generator)
 */
const RoleDashboard: React.FC = () => {
  const { user } = useAuth()

  if (user?.role === 'PARENT') {
    return <ParentDashboardPage />
  }

  return <DashboardPage />
}

export default RoleDashboard
