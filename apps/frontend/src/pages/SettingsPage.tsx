import ScreenHeader from '../components/design/ScreenHeader'
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
    <div className="new-screen screen-settings bg-gray-50 flex min-h-screen">
      <Sidebar currentPage="settings" />

      <main id="main-content" tabIndex={-1} className="flex-1 min-w-0 lg:ml-64 p-4 md:p-6 lg:p-8 pb-20 lg:pb-8">
        <ScreenHeader title="Account Settings" description="Your details, your preferences, your space to learn." action={<div className="relative settings-menu-container"><button data-testid="settings-cog" aria-label="More account settings" aria-expanded={showSettingsMenu} onClick={() => setShowSettingsMenu(!showSettingsMenu)} className="learning-button-secondary"><FaCog aria-hidden="true" /> More</button>{showSettingsMenu && <SettingsMenu activeTab={activeTab} onTabChange={setActiveTab} onClose={() => setShowSettingsMenu(false)} />}</div>} />
        <div className="screen-settings-layout">
          <nav className="screen-settings-nav" aria-label="Settings sections">{([{ id: 'profile', label: 'Profile details' }, { id: 'security', label: 'Account access' }, { id: 'language', label: 'Display language' }] as const).map(tab => <button key={tab.id} type="button" aria-pressed={activeTab === tab.id} onClick={() => setActiveTab(tab.id)}>{tab.label}</button>)}</nav>
        {/* Tab content */}
        <div className="screen-settings-content min-w-0">
          <div className="flex-1">
            {activeTab === 'profile' && <ProfileTab />}
            {activeTab === 'security' && <SecurityTab />}
            {activeTab === 'language' && <LanguageTab />}
          </div>
        </div>

        </div>
        <MobileNavigation currentPage="settings" />
      </main>
    </div>
  );
};

export default SettingsPage;
