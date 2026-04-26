import React, { useEffect, useState } from 'react';
import { FiCheckCircle, FiXCircle, FiEye } from 'react-icons/fi';

const ModerationList: React.FC = () => {
    const [resources, setResources] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        fetchResources();
    }, []);

    const fetchResources = async () => {
        try {
            const response = await fetch(`${(import.meta as any).env.VITE_API_URL}/api/admin/resources`, {
                headers: {
                    /* access_token cookie sent automatically */
                }
            });
            const data = await response.json();
            setResources(data);
        } catch (error) {
            console.error('Failed to fetch resources:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleModerate = async (resourceId: number, status: string) => {
        try {
            const response = await fetch(`${(import.meta as any).env.VITE_API_URL}/api/admin/resources/${resourceId}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    /* access_token cookie sent automatically */
                },
                body: JSON.stringify({ status, notes: `Action taken by Admin at ${new Date().toLocaleString()}` })
            });
            if (response.ok) fetchResources();
        } catch (error) {
            console.error('Failed to moderate resource:', error);
        }
    };

    if (isLoading) return <div className="animate-pulse">Loading resources...</div>;

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold text-gray-900">Resource Moderation</h2>
                <p className="text-gray-500">Review flagged or reported content.</p>
            </div>

            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {resources.map((res) => (
                    <div key={res.lesson_resources_id} className="bg-white shadow rounded-lg border border-gray-200 flex flex-col">
                        <div className="p-4 flex-1">
                            <div className="flex items-center justify-between mb-2">
                                <span className={`px-2 py-0.5 text-xs font-bold rounded-full uppercase ${res.status === 'flagged' ? 'bg-red-100 text-red-700' :
                                    res.status === 'approved' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                                    }`}>
                                    {res.status}
                                </span>
                                <span className="text-xs text-gray-400">{new Date(res.created_at).toLocaleDateString()}</span>
                            </div>
                            <h4 className="text-sm font-bold text-gray-900 mb-1">Resource ID: {res.lesson_resources_id}</h4>
                            <p className="text-xs text-gray-500 line-clamp-3 mb-4">
                                {res.ai_generated_content || 'No content available.'}
                            </p>
                        </div>
                        <div className="bg-gray-50 p-3 flex justify-around border-t border-gray-200">
                            <button
                                onClick={() => handleModerate(res.lesson_resources_id, 'safe')}
                                className="text-green-600 hover:text-green-700 p-1 flex items-center text-xs font-bold"
                            >
                                <FiCheckCircle className="mr-1" /> Approve
                            </button>
                            <button
                                onClick={() => handleModerate(res.lesson_resources_id, 'removed')}
                                className="text-red-600 hover:text-red-700 p-1 flex items-center text-xs font-bold"
                            >
                                <FiXCircle className="mr-1" /> Reject
                            </button>
                            <button
                                className="text-indigo-600 hover:text-indigo-700 p-1 flex items-center text-xs font-bold"
                                onClick={() => alert(res.ai_generated_content)}
                            >
                                <FiEye className="mr-1" /> View
                            </button>
                        </div>
                    </div>
                ))}
                {resources.length === 0 && (
                    <div className="col-span-full p-12 text-center text-gray-500 bg-gray-50 rounded-lg border-2 border-dashed border-gray-200">
                        No resources pending moderation.
                    </div>
                )}
            </div>
        </div>
    );
};

export default ModerationList;
