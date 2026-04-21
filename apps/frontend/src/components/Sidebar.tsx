import React from 'react';
import { useNavigate } from 'react-router-dom';
import { FaHome, FaBookOpen, FaFolder, FaCog, FaSignOutAlt, FaBookmark } from 'react-icons/fa';
import { useAuth } from '../contexts/AuthContext';

interface SidebarProps {
  currentPage: 'dashboard' | 'lesson-plans' | 'lesson-resources' | 'settings' | 'children' | 'saved-guides';
  showLogo?: boolean;
  showLogout?: boolean;
  className?: string;
}

interface NavItem {
  id: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  path: string;
}

const Sidebar: React.FC<SidebarProps> = ({
  currentPage,
  showLogo = true,
  showLogout = true,
  className = ''
}) => {
  const navigate = useNavigate();
  const { logout, user } = useAuth();

  const isParent = user?.role === 'PARENT';

  // Different nav items based on role
  const parentNavItems: NavItem[] = [
    { id: 'dashboard', label: 'Home', icon: FaHome, path: '/dashboard' },
    { id: 'saved-guides', label: 'Saved Guides', icon: FaBookmark, path: '/saved-guides' },
    { id: 'settings', label: 'Settings', icon: FaCog, path: '/settings' },
  ];

  const educatorNavItems: NavItem[] = [
    { id: 'dashboard', label: 'Dashboard', icon: FaHome, path: '/dashboard' },
    { id: 'lesson-plans', label: 'Lesson Plans', icon: FaBookOpen, path: '/lesson-plans' },
    { id: 'lesson-resources', label: 'Resources', icon: FaFolder, path: '/lesson-resources' },
    { id: 'settings', label: 'Settings', icon: FaCog, path: '/settings' },
  ];

  const navItems = isParent ? parentNavItems : educatorNavItems;

  const getActiveClass = (page: string) => {
    return currentPage === page
      ? 'bg-accent-600 text-white'
      : 'hover:bg-gray-100 text-gray-700';
  };

  const getIconColor = (page: string) => {
    return currentPage === page ? 'text-white' : 'text-gray-700';
  };

  return (
    <aside className={`hidden w-full lg:w-64 bg-white border-b lg:border-b-0 lg:border-r border-gray-200 lg:flex flex-row lg:flex-col pb-3 md:pb-4 lg:pb-8 px-2 md:px-4 lg:px-4 lg:min-h-screen lg:fixed lg:left-0 lg:top-0 lg:z-[60] items-center lg:items-stretch flex-shrink-0 shadow-lg ${className}`}>
      {/* Logo */}
      {showLogo && (
        <div className="items-center mb-8 mt-12 w-full justify-center">
          <span className="font-bold text-3xl text-center tracking-wide text-primary-800">AWADE</span>
          {isParent && (
            <span className="block text-xs text-gray-400 tracking-wider mt-1">FOR PARENTS</span>
          )}
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 space-y-2 mt-12 w-full hidden lg:block">
        {navItems.map(item => {
          const Icon = item.icon;
          return (
            <button
              key={item.id}
              className={`w-full text-left px-4 py-3 rounded-lg font-medium flex items-center transition-colors duration-200 ${getActiveClass(item.id)}`}
              onClick={() => navigate(item.path)}
            >
              <Icon className={`w-4 h-4 mr-3 ${getIconColor(item.id)}`} />
              {item.label}
            </button>
          );
        })}
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
