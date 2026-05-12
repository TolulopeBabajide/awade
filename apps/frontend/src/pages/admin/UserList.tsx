import React, { useEffect, useState } from 'react';
import { FiSearch, FiFilter, FiMoreVertical } from 'react-icons/fi';
import ConfirmRoleChangeModal from '../../components/ConfirmRoleChangeModal';
import ErrorBanner from '../../components/ErrorBanner';

// AWD-M-144: tracks a pending role-change confirmation before the modal fires.
interface PendingRoleChange {
    userId: number;
    userName: string;
    newRole: string;
}

const UserList: React.FC = () => {
    const [users, setUsers] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [actionError, setActionError] = useState<string | null>(null);
    // AWD-M-144: replaces inline window.confirm() with an accessible modal.
    const [pendingRoleChange, setPendingRoleChange] = useState<PendingRoleChange | null>(null);

    useEffect(() => {
        fetchUsers();
    }, []);

    const fetchUsers = async () => {
        try {
            const response = await fetch(`${(import.meta as any).env.VITE_API_URL}/api/admin/users`, {
                headers: {
                    /* access_token cookie sent automatically */
                }
            });
            const data = await response.json();
            setUsers(data);
        } catch (error) {
            if (import.meta.env.DEV) console.error('Failed to fetch users:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleRoleChange = async (userId: number, newRole: string) => {
        setActionError(null);
        try {
            const response = await fetch(`${(import.meta as any).env.VITE_API_URL}/api/admin/users/${userId}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    /* access_token cookie sent automatically */
                },
                body: JSON.stringify({ role: newRole })
            });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            fetchUsers();
        } catch (error) {
            if (import.meta.env.DEV) console.error('Failed to change role:', error);
            setActionError(error instanceof Error ? error.message : 'Failed to update role. Please try again.');
        }
    };

    /**
     * AWD-M-144: invoked from ConfirmRoleChangeModal's "Confirm" button.
     * Closes the modal and performs the actual role change.
     */
    const confirmRoleChange = async () => {
        if (!pendingRoleChange) return;
        const { userId, newRole } = pendingRoleChange;
        setPendingRoleChange(null);
        await handleRoleChange(userId, newRole);
    };

    const handleToggleSuspension = async (userId: number, currentStatus: boolean) => {
        setActionError(null);
        try {
            const response = await fetch(`${(import.meta as any).env.VITE_API_URL}/api/admin/users/${userId}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    /* access_token cookie sent automatically */
                },
                body: JSON.stringify({ is_suspended: !currentStatus })
            });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            fetchUsers();
        } catch (error) {
            if (import.meta.env.DEV) console.error('Failed to toggle suspension:', error);
            setActionError(error instanceof Error ? error.message : 'Failed to update suspension status. Please try again.');
        }
    };

    const filteredUsers = users.filter(user =>
        user.full_name?.toLowerCase().includes(search.toLowerCase()) ||
        user.email?.toLowerCase().includes(search.toLowerCase())
    );

    if (isLoading) return <div className="animate-pulse">Loading users...</div>;

    return (
        <div className="space-y-6">
            {/* AWD-M-144: accessible role-change confirmation modal */}
            {pendingRoleChange && (
                <ConfirmRoleChangeModal
                    userName={pendingRoleChange.userName}
                    newRole={pendingRoleChange.newRole}
                    onConfirm={confirmRoleChange}
                    onCancel={() => setPendingRoleChange(null)}
                />
            )}

            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-2xl font-bold text-gray-900">User Management</h2>
                    <p className="text-gray-500">View and manage all platform users.</p>
                </div>
            </div>

            {actionError && (
                <ErrorBanner
                    message={actionError}
                    onDismiss={() => setActionError(null)}
                />
            )}

            <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4">
                <div className="relative flex-1">
                    <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                    <input
                        type="text"
                        placeholder="Search by name or email..."
                        className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                    />
                </div>
                <button className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg bg-white text-gray-700 hover:bg-gray-50 transition-colors">
                    <FiFilter className="mr-2" />
                    Filter
                </button>
            </div>

            <div className="bg-white shadow rounded-lg overflow-hidden border border-gray-200">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Login</th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {filteredUsers.map((user) => (
                            <tr key={user.user_id}>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="flex items-center">
                                        <div className="h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-700 font-bold">
                                            {user.full_name?.charAt(0)}
                                        </div>
                                        <div className="ml-4">
                                            <div className="text-sm font-medium text-gray-900">{user.full_name}</div>
                                            <div className="text-sm text-gray-500">{user.email}</div>
                                        </div>
                                    </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="flex flex-col space-y-1">
                                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${user.role === 'SUPER_ADMIN' ? 'bg-purple-100 text-purple-800' :
                                            user.role === 'ADMIN' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'
                                            }`}>
                                            {user.role}
                                        </span>
                                        {user.is_suspended === 1 && (
                                            <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
                                                Suspended
                                            </span>
                                        )}
                                    </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    {new Date(user.created_at).toLocaleDateString()}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    {user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                    <div className="flex justify-end space-x-2">
                                        <button
                                            onClick={() => handleToggleSuspension(user.user_id, user.is_suspended === 1)}
                                            className={`text-xs px-2 py-1 rounded border ${user.is_suspended === 1 ? 'border-green-300 text-green-600 hover:bg-green-50' : 'border-red-300 text-red-600 hover:bg-red-50'}`}
                                        >
                                            {user.is_suspended === 1 ? 'Unsuspend' : 'Suspend'}
                                        </button>
                                        <button
                                            title="Manage Role"
                                            className="text-indigo-600 hover:text-indigo-900 p-1"
                                            onClick={() => {
                                                // AWD-M-144: open the accessible confirmation modal instead of
                                                // calling blocking window.confirm().
                                                const nextRole = user.role === 'EDUCATOR' ? 'ADMIN' : (user.role === 'ADMIN' ? 'SUPER_ADMIN' : 'EDUCATOR');
                                                setPendingRoleChange({
                                                    userId: user.user_id,
                                                    userName: user.full_name,
                                                    newRole: nextRole,
                                                });
                                            }}
                                        >
                                            <FiMoreVertical />
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                {filteredUsers.length === 0 && (
                    <div className="p-8 text-center text-gray-500">No users found.</div>
                )}
            </div>
        </div>
    );
};

export default UserList;
