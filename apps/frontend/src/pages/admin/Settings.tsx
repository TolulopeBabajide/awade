import React from 'react';
import { FiSliders, FiLock, FiGlobe } from 'react-icons/fi';

const AdminSettings: React.FC = () => {
    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold text-gray-900">Platform Settings</h2>
                <p className="text-gray-500">Global configuration and system preferences.</p>
            </div>

            <div className="bg-white shadow rounded-lg divide-y divide-gray-200">
                <div className="p-6">
                    <div className="flex items-center space-x-3 mb-4">
                        <FiGlobe className="text-indigo-500 w-5 h-5" />
                        <h3 className="text-lg font-medium text-gray-900">General Configuration</h3>
                    </div>
                    <div className="grid grid-cols-1 gap-y-6 sm:grid-cols-2 sm:gap-x-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Platform Name</label>
                            <input type="text" defaultValue="Awade" className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Maintenance Mode</label>
                            <div className="mt-2 flex items-center">
                                <button type="button" className="bg-gray-200 relative inline-flex flex-shrink-0 h-6 w-11 border-2 border-transparent rounded-full cursor-pointer transition-colors ease-in-out duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                                    <span className="translate-x-0 pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow transform ring-0 transition ease-in-out duration-200"></span>
                                </button>
                                <span className="ml-3 text-sm text-gray-500">Disabled</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="p-6">
                    <div className="flex items-center space-x-3 mb-4">
                        <FiLock className="text-indigo-500 w-5 h-5" />
                        <h3 className="text-lg font-medium text-gray-900">Security & Registration</h3>
                    </div>
                    <div className="space-y-4">
                        <div className="flex items-center justify-between">
                            <span className="flex flex-col">
                                <span className="text-sm font-medium text-gray-900">Allow New User Registrations</span>
                                <span className="text-sm text-gray-500">Disable this to prevent new users from creating accounts.</span>
                            </span>
                            <button type="button" className="bg-indigo-600 relative inline-flex flex-shrink-0 h-6 w-11 border-2 border-transparent rounded-full cursor-pointer transition-colors ease-in-out duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                                <span className="translate-x-5 pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow transform ring-0 transition ease-in-out duration-200"></span>
                            </button>
                        </div>
                    </div>
                </div>

                <div className="p-6">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                            <FiSliders className="text-indigo-500 w-5 h-5" />
                            <h3 className="text-lg font-medium text-gray-900">System Parameters</h3>
                        </div>
                        <button className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 font-medium transition-colors">
                            Save Changes
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AdminSettings;
