import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { FaHome, FaBookOpen, FaFolder, FaCog, FaSignOutAlt } from 'react-icons/fa';
import { useAuth } from '../contexts/AuthContext';

interface SidebarProps {
  currentPage: 'dashboard' | 'lesson-plans' | 'lesson-resources' | 'edit-resource';
  showLogo?: boolean;
  showLogout?: boolean;
  className?: string;
}

const Sidebar: React.FC<SidebarProps> = ({ 
  currentPage, 
  showLogo = true, 
  showLogout = true,
  className = ''
}) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { logout } = useAuth();

  const getActiveClass = (page: string) => {
    return currentPage === page 
      ? 'bg-accent-600 text-white' 
      : 'hover:bg-gray-100 text-gray-700';
  };

  const getIconColor = (page: string) => {
    return currentPage === page ? 'text-white' : 'text-gray-700';
  };

  return (
    <aside className={`hidden w-full lg:w-64 bg-white border-b lg:border-b-0 lg:border-r border-gray-200 lg:flex flex-row lg:flex-col pb-3 md:pb-4 lg:pb-8 px-2 md:px-4 lg:px-4 lg:min-h-screen lg:fixed lg:left-0 lg:top-0 lg:z-50 items-center lg:items-stretch flex-shrink-0 shadow-lg ${className}`}>
      {/* Logo */}
      {showLogo && (
        <div className="items-center mb-8 lg:mb-8 w-full justify-center">
          <span className="font-bold text-3xl text-center tracking-wide text-primary-800">AWADE</span>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 space-y-2 w-full hidden lg:block">
        <button 
          className={`w-full text-left px-4 py-3 rounded-lg font-medium flex items-center transition-colors duration-200 ${getActiveClass('dashboard')}`}
          onClick={() => navigate('/dashboard')}
        >
          <FaHome className={`w-4 h-4 mr-3 ${getIconColor('dashboard')}`} />
          Dashboard
        </button>
        
        <button 
          className={`w-full text-left px-4 py-3 rounded-lg font-medium flex items-center transition-colors duration-200 ${getActiveClass('lesson-plans')}`}
          onClick={() => navigate('/lesson-plans')}
        >
          <FaBookOpen className={`w-4 h-4 mr-3 ${getIconColor('lesson-plans')}`} />
          Lesson Plans
        </button>
        
        <button 
          className={`w-full text-left px-4 py-3 rounded-lg font-medium flex items-center transition-colors duration-200 ${getActiveClass('lesson-resources')}`}
          onClick={() => navigate('/lesson-resources')}
        >
          <FaFolder className={`w-4 h-4 mr-3 ${getIconColor('lesson-resources')}`} />
          Resources
        </button>
        
        <button 
          className={`w-full text-left px-4 py-3 rounded-lg font-medium flex items-center transition-colors duration-200 ${getActiveClass('edit-resource')}`}
          onClick={() => navigate('/dashboard')}
        >
          <FaCog className={`w-4 h-4 mr-3 ${getIconColor('edit-resource')}`} />
          Settings
        </button>
      </nav>

      {/* Logout */}
      {showLogout && (
        <button 
          className="mt-8 text-left px-4 py-3 text-red-500 hover:text-red-700 hover:bg-red-50 rounded-lg hidden lg:flex items-center transition-colors duration-200" 
          onClick={logout}
        >
          <FaSignOutAlt className="w-4 h-4 mr-3" />
          Log out
        </button>
      )}
    </aside>
  );
};

export default Sidebar;
