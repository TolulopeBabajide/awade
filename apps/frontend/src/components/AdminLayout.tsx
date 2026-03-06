import React, { useState } from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
    FiLayout,
    FiUsers,
    FiFileText,
    FiShield,
    FiBookOpen,
    FiSettings,
    FiLogOut,
    FiMenu,
    FiX,
    FiClock
} from 'react-icons/fi';

const AdminLayout: React.FC = () => {
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const { user, logout } = useAuth();

    const navItems = [
        { name: 'Dashboard', path: '/admin', icon: FiLayout },
        { name: 'User Management', path: '/admin/users', icon: FiUsers },
        { name: 'Lesson Resources', path: '/admin/resources', icon: FiFileText },
        { name: 'Moderation', path: '/admin/moderation', icon: FiShield },
        { name: 'Curriculum', path: '/admin/curriculum', icon: FiBookOpen },
        { name: 'Audit Logs', path: '/admin/logs', icon: FiClock },
        { name: 'Settings', path: '/admin/settings', icon: FiSettings },
    ];

    return (
        <div className="min-h-screen bg-gray-50 flex">
            {/* Sidebar */}
            <aside
                className={`${isSidebarOpen ? 'w-64' : 'w-20'
                    } bg-slate-900 text-white transition-all duration-300 flex flex-col fixed inset-y-0 z-50`}
            >
                <div className="p-6 flex items-center justify-between">
                    <h1 className={`font-bold text-xl ${!isSidebarOpen && 'hidden'}`}>Awade Admin</h1>
                    <button onClick={() => setIsSidebarOpen(!isSidebarOpen)} className="p-1 hover:bg-slate-800 rounded">
                        {isSidebarOpen ? <FiX size={20} /> : <FiMenu size={20} />}
                    </button>
                </div>

                <nav className="flex-1 px-4 py-4 space-y-2">
                    {navItems.map((item) => (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            className={({ isActive }) =>
                                `flex items-center p-3 rounded-lg transition-colors ${isActive ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:bg-slate-800 hover:text-white'
                                }`
                            }
                        >
                            <item.icon size={20} />
                            <span className={`ml-4 ${!isSidebarOpen && 'hidden'}`}>{item.name}</span>
                        </NavLink>
                    ))}
                </nav>

                <div className="p-4 border-t border-slate-800">
                    <button
                        onClick={logout}
                        className="flex items-center w-full p-3 text-slate-400 hover:bg-slate-800 hover:text-white rounded-lg transition-colors"
                    >
                        <FiLogOut size={20} />
                        <span className={`ml-4 ${!isSidebarOpen && 'hidden'}`}>Logout</span>
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <main className={`flex-1 flex flex-col transition-all duration-300 ${isSidebarOpen ? 'ml-64' : 'ml-20'}`}>
                <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-8 sticky top-0 z-40">
                    <div className="flex items-center">
                        <span className="text-gray-500 font-medium">Hello, {user?.full_name}</span>
                        <span className="ml-2 px-2 py-0.5 bg-indigo-100 text-indigo-700 text-xs font-bold rounded-full uppercase">
                            {user?.role}
                        </span>
                    </div>

                    <div className="flex items-center space-x-4">
                        <button className="text-gray-400 hover:text-gray-600">
                            <span className="sr-only">Notifications</span>
                            <div className="relative">
                                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                                </svg>
                                <span className="absolute top-0 right-0 block h-2 w-2 rounded-full bg-red-500 border-2 border-white"></span>
                            </div>
                        </button>
                    </div>
                </header>

                <div className="p-8 flex-1">
                    <Outlet />
                </div>
            </main>
        </div>
    );
};

export default AdminLayout;
