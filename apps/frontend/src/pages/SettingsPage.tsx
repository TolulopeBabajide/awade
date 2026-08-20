import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import Sidebar from '../components/Sidebar';
import MobileNavigation from '../components/MobileNavigation';
import { FaCog } from 'react-icons/fa';
import {
  ProfileTab,
  SecurityTab,
  LanguageTab,
  SettingsMenu,
} from './SettingsPage.components';

type Tab = 'profile' | 'security' | 'language';

const SettingsPage: React.FC = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<Tab>('profile');
  const [showSettingsMenu, setShowSettingsMenu] = useState(false);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Element;
      if (showSettingsMenu && !target.closest('.settings-menu-container')) {
        setShowSettingsMenu(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showSettingsMenu]);

  if (!user) {
    return <div>Loading...</div>;
  }

  return (
    <div className="bg-gray-50 flex min-h-screen">
      <Sidebar currentPage="settings" />

      <main className="flex-1 lg:ml-64 p-4 md:p-6 lg:p-8 pb-20 lg:pb-8">
        {/* Header */}
        <div className="flex justify-between items-start pt-0 pb-2 md:pb-4 lg:pb-5 px-2 md:px-4 lg:px-5 gap-2 md:gap-4 flex-shrink-0">
          <div className="flex-1">
            <div className="text-left">
              <h2 className="text-xl md:text-2xl lg:text-3xl xl:text-4xl font-bold mb-1 md:mb-2 text-gray-900 mt-0 pt-0">
                Account Settings
              </h2>
              <p className="text-sm md:text-base lg:text-lg text-gray-600">
                Manage your profile, security, and preferences.
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2 md:space-x-3 flex-shrink-0">
            <div className="relative settings-menu-container">
              <button
                data-testid="settings-cog"
                onClick={() => setShowSettingsMenu(!showSettingsMenu)}
                className="w-8 h-8 md:w-10 md:h-10 bg-accent-600 rounded-full flex items-center justify-center hover:bg-accent-700 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:ring-offset-2"
              >
                <FaCog className="w-4 h-4 md:w-5 md:h-5 text-white" />
              </button>

              {showSettingsMenu && (
                <SettingsMenu
                  activeTab={activeTab}
                  onTabChange={setActiveTab}
                  onClose={() => setShowSettingsMenu(false)}
                />
              )}
            </div>
          </div>
        </div>

        {/* Tab content */}
        <div className="flex-1 p-2 md:p-4 lg:p-8 overflow-y-auto">
          <div className="flex-1">
            {activeTab === 'profile' && <ProfileTab />}
            {activeTab === 'security' && <SecurityTab />}
            {activeTab === 'language' && <LanguageTab />}
          </div>
        </div>

        <MobileNavigation />
      </main>
    </div>
  );
};

export default SettingsPage;
