import React, { useEffect, useState } from 'react';
import {
    FiUsers,
    FiFileText,
    FiAlertTriangle,
    FiActivity,
    FiArrowUpRight
} from 'react-icons/fi';

const AdminDashboard: React.FC = () => {
    const [metrics, setMetrics] = useState<any>(null);
    const [activities, setActivities] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
const [metricsRes, logsRes] = await Promise.all([
                    fetch(`${(import.meta as any).env.VITE_API_URL}/admin/metrics`, { credentials: 'include' }),
                    fetch(`${(import.meta as any).env.VITE_API_URL}/admin/audit-logs?limit=5`, { credentials: 'include' })
                ]);

                const metricsData = await metricsRes.json();
                const logsData = await logsRes.json();

                setMetrics(metricsData);
                setActivities(logsData);
            } catch (error) {
                console.error('Failed to fetch dashboard data:', error);
            } finally {
                setIsLoading(false);
            }
        };

        fetchData();
    }, []);

    if (isLoading) return <div className="animate-pulse flex items-center justify-center min-h-[400px]">Loading dashboard...</div>;

    const stats = [
        { name: 'Total Users', value: metrics?.total_users ?? 0, change: `+${metrics?.new_users_7d ?? 0}`, changeType: 'increase', icon: FiUsers },
        { name: 'Lessons Generated', value: metrics?.total_lessons ?? 0, change: `+${metrics?.lessons_7d ?? 0}`, changeType: 'increase', icon: FiFileText },
        { name: 'Flagged Content', value: metrics?.flagged_resources ?? 0, change: '0', changeType: 'stable', icon: FiAlertTriangle },
        { name: 'System Status', value: 'Healthy', change: '100%', changeType: 'increase', icon: FiActivity },
    ];

    return (
        <div className="space-y-8">
            <div>
                <h2 className="text-2xl font-bold text-gray-900">Admin Overview</h2>
                <p className="text-gray-500">Real-time platform performance and safety metrics.</p>
            </div>

            <dl className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
                {stats.map((item) => (
                    <div key={item.name} className="relative bg-white pt-5 px-4 pb-12 sm:pt-6 sm:px-6 shadow rounded-lg overflow-hidden border border-gray-100">
                        <dt>
                            <div className="absolute bg-indigo-500 rounded-md p-3">
                                <item.icon className="h-6 w-6 text-white" aria-hidden="true" />
                            </div>
                            <p className="ml-16 text-sm font-medium text-gray-500 truncate">{item.name}</p>
                        </dt>
                        <dd className="ml-16 flex items-baseline sm:pb-1">
                            <p className="text-2xl font-semibold text-gray-900">{item.value}</p>
                            <p className={`ml-2 flex items-baseline text-sm font-semibold ${item.changeType === 'increase' ? 'text-green-600' : 'text-gray-500'
                                }`}>
                                {item.changeType === 'increase' ? (
                                    <FiArrowUpRight className="self-center flex-shrink-0 h-4 w-4 text-green-500" aria-hidden="true" />
                                ) : (
                                    <FiActivity className="self-center flex-shrink-0 h-4 w-4 text-gray-400" aria-hidden="true" />
                                )}
                                <span className="sr-only"> {item.changeType === 'increase' ? 'Increased' : 'Stable'} by </span>
                                {item.change}
                            </p>
                        </dd>
                    </div>
                ))}
            </dl>

            <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
                <div className="bg-white shadow rounded-lg p-6 border border-gray-100">
                    <h3 className="text-lg font-medium leading-6 text-gray-900 mb-4">Recent Activity</h3>
                    <div className="flow-root">
                        <ul className="-mb-8">
                            {activities.map((activity, idx) => (
                                <li key={activity.log_id}>
                                    <div className="relative pb-8">
                                        {idx !== activities.length - 1 && (
                                            <span className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200" aria-hidden="true" />
                                        )}
                                        <div className="relative flex space-x-3">
                                            <div>
                                                <span className="h-8 w-8 rounded-full bg-gray-100 flex items-center justify-center ring-8 ring-white">
                                                    <FiActivity className="h-4 w-4 text-gray-500" />
                                                </span>
                                            </div>
                                            <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                                                <div>
                                                    <p className="text-sm text-gray-500">
                                                        {activity.action} by <span className="font-medium text-gray-900">{activity.actor_name}</span>
                                                    </p>
                                                </div>
                                                <div className="whitespace-nowrap text-right text-sm text-gray-500">
                                                    {new Date(activity.created_at).toLocaleDateString()}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </li>
                            ))}
                            {activities.length === 0 && <p className="text-gray-400 text-sm">No recent activity.</p>}
                        </ul>
                    </div>
                </div>

                <div className="bg-white shadow rounded-lg p-6 border border-gray-100">
                    <h3 className="text-lg font-medium leading-6 text-gray-900 mb-4">System Alerts</h3>
                    <div className="flex items-center justify-center h-40 border-2 border-dashed border-gray-200 rounded-lg">
                        <p className="text-gray-400">No active alerts.</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AdminDashboard;
