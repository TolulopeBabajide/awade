import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  FaHome, 
  FaBookOpen, 
  FaFolder, 
  FaCog 
} from 'react-icons/fa';

interface MobileNavigationProps {
  currentPage?: string;
}

interface NavItem {
  id: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  path: string;
}

const MobileNavigation: React.FC<MobileNavigationProps> = ({ currentPage }) => {
  const navigate = useNavigate();
  const location = useLocation();
  
  // Determine current page if not provided
  const activePage = currentPage || location.pathname.split('/')[1] || 'dashboard';
  
  const navItems: NavItem[] = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: FaHome,
      path: '/dashboard'
    },
    {
      id: 'lesson-plans',
      label: 'Plans',
      icon: FaBookOpen,
      path: '/lesson-plans'
    },
    {
      id: 'lesson-resources',
      label: 'Resources',
      icon: FaFolder,
      path: '/lesson-resources'
    },
    {
      id: 'settings',
      label: 'Settings',
      icon: FaCog,
      path: '/settings'
    }
  ];

  const handleNavigation = (path: string) => {
    // Only navigate if we're not already on that page
    if (location.pathname !== path) {
      navigate(path);
    }
  };

  return (
    <nav className="lg:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-4 py-3 z-50 shadow-lg">
      <div className="flex justify-around items-center">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activePage === item.id;
          
          return (
            <button 
              key={item.id}
              className={`flex flex-col items-center py-2 px-3 font-medium transition-colors duration-200 ${
                isActive 
                  ? 'text-primary-600' 
                  : 'text-gray-500 hover:text-primary-600'
              }`}
              onClick={() => handleNavigation(item.path)}
              aria-label={`Navigate to ${item.label}`}
              title={item.label}
            >
              <Icon className="w-6 h-6 mb-1" />
              <span className={`text-xs ${isActive ? 'font-medium' : ''}`}>
                {item.label}
              </span>
            </button>
          );
        })}
      </div>
    </nav>
  );
};

export default MobileNavigation;
