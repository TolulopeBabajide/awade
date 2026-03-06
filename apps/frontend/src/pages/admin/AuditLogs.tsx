import React, { useEffect, useState } from 'react';
import { FiClock, FiUser, FiLayers } from 'react-icons/fi';

const AuditLogs: React.FC = () => {
    const [logs, setLogs] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchLogs = async () => {
            try {
                const response = await fetch(`${(import.meta as any).env.VITE_API_URL}/api/admin/audit-logs`, {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                    }
                });
                const data = await response.json();
                setLogs(data);
            } catch (error) {
                console.error('Failed to fetch logs:', error);
            } finally {
                setIsLoading(false);
            }
        };

        fetchLogs();
    }, []);

    if (isLoading) return <div className="animate-pulse">Loading audit logs...</div>;

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold text-gray-900">Audit Logs</h2>
                <p className="text-gray-500">History of administrative and security events.</p>
            </div>

            <div className="bg-white shadow rounded-lg overflow-hidden border border-gray-200">
                <ul className="divide-y divide-gray-200">
                    {logs.map((log) => (
                        <li key={log.log_id} className="p-4 hover:bg-gray-50 transition-colors">
                            <div className="flex items-center space-x-4">
                                <div className="flex-shrink-0">
                                    <div className="h-10 w-10 rounded-full bg-gray-100 flex items-center justify-center text-gray-500">
                                        <FiClock />
                                    </div>
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center justify-between">
                                        <p className="text-sm font-medium text-gray-900 truncate">
                                            {log.action}
                                        </p>
                                        <p className="text-xs text-gray-500">
                                            {new Date(log.created_at).toLocaleString()}
                                        </p>
                                    </div>
                                    <div className="mt-1 flex items-center text-sm text-gray-500 space-x-4">
                                        <span className="flex items-center">
                                            <FiUser className="mr-1.5 h-4 w-4 flex-shrink-0" />
                                            {log.actor_name || `User #${log.actor_id}`}
                                        </span>
                                        <span className="flex items-center">
                                            <FiLayers className="mr-1.5 h-4 w-4 flex-shrink-0" />
                                            {log.target_type}: {log.target_id || 'N/A'}
                                        </span>
                                    </div>
                                    {log.metadata_json && (
                                        <div className="mt-2 text-xs bg-gray-50 p-2 rounded border border-gray-100 font-mono overflow-auto">
                                            {log.metadata_json}
                                        </div>
                                    )}
                                </div>
                            </div>
                        </li>
                    ))}
                    {logs.length === 0 && (
                        <li className="p-8 text-center text-gray-500">No audit logs found.</li>
                    )}
                </ul>
            </div>
        </div>
    );
};

export default AuditLogs;
