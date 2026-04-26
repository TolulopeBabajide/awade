import React, { useEffect, useState } from 'react';
import { FiSearch, FiUser, FiEye, FiShield } from 'react-icons/fi';

interface AdminChildProfile {
    child_id: number;
    parent_id: number;
    name: string;
    age: number | null;
    school_name: string | null;
    country_id: number | null;
    curricula_id: number | null;
    grade_level_id: number | null;
    subjects: string | null;
    created_at: string;
    updated_at: string;
}

const ChildProfileList: React.FC = () => {
    const [children, setChildren] = useState<AdminChildProfile[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [search, setSearch] = useState('');
    const [parentIdFilter, setParentIdFilter] = useState('');

    useEffect(() => {
        fetchChildren();
    }, []);

    const fetchChildren = async (parentId?: number) => {
        setIsLoading(true);
        setError(null);
        try {
            const params = new URLSearchParams({ limit: '200' });
            if (parentId !== undefined) params.set('parent_id', String(parentId));
            const response = await fetch(
                `${(import.meta as any).env.VITE_API_URL}/api/admin/children?${params}`,
                { credentials: 'include' }
            );
            if (!response.ok) {
                throw new Error(`Request failed: ${response.status}`);
            }
            const data: AdminChildProfile[] = await response.json();
            setChildren(data);
        } catch {
            setError('Failed to load child profiles. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleParentFilter = () => {
        const id = parseInt(parentIdFilter, 10);
        if (parentIdFilter === '') {
            fetchChildren();
        } else if (!isNaN(id)) {
            fetchChildren(id);
        }
    };

    const handleClearFilter = () => {
        setParentIdFilter('');
        fetchChildren();
    };

    const filteredChildren = children.filter((child) =>
        child.name.toLowerCase().includes(search.toLowerCase()) ||
        String(child.parent_id).includes(search)
    );

    const subjectCount = (subjectsJson: string | null): number => {
        if (!subjectsJson) return 0;
        try {
            const parsed = JSON.parse(subjectsJson);
            return Array.isArray(parsed) ? parsed.length : 0;
        } catch {
            return 0;
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-start">
                <div>
                    <h2 className="text-2xl font-bold text-gray-900">Child Profiles</h2>
                    <p className="text-gray-500 mt-1">
                        Read-only oversight view. All access is audit-logged per COPPA/GRC-05.
                    </p>
                </div>
                <div className="flex items-center space-x-1 text-xs text-indigo-700 bg-indigo-50 border border-indigo-200 rounded px-3 py-1.5">
                    <FiShield size={13} className="mr-1" />
                    COPPA Audited
                </div>
            </div>

            {/* Filters */}
            <div className="flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-3">
                <div className="relative flex-1">
                    <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                    <input
                        type="text"
                        placeholder="Search by child name or parent ID..."
                        className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        aria-label="Search child profiles"
                    />
                </div>
                <div className="flex space-x-2">
                    <input
                        type="number"
                        placeholder="Filter by parent ID"
                        className="w-44 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
                        value={parentIdFilter}
                        onChange={(e) => setParentIdFilter(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleParentFilter()}
                        aria-label="Filter by parent ID"
                    />
                    <button
                        onClick={handleParentFilter}
                        className="px-3 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors text-sm font-medium"
                    >
                        Apply
                    </button>
                    {parentIdFilter && (
                        <button
                            onClick={handleClearFilter}
                            className="px-3 py-2 border border-gray-300 text-gray-600 rounded-lg hover:bg-gray-50 transition-colors text-sm"
                        >
                            Clear
                        </button>
                    )}
                </div>
            </div>

            {/* Loading */}
            {isLoading && (
                <div className="flex justify-center py-12" role="status" aria-label="Loading child profiles">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600" />
                </div>
            )}

            {/* Error */}
            {!isLoading && error && (
                <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-center" role="alert">
                    <p className="text-red-700 text-sm">{error}</p>
                    <button
                        onClick={() => fetchChildren()}
                        className="mt-3 text-sm text-red-600 underline hover:text-red-800"
                    >
                        Retry
                    </button>
                </div>
            )}

            {/* Table */}
            {!isLoading && !error && (
                <div className="bg-white shadow rounded-lg overflow-hidden border border-gray-200">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Child
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Parent ID
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Age
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    School
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Subjects
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Created
                                </th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {filteredChildren.map((child) => (
                                <tr key={child.child_id} className="hover:bg-gray-50">
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="flex items-center">
                                            <div className="h-9 w-9 rounded-full bg-purple-100 flex items-center justify-center text-purple-700">
                                                <FiUser size={15} />
                                            </div>
                                            <div className="ml-3">
                                                <div className="text-sm font-medium text-gray-900">
                                                    {child.name}
                                                </div>
                                                <div className="text-xs text-gray-400">
                                                    ID: {child.child_id}
                                                </div>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <button
                                            onClick={() => {
                                                setParentIdFilter(String(child.parent_id));
                                                fetchChildren(child.parent_id);
                                            }}
                                            className="inline-flex items-center text-sm text-indigo-600 hover:text-indigo-900 font-medium"
                                            title={`Show all children for parent ${child.parent_id}`}
                                        >
                                            <FiEye size={13} className="mr-1" />
                                            {child.parent_id}
                                        </button>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                                        {child.age !== null ? child.age : <span className="text-gray-400">—</span>}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 max-w-xs truncate">
                                        {child.school_name ?? <span className="text-gray-400">—</span>}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                                        {subjectCount(child.subjects) > 0 ? (
                                            <span className="px-2 py-0.5 bg-gray-100 text-gray-700 rounded-full text-xs">
                                                {subjectCount(child.subjects)} subject{subjectCount(child.subjects) !== 1 ? 's' : ''}
                                            </span>
                                        ) : (
                                            <span className="text-gray-400">—</span>
                                        )}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {new Date(child.created_at).toLocaleDateString()}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>

                    {filteredChildren.length === 0 && (
                        <div className="p-10 text-center text-gray-500">
                            <FiUser size={32} className="mx-auto mb-3 text-gray-300" />
                            <p className="text-sm">No child profiles found.</p>
                            {(search || parentIdFilter) && (
                                <p className="text-xs text-gray-400 mt-1">
                                    Try adjusting your search or filter.
                                </p>
                            )}
                        </div>
                    )}
                </div>
            )}

            {!isLoading && !error && filteredChildren.length > 0 && (
                <p className="text-xs text-gray-400 text-right">
                    Showing {filteredChildren.length} of {children.length} profiles
                </p>
            )}
        </div>
    );
};

export default ChildProfileList;
