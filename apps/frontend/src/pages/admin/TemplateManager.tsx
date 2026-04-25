import React, { useEffect, useState } from 'react';
import { FiPlus, FiEdit2, FiCheckCircle, FiTrash2 } from 'react-icons/fi';
import apiService from '../../services/api';

const TemplateManager: React.FC = () => {
    const [templates, setTemplates] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingTemplate, setEditingTemplate] = useState<any>(null);
    const [formData, setFormData] = useState({
        name: '',
        version: '1.0.0',
        schema_json: '{\n  "Warm-up": "5 minutes",\n  "Main Content": "30 minutes",\n  "Closure": "10 minutes"\n}',
        is_active: 0
    });

    useEffect(() => {
        fetchTemplates();
    }, []);

    const fetchTemplates = async () => {
        setIsLoading(true);
        const response = await apiService.listTemplates();
        if (response.data) {
            setTemplates(response.data);
        }
        setIsLoading(false);
    };

    const handleSave = async (e: React.FormEvent) => {
        e.preventDefault();

        const response = editingTemplate
            ? await apiService.updateTemplate(editingTemplate.template_id, formData)
            : await apiService.createTemplate(formData);

        if (!response.error) {
            setIsModalOpen(false);
            setEditingTemplate(null);
            fetchTemplates();
        } else {
            alert(`Failed to save template: ${response.error}`);
        }
    };

    const handleDelete = async (id: number) => {
        if (!window.confirm('Are you sure you want to delete this template?')) return;
        const response = await apiService.deleteTemplate(id);
        if (!response.error) {
            fetchTemplates();
        } else {
            alert(`Failed to delete template: ${response.error}`);
        }
    };

    const openEdit = (tpl: any) => {
        setEditingTemplate(tpl);
        setFormData({
            name: tpl.name,
            version: tpl.version,
            schema_json: tpl.schema_json,
            is_active: tpl.is_active
        });
        setIsModalOpen(true);
    };

    const openCreate = () => {
        setEditingTemplate(null);
        setFormData({
            name: '',
            version: '1.0.0',
            schema_json: '{\n  "warm_up": "5 mins",\n  "activities": ["intro", "main", "outro"]\n}',
            is_active: 0
        });
        setIsModalOpen(true);
    };

    if (isLoading) return <div className="animate-pulse">Loading templates...</div>;

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-2xl font-bold text-gray-900">Lesson Templates</h2>
                    <p className="text-gray-500">Configure AI generation structures and schemas.</p>
                </div>
                <button
                    onClick={openCreate}
                    className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                >
                    <FiPlus className="mr-2" /> New Template
                </button>
            </div>

            {isModalOpen && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
                        <h3 className="text-xl font-bold mb-4">{editingTemplate ? 'Edit Template' : 'Create Template'}</h3>
                        <form onSubmit={handleSave} className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Name</label>
                                    <input
                                        type="text" required
                                        value={formData.name}
                                        onChange={e => setFormData({ ...formData, name: e.target.value })}
                                        className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Version</label>
                                    <input
                                        type="text" required
                                        value={formData.version}
                                        onChange={e => setFormData({ ...formData, version: e.target.value })}
                                        className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
                                    />
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Schema JSON (Prompt Rules)</label>
                                <textarea
                                    rows={10} required
                                    value={formData.schema_json}
                                    onChange={e => setFormData({ ...formData, schema_json: e.target.value })}
                                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 font-mono text-sm"
                                    placeholder='{"rules": ["Follow 5E model"]}'
                                />
                            </div>
                            <div className="flex items-center">
                                <input
                                    type="checkbox"
                                    id="is_active"
                                    checked={formData.is_active === 1}
                                    onChange={e => setFormData({ ...formData, is_active: e.target.checked ? 1 : 0 })}
                                    className="h-4 w-4 text-indigo-600 border-gray-300 rounded"
                                />
                                <label htmlFor="is_active" className="ml-2 block text-sm text-gray-900">
                                    Set as Active Template (Deactivates others)
                                </label>
                            </div>
                            <div className="flex justify-end space-x-3 mt-6">
                                <button
                                    type="button"
                                    onClick={() => setIsModalOpen(false)}
                                    className="px-4 py-2 text-gray-700 hover:text-gray-900"
                                >Cancel</button>
                                <button
                                    type="submit"
                                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                                >Save Template</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            <div className="bg-white shadow rounded-lg border border-gray-200 overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Template Name</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Version</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Updated</th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {templates.map((tpl) => (
                            <tr key={tpl.template_id}>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <span className="text-sm font-medium text-gray-900">{tpl.name}</span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    {tpl.version}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    {tpl.is_active ? (
                                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                                            <FiCheckCircle className="mr-1 mt-1" /> Active
                                        </span>
                                    ) : (
                                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">
                                            Draft
                                        </span>
                                    )}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    {new Date(tpl.updated_at).toLocaleDateString()}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                    <div className="flex justify-end space-x-3">
                                        <button
                                            onClick={() => openEdit(tpl)}
                                            className="text-indigo-600 hover:text-indigo-900"
                                        ><FiEdit2 size={18} /></button>
                                        <button
                                            onClick={() => handleDelete(tpl.template_id)}
                                            className="text-gray-400 hover:text-red-600"
                                        ><FiTrash2 size={18} /></button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default TemplateManager;
