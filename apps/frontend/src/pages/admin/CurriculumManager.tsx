import React, { useEffect, useState } from 'react';
import { FiPlus, FiEdit2, FiTrash2, FiMapPin, FiLayers, FiBook, FiArrowLeft } from 'react-icons/fi';
import apiService from '../../services/api';
import Modal from '../../components/Modal';

const CurriculumManager: React.FC = () => {
    const [countries, setCountries] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingCountry, setEditingCountry] = useState<any>(null);
    const [formData, setFormData] = useState({
        country_name: '',
        iso_code: '',
        region: ''
    });
    // Modals
    const [isStructureModalOpen, setIsStructureModalOpen] = useState(false);
    const [isTopicModalOpen, setIsTopicModalOpen] = useState(false);
    const [structureFormData, setStructureFormData] = useState({ grade_level_id: 0, subject_id: 0 });
    const [topicFormData, setTopicFormData] = useState({ topic_title: '' });
    const [selectedCountry, setSelectedCountry] = useState<any>(null);
    const [curricula, setCurricula] = useState<any[]>([]);
    const [isLoadingCurricula, setIsLoadingCurricula] = useState(false);

    // Deep drill-down states
    const [selectedCurriculum, setSelectedCurriculum] = useState<any>(null);
    const [structures, setStructures] = useState<any[]>([]);
    const [isLoadingStructures, setIsLoadingStructures] = useState(false);

    const [selectedStructure, setSelectedStructure] = useState<any>(null);
    const [topics, setTopics] = useState<any[]>([]);
    const [isLoadingTopics, setIsLoadingTopics] = useState(false);

    const [selectedTopic, setSelectedTopic] = useState<any>(null);
    const [objectives, setObjectives] = useState<any[]>([]);
    const [contents, setContents] = useState<any[]>([]);
    const [isLoadingDetails, setIsLoadingDetails] = useState(false);

    // Generic Modals State
    const [inputModal, setInputModal] = useState<{
        isOpen: boolean;
        title: string;
        label: string;
        initialValue?: string;
        onConfirm: (val: string) => void;
    }>({ isOpen: false, title: '', label: '', onConfirm: () => { } });

    const [confirmModal, setConfirmModal] = useState<{
        isOpen: boolean;
        title: string;
        message: string;
        onConfirm: () => void;
    }>({ isOpen: false, title: '', message: '', onConfirm: () => { } });

    // Support data
    const [gradeLevels, setGradeLevels] = useState<any[]>([]);
    const [subjects, setSubjects] = useState<any[]>([]);

    useEffect(() => {
        fetchCountries();
        fetchSupportData();
    }, []);

    const fetchSupportData = async () => {
        const [glRes, subRes] = await Promise.all([
            apiService.getGradeLevels(),
            apiService.getSubjects()
        ]);
        if (glRes.data) {
            const data = glRes.data;
            setGradeLevels(data);
            if (data.length > 0) setStructureFormData(prev => ({ ...prev, grade_level_id: data[0].grade_level_id }));
        }
        if (subRes.data) {
            const data = subRes.data;
            setSubjects(data);
            if (data.length > 0) setStructureFormData(prev => ({ ...prev, subject_id: data[0].subject_id }));
        }
    };

    const fetchCountries = async () => {
        setIsLoading(true);
        const response = await apiService.getCountries();
        if (response.data) {
            setCountries(response.data);
        }
        setIsLoading(false);
    };

    const fetchCurricula = async (countryId: number) => {
        setIsLoadingCurricula(true);
        const response = await apiService.getCurriculums(countryId);
        if (response.data) {
            setCurricula(response.data);
        }
        setIsLoadingCurricula(false);
    };

    const fetchStructures = async (curriculaId: number) => {
        setIsLoadingStructures(true);
        const response = await apiService.getCurriculumStructures(curriculaId);
        if (response.data) {
            setStructures(response.data);
        }
        setIsLoadingStructures(false);
    };

    const fetchTopics = async (structureId: number) => {
        setIsLoadingTopics(true);
        const response = await apiService.getTopicsByCurriculumStructure(structureId);
        if (response.data) {
            setTopics(response.data);
        }
        setIsLoadingTopics(false);
    };

    const [editingTopic, setEditingTopic] = useState<any>(null);
    const [editingStructure, setEditingStructure] = useState<any>(null);

    const fetchTopicDetails = async (topicId: number) => {
        setIsLoadingDetails(true);
        const [objRes, conRes] = await Promise.all([
            apiService.getLearningObjectives(topicId),
            apiService.getTopicContents(topicId)
        ]);
        if (objRes.data) setObjectives(objRes.data);
        if (conRes.data) setContents(conRes.data);
        setIsLoadingDetails(false);
    };

    const handleManageCountry = (country: any) => {
        setSelectedCountry(country);
        fetchCurricula(country.country_id);
    };

    const handleConfigureStructures = (curriculum: any) => {
        setSelectedCurriculum(curriculum);
        fetchStructures(curriculum.curricula_id);
    };

    const handleManageTopics = (structure: any) => {
        setSelectedStructure(structure);
        fetchTopics(structure.curriculum_structure_id);
    };

    const handleManageContent = (topic: any) => {
        setSelectedTopic(topic);
        fetchTopicDetails(topic.topic_id);
    };

    const handleAddCurriculum = () => {
        setInputModal({
            isOpen: true,
            title: 'Add Curriculum',
            label: 'Curriculum Name',
            initialValue: '',
            onConfirm: async (title) => {
                if (!title) return;
                const response = await apiService.createCurriculum({
                    curriculum_title: title,
                    country_id: selectedCountry.country_id
                });
                if (!response.error) {
                    fetchCurricula(selectedCountry.country_id);
                } else {
                    alert(`Failed to add curriculum: ${response.error}`);
                }
                setInputModal(prev => ({ ...prev, isOpen: false }));
            }
        });
    };

    const handleEditCurriculum = (curriculum: any) => {
        setInputModal({
            isOpen: true,
            title: 'Edit Curriculum',
            label: 'Curriculum Name',
            initialValue: curriculum.curriculum_title,
            onConfirm: async (title) => {
                if (!title || title === curriculum.curriculum_title) {
                    setInputModal(prev => ({ ...prev, isOpen: false }));
                    return;
                }
                const response = await apiService.updateCurriculum(curriculum.curricula_id, {
                    curriculum_title: title
                });
                if (!response.error) {
                    fetchCurricula(selectedCountry.country_id);
                } else {
                    alert(`Failed to update curriculum: ${response.error}`);
                }
                setInputModal(prev => ({ ...prev, isOpen: false }));
            }
        });
    };

    const handleDeleteCurriculum = (id: number) => {
        setConfirmModal({
            isOpen: true,
            title: 'Delete Curriculum',
            message: 'Are you sure you want to delete this curriculum and all its structures?',
            onConfirm: async () => {
                const response = await apiService.deleteCurriculum(id);
                if (!response.error) {
                    fetchCurricula(selectedCountry.country_id);
                } else {
                    alert(`Failed to delete curriculum: ${response.error}`);
                }
                setConfirmModal(prev => ({ ...prev, isOpen: false }));
            }
        });
    };

    const handleSaveStructure = async (e: React.FormEvent) => {
        e.preventDefault();
        let response;

        if (editingStructure) {
            response = await apiService.updateCurriculumStructure(editingStructure.curriculum_structure_id, {
                curricula_id: selectedCurriculum.curricula_id,
                grade_level_id: structureFormData.grade_level_id,
                subject_id: structureFormData.subject_id
            });
        } else {
            response = await apiService.createCurriculumStructure({
                curricula_id: selectedCurriculum.curricula_id,
                grade_level_id: structureFormData.grade_level_id,
                subject_id: structureFormData.subject_id
            });
        }

        if (!response.error) {
            setIsStructureModalOpen(false);
            setEditingStructure(null);
            fetchStructures(selectedCurriculum.curricula_id);
        } else {
            alert(`Failed to ${editingStructure ? 'update' : 'add'} structure: ${response.error}`);
        }
    };

    const handleEditStructure = (str: any) => {
        setEditingStructure(str);
        setStructureFormData({
            grade_level_id: str.grade_level_id,
            subject_id: str.subject_id
        });
        setIsStructureModalOpen(true);
    };

    const handleSaveTopic = async (e: React.FormEvent) => {
        e.preventDefault();
        let response;

        if (editingTopic) {
            response = await apiService.updateTopic(editingTopic.topic_id, {
                topic_title: topicFormData.topic_title
            });
        } else {
            response = await apiService.createTopic({
                topic_title: topicFormData.topic_title,
                curriculum_structure_id: selectedStructure.curriculum_structure_id
            });
        }

        if (!response.error) {
            setIsTopicModalOpen(false);
            setEditingTopic(null);
            setTopicFormData({ topic_title: '' });
            fetchTopics(selectedStructure.curriculum_structure_id);
        } else {
            alert(`Failed to ${editingTopic ? 'update' : 'add'} topic: ${response.error}`);
        }
    };

    const handleEditTopic = (topic: any) => {
        setEditingTopic(topic);
        setTopicFormData({ topic_title: topic.topic_title });
        setIsTopicModalOpen(true);
    };

    const handleDeleteTopic = (id: number) => {
        setConfirmModal({
            isOpen: true,
            title: 'Delete Topic',
            message: 'Are you sure you want to delete this topic and all its content?',
            onConfirm: async () => {
                const response = await apiService.deleteTopic(id);
                if (!response.error) {
                    fetchTopics(selectedStructure.curriculum_structure_id);
                } else {
                    alert(`Failed to delete topic: ${response.error}`);
                }
                setConfirmModal(prev => ({ ...prev, isOpen: false }));
            }
        });
    };

    const handleAddObjective = () => {
        setInputModal({
            isOpen: true,
            title: 'Add Learning Objective',
            label: 'Objective Description',
            initialValue: '',
            onConfirm: async (text) => {
                if (!text) return;
                const response = await apiService.createLearningObjective({
                    topic_id: selectedTopic.topic_id,
                    objective: text
                });
                if (!response.error) fetchTopicDetails(selectedTopic.topic_id);
                setInputModal(prev => ({ ...prev, isOpen: false }));
            }
        });
    };

    const handleEditObjective = (obj: any) => {
        setInputModal({
            isOpen: true,
            title: 'Edit Learning Objective',
            label: 'Objective Description',
            initialValue: obj.objective,
            onConfirm: async (text) => {
                if (!text || text === obj.objective) {
                    setInputModal(prev => ({ ...prev, isOpen: false }));
                    return;
                }
                const response = await apiService.updateLearningObjective(obj.learning_objective_id, text);
                if (!response.error) fetchTopicDetails(selectedTopic.topic_id);
                setInputModal(prev => ({ ...prev, isOpen: false }));
            }
        });
    };

    const handleAddContent = () => {
        setInputModal({
            isOpen: true,
            title: 'Add Content Area',
            label: 'Content Summary',
            initialValue: '',
            onConfirm: async (text) => {
                if (!text) return;
                const response = await apiService.createTopicContent({
                    topic_id: selectedTopic.topic_id,
                    content_area: text
                });
                if (!response.error) fetchTopicDetails(selectedTopic.topic_id);
                setInputModal(prev => ({ ...prev, isOpen: false }));
            }
        });
    };

    const handleEditContent = (con: any) => {
        setInputModal({
            isOpen: true,
            title: 'Edit Content Area',
            label: 'Content Summary',
            initialValue: con.content_area,
            onConfirm: async (text) => {
                if (!text || text === con.content_area) {
                    setInputModal(prev => ({ ...prev, isOpen: false }));
                    return;
                }
                const response = await apiService.updateTopicContent(con.topic_contents_id, text);
                if (!response.error) fetchTopicDetails(selectedTopic.topic_id);
                setInputModal(prev => ({ ...prev, isOpen: false }));
            }
        });
    };

    const handleSaveCountry = async (e: React.FormEvent) => {
        e.preventDefault();

        const response = editingCountry
            ? await apiService.updateCountry(editingCountry.country_id, formData)
            : await apiService.createCountry(formData);

        if (!response.error) {
            setIsModalOpen(false);
            setEditingCountry(null);
            fetchCountries();
        } else {
            alert(`Failed to save country: ${response.error}`);
        }
    };

    const handleDeleteCountry = (id: number) => {
        setConfirmModal({
            isOpen: true,
            title: 'Delete Country',
            message: 'Are you sure you want to delete this country and all its curricula?',
            onConfirm: async () => {
                const response = await apiService.deleteCountry(id);
                if (!response.error) {
                    fetchCountries();
                } else {
                    alert(`Failed to delete country: ${response.error}`);
                }
                setConfirmModal(prev => ({ ...prev, isOpen: false }));
            }
        });
    };

    const openEditCountry = (country: any) => {
        setEditingCountry(country);
        setFormData({
            country_name: country.country_name,
            iso_code: country.iso_code || '',
            region: country.region || ''
        });
        setIsModalOpen(true);
    };

    const openCreateCountry = () => {
        setEditingCountry(null);
        setFormData({ country_name: '', iso_code: '', region: '' });
        setIsModalOpen(true);
    };

    if (isLoading) return <div className="p-8 text-center text-gray-500">Loading curriculum data...</div>;

    // View: Topic Details (Objectives & Content)
    if (selectedTopic) {
        return (
            <div className="space-y-6">
                <div className="flex items-center space-x-4">
                    <button onClick={() => setSelectedTopic(null)} className="p-2 hover:bg-gray-100 rounded-full transition-colors text-gray-400">
                        <FiArrowLeft size={20} />
                    </button>
                    <div>
                        <h2 className="text-2xl font-bold text-gray-900">{selectedTopic.topic_title}</h2>
                        <div className="flex items-center text-sm text-gray-500 mt-1">
                            <span>ID: {selectedTopic.topic_id}</span>
                            <span className="mx-2">•</span>
                            <span>{selectedCurriculum?.curriculum_title}</span>
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Objectives Section */}
                    <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex flex-col h-[600px]">
                        <div className="flex justify-between items-center mb-6">
                            <h3 className="font-bold text-lg text-gray-900">Learning Objectives</h3>
                            <button onClick={handleAddObjective} className="inline-flex items-center px-3 py-1.5 bg-indigo-50 text-indigo-700 text-sm font-semibold rounded-lg hover:bg-indigo-100 transition-colors">
                                <FiPlus className="mr-1.5" /> Add Objective
                            </button>
                        </div>
                        <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
                            {isLoadingDetails ? <div className="text-gray-400 text-sm italic">Loading objectives...</div> : (
                                <ul className="space-y-3">
                                    {objectives.map(obj => (
                                        <li key={obj.learning_objective_id} className="p-4 bg-gray-50 rounded-xl text-sm text-gray-700 border border-gray-100 group flex items-start justify-between hover:bg-white hover:border-indigo-200 transition-all">
                                            <span className="leading-relaxed">{obj.objective}</span>
                                            <div className="flex space-x-1 ml-4 mt-0.5">
                                                <button
                                                    onClick={() => handleEditObjective(obj)}
                                                    className="text-gray-300 hover:text-indigo-500 opacity-0 group-hover:opacity-100 transition-opacity"
                                                ><FiEdit2 size={16} /></button>
                                                <button
                                                    onClick={() => {
                                                        setConfirmModal({
                                                            isOpen: true,
                                                            title: 'Delete Objective',
                                                            message: 'Are you sure you want to delete this objective?',
                                                            onConfirm: async () => {
                                                                await apiService.deleteLearningObjective(obj.learning_objective_id);
                                                                fetchTopicDetails(selectedTopic.topic_id);
                                                                setConfirmModal(prev => ({ ...prev, isOpen: false }));
                                                            }
                                                        });
                                                    }}
                                                    className="text-gray-300 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                                                ><FiTrash2 size={16} /></button>
                                            </div>
                                        </li>
                                    ))}
                                    {objectives.length === 0 && (
                                        <div className="text-center py-8 text-gray-400 text-sm">No objectives added yet.</div>
                                    )}
                                </ul>
                            )}
                        </div>
                    </div>

                    {/* Content Section */}
                    <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex flex-col h-[600px]">
                        <div className="flex justify-between items-center mb-6">
                            <h3 className="font-bold text-lg text-gray-900">Topic Content Areas</h3>
                            <button onClick={handleAddContent} className="inline-flex items-center px-3 py-1.5 bg-indigo-50 text-indigo-700 text-sm font-semibold rounded-lg hover:bg-indigo-100 transition-colors">
                                <FiPlus className="mr-1.5" /> Add Content
                            </button>
                        </div>
                        <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
                            {isLoadingDetails ? <div className="text-gray-400 text-sm italic">Loading content...</div> : (
                                <ul className="space-y-3">
                                    {contents.map(con => (
                                        <li key={con.topic_contents_id} className="p-4 bg-gray-50 rounded-xl text-sm text-gray-700 border border-gray-100 group flex items-start justify-between hover:bg-white hover:border-indigo-200 transition-all">
                                            <span className="leading-relaxed font-medium">{con.content_area}</span>
                                            <div className="flex space-x-1 ml-4 mt-0.5">
                                                <button
                                                    onClick={() => handleEditContent(con)}
                                                    className="text-gray-300 hover:text-indigo-500 opacity-0 group-hover:opacity-100 transition-opacity"
                                                ><FiEdit2 size={16} /></button>
                                                <button
                                                    onClick={() => {
                                                        setConfirmModal({
                                                            isOpen: true,
                                                            title: 'Delete Content',
                                                            message: 'Are you sure you want to delete this content?',
                                                            onConfirm: async () => {
                                                                await apiService.deleteTopicContent(con.topic_contents_id);
                                                                fetchTopicDetails(selectedTopic.topic_id);
                                                                setConfirmModal(prev => ({ ...prev, isOpen: false }));
                                                            }
                                                        });
                                                    }}
                                                    className="text-gray-300 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                                                ><FiTrash2 size={16} /></button>
                                            </div>
                                        </li>
                                    ))}
                                    {contents.length === 0 && (
                                        <div className="text-center py-8 text-gray-400 text-sm">No content entries added yet.</div>
                                    )}
                                </ul>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    // View: Topics List
    if (selectedStructure) {
        const grade = gradeLevels.find(g => g.grade_level_id === selectedStructure.grade_level_id)?.name || 'Unknown Grade';
        const subject = subjects.find(s => s.subject_id === selectedStructure.subject_id)?.name || 'Unknown Subject';

        return (
            <div className="space-y-6">
                <div className="flex items-center space-x-4">
                    <button onClick={() => setSelectedStructure(null)} className="p-2 hover:bg-gray-100 rounded-full transition-colors text-gray-400">
                        <FiArrowLeft size={20} />
                    </button>
                    <div>
                        <h2 className="text-2xl font-bold text-gray-900">{subject}</h2>
                        <p className="text-gray-500 font-medium">{grade}</p>
                    </div>
                </div>

                <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex justify-between items-center">
                    <span className="text-sm text-gray-600 font-medium bg-gray-50 px-3 py-1 rounded-full border border-gray-100">{topics.length} Topics defined</span>
                    <button onClick={() => setIsTopicModalOpen(true)} className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-all shadow-sm font-semibold">
                        <FiPlus className="mr-2" /> New Topic
                    </button>
                </div>

                {isLoadingTopics ? (
                    <div className="text-center py-12">Loading topics...</div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {topics.map((topic) => (
                            <div key={topic.topic_id} className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md hover:border-indigo-300 transition-all group">
                                <div className="flex justify-between items-start mb-6">
                                    <h3 className="text-lg font-bold text-gray-900 line-clamp-2">{topic.topic_title}</h3>
                                    <div className="flex space-x-1 ml-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                        <button onClick={() => handleEditTopic(topic)} className="p-1 text-gray-400 hover:text-indigo-600"><FiEdit2 size={16} /></button>
                                        <button onClick={() => handleDeleteTopic(topic.topic_id)} className="p-1 text-gray-400 hover:text-red-600"><FiTrash2 size={16} /></button>
                                    </div>
                                </div>
                                <div className="flex justify-between items-center pt-4 border-t border-gray-50">
                                    <span className="text-xs font-mono text-gray-400">#{topic.topic_id}</span>
                                    <button
                                        onClick={() => handleManageContent(topic)}
                                        className="text-sm font-bold text-indigo-600 hover:text-indigo-800 flex items-center group-hover:translate-x-1 transition-transform"
                                    >Objectives & Content <FiArrowLeft className="ml-1 rotate-180" /></button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {isTopicModalOpen && (
                    <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4 z-50">
                        <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8 border border-white/20">
                            <h3 className="text-2xl font-bold text-gray-900 mb-6">Add New Topic</h3>
                            <form onSubmit={handleSaveTopic} className="space-y-6">
                                <div>
                                    <label className="block text-sm font-semibold text-gray-700 mb-2">Topic Title</label>
                                    <textarea
                                        required rows={3}
                                        value={topicFormData.topic_title}
                                        onChange={e => setTopicFormData({ topic_title: e.target.value })}
                                        className="w-full border border-gray-200 rounded-xl p-4 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all shadow-inner bg-gray-50"
                                        placeholder="Enter the main topic title..."
                                    />
                                </div>
                                <div className="flex justify-end space-x-3 pt-4">
                                    <button
                                        type="button" onClick={() => setIsTopicModalOpen(false)}
                                        className="px-5 py-2.5 text-gray-500 font-semibold hover:bg-gray-100 rounded-xl transition-colors"
                                    >Cancel</button>
                                    <button
                                        type="submit"
                                        className="px-6 py-2.5 bg-indigo-600 text-white font-bold rounded-xl hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-200"
                                    >Create Topic</button>
                                </div>
                            </form>
                        </div>
                    </div>
                )}
            </div>
        );
    }

    // View: Structures List (Grades + Subjects)
    if (selectedCurriculum) {
        return (
            <div className="space-y-6">
                <div className="flex items-center space-x-4">
                    <button onClick={() => setSelectedCurriculum(null)} className="p-2 hover:bg-gray-100 rounded-full transition-colors text-gray-400">
                        <FiArrowLeft size={20} />
                    </button>
                    <div>
                        <h2 className="text-2xl font-bold text-gray-900">{selectedCurriculum.curriculum_title}</h2>
                        <p className="text-gray-500 font-medium">Curriculum Structure Configuration</p>
                    </div>
                </div>

                <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex justify-between items-center">
                    <span className="text-sm font-bold text-gray-600 px-3 py-1 bg-indigo-50 rounded-full border border-indigo-100">{structures.length} Active Structures</span>
                    <button onClick={() => {
                        setEditingStructure(null);
                        setStructureFormData({ grade_level_id: 0, subject_id: 0 });
                        setIsStructureModalOpen(true);
                    }} className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-all font-semibold shadow-sm">
                        <FiPlus className="mr-2" /> Add Subject/Grade
                    </button>
                </div>

                {isLoadingStructures ? (
                    <div className="text-center py-12 text-gray-400 italic animate-pulse">Fetching structure mappings...</div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {structures.map((str) => {
                            const grade = gradeLevels.find(g => g.grade_level_id === str.grade_level_id)?.name || 'Unknown Grade';
                            const subject = subjects.find(s => s.subject_id === str.subject_id)?.name || 'Unknown Subject';
                            return (
                                <div key={str.curriculum_structure_id} className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm hover:border-indigo-400 transition-all group">
                                    <div className="flex items-center bg-indigo-50 text-indigo-700 text-xs font-bold uppercase tracking-wider px-2 py-1 rounded w-fit mb-3">
                                        <FiLayers className="mr-2" /> {grade}
                                    </div>
                                    <div className="text-xl font-bold text-gray-900 mb-6 group-hover:text-indigo-600 transition-colors">{subject}</div>
                                    <div className="flex justify-between items-center border-t pt-4 border-gray-50">
                                        <div className="flex space-x-1">
                                            <button
                                                onClick={() => handleEditStructure(str)}
                                                className="p-2 text-gray-300 hover:text-indigo-600 rounded-lg hover:bg-indigo-50 transition-colors"
                                            ><FiEdit2 size={18} /></button>
                                            <button
                                                onClick={() => {
                                                    setConfirmModal({
                                                        isOpen: true,
                                                        title: 'Delete Structure',
                                                        message: 'WARNING: This will delete all topics under this structure. Proceed?',
                                                        onConfirm: async () => {
                                                            const res = await apiService.deleteCurriculumStructure(str.curriculum_structure_id);
                                                            if (res.error) alert(res.error);
                                                            fetchStructures(selectedCurriculum.curricula_id);
                                                            setConfirmModal(prev => ({ ...prev, isOpen: false }));
                                                        }
                                                    });
                                                }}
                                                className="p-2 text-gray-300 hover:text-red-600 rounded-lg hover:bg-red-50 transition-colors"
                                            ><FiTrash2 size={18} /></button>
                                        </div>
                                        <button
                                            onClick={() => handleManageTopics(str)}
                                            className="text-sm font-bold text-indigo-600 bg-indigo-50 px-4 py-2 rounded-xl group-hover:bg-indigo-600 group-hover:text-white transition-all shadow-sm"
                                        >Manage Topics</button>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}

                {isStructureModalOpen && (
                    <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4 z-50">
                        <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full p-8">
                            <h3 className="text-2xl font-bold text-gray-900 mb-6">{editingStructure ? 'Edit Mapping' : 'Define New Mapping'}</h3>
                            <form onSubmit={handleSaveStructure} className="space-y-6">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div>
                                        <label className="block text-sm font-semibold text-gray-700 mb-2">Grade Level</label>
                                        <div className="flex gap-2">
                                            <select
                                                className="w-full border-gray-200 rounded-xl p-3 bg-gray-50 focus:ring-2 focus:ring-indigo-500"
                                                value={structureFormData.grade_level_id}
                                                onChange={e => setStructureFormData({ ...structureFormData, grade_level_id: parseInt(e.target.value) })}
                                            >
                                                <option value={0} disabled>Select Grade...</option>
                                                {gradeLevels.map(gl => (
                                                    <option key={gl.grade_level_id} value={gl.grade_level_id}>{gl.name}</option>
                                                ))}
                                            </select>
                                            <button
                                                type="button"
                                                onClick={() => {
                                                    setInputModal({
                                                        isOpen: true,
                                                        title: 'New Grade Level',
                                                        label: 'Grade Name',
                                                        onConfirm: async (name) => {
                                                            if (name) {
                                                                const res = await apiService.createGradeLevel({ name, level_code: name.toUpperCase().replace(/\s+/g, '_') });
                                                                if (res.data) {
                                                                    setGradeLevels(prev => [...prev, res.data]);
                                                                    setStructureFormData(prev => ({ ...prev, grade_level_id: res.data.grade_level_id }));
                                                                } else {
                                                                    alert("Failed to create grade level: " + res.error);
                                                                }
                                                                setInputModal(prev => ({ ...prev, isOpen: false }));
                                                            }
                                                        }
                                                    });
                                                }}
                                                className="px-3 py-2 bg-gray-100 hover:bg-gray-200 text-gray-600 rounded-lg text-sm font-medium transition-colors whitespace-nowrap"
                                            >
                                                + New
                                            </button>
                                        </div>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-semibold text-gray-700 mb-2">Subject</label>
                                        <div className="flex gap-2">
                                            <select
                                                className="w-full border-gray-200 rounded-xl p-3 bg-gray-50 focus:ring-2 focus:ring-indigo-500"
                                                value={structureFormData.subject_id}
                                                onChange={e => setStructureFormData({ ...structureFormData, subject_id: parseInt(e.target.value) })}
                                            >
                                                <option value={0} disabled>Select Subject...</option>
                                                {subjects.map(s => (
                                                    <option key={s.subject_id} value={s.subject_id}>{s.name}</option>
                                                ))}
                                            </select>
                                            <button
                                                type="button"
                                                onClick={() => {
                                                    setInputModal({
                                                        isOpen: true,
                                                        title: 'New Subject',
                                                        label: 'Subject Name',
                                                        onConfirm: async (name) => {
                                                            if (name) {
                                                                const res = await apiService.createSubject({ name });
                                                                if (res.data) {
                                                                    setSubjects(prev => [...prev, res.data]);
                                                                    setStructureFormData(prev => ({ ...prev, subject_id: res.data.subject_id }));
                                                                    fetchSupportData();
                                                                } else {
                                                                    alert("Failed to create subject: " + (res.error || 'Unknown error'));
                                                                }
                                                                setInputModal(prev => ({ ...prev, isOpen: false }));
                                                            }
                                                        }
                                                    });
                                                }}
                                                className="px-3 py-2 bg-gray-100 hover:bg-gray-200 text-gray-600 rounded-lg text-sm font-medium transition-colors whitespace-nowrap"
                                            >
                                                + New
                                            </button>
                                        </div>
                                    </div>
                                </div>
                                <div className="flex justify-end space-x-3 pt-6 border-t border-gray-100 mt-4">
                                    <button
                                        type="button" onClick={() => setIsStructureModalOpen(false)}
                                        className="px-5 py-2.5 text-gray-500 font-semibold rounded-xl hover:bg-gray-100"
                                    >Cancel</button>
                                    <button
                                        type="submit"
                                        className="px-8 py-2.5 bg-indigo-600 text-white font-bold rounded-xl hover:bg-indigo-700 shadow-lg shadow-indigo-100 disabled:opacity-50"
                                        disabled={!structureFormData.grade_level_id || !structureFormData.subject_id}
                                    >{editingStructure ? 'Update Structure' : 'Create Structure'}</button>
                                </div>
                            </form>
                        </div>
                    </div>
                )}
            </div>
        );
    }

    if (selectedCountry) {
        return (
            <div className="space-y-6">
                <div className="flex items-center space-x-4">
                    <button
                        onClick={() => setSelectedCountry(null)}
                        className="p-2 hover:bg-gray-100 rounded-full transition-colors text-gray-400"
                    >
                        <FiArrowLeft size={20} />
                    </button>
                    <div>
                        <h2 className="text-2xl font-bold text-gray-900">{selectedCountry.country_name} Curricula</h2>
                        <p className="text-gray-500 font-medium">Manage specific educational systems for {selectedCountry.country_name}.</p>
                    </div>
                </div>

                <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex justify-between items-center">
                    <span className="text-sm font-bold text-gray-600 px-3 py-1 bg-indigo-50 rounded-full border border-indigo-100">{curricula.length} Curricula defined</span>
                    <button
                        onClick={handleAddCurriculum}
                        className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-all font-semibold shadow-sm"
                    >
                        <FiPlus className="mr-2" /> Add Curriculum
                    </button>
                </div>

                {isLoadingCurricula ? (
                    <div className="text-center py-12 text-gray-400 animate-pulse">Loading curricula...</div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {curricula.map((cur) => (
                            <div key={cur.curricula_id} className="bg-white p-8 rounded-2xl border border-gray-100 shadow-sm hover:border-indigo-400 transition-all hover:shadow-md group">
                                <div className="flex justify-between items-start mb-6">
                                    <h3 className="text-xl font-bold text-gray-900 group-hover:text-indigo-600 transition-colors">{cur.curriculum_title}</h3>
                                    <div className="flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                        <button onClick={() => handleEditCurriculum(cur)} className="p-1 text-gray-400 hover:text-indigo-600"><FiEdit2 size={18} /></button>
                                        <button onClick={() => handleDeleteCurriculum(cur.curricula_id)} className="p-1 text-gray-400 hover:text-red-600"><FiTrash2 size={18} /></button>
                                    </div>
                                </div>
                                <div className="flex justify-between items-center pt-4 border-t border-gray-50">
                                    <span className="text-xs font-mono text-gray-400">ID: {cur.curricula_id}</span>
                                    <button
                                        onClick={() => handleConfigureStructures(cur)}
                                        className="text-sm font-bold text-indigo-600 bg-indigo-50 px-5 py-2.5 rounded-xl hover:bg-indigo-600 hover:text-white transition-all shadow-sm"
                                    >Configure Structures &rarr;</button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
                {curricula.length === 0 && !isLoadingCurricula && (
                    <div className="text-center py-12 bg-gray-50 rounded-2xl border-2 border-dashed border-gray-200">
                        <p className="text-gray-500 italic">No curricula defined for this country yet.</p>
                    </div>
                )}
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-2xl font-bold text-gray-900">Curriculum Manager</h2>
                    <p className="text-gray-500">Manage educational structures across countries.</p>
                </div>
                <button
                    onClick={openCreateCountry}
                    className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                >
                    <FiPlus className="mr-2" /> Add Country
                </button>
            </div>

            {/* Country Modal */}
            <Modal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                title={editingCountry ? 'Edit Country' : 'Add New Country'}
            >
                <form onSubmit={handleSaveCountry} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Country Name</label>
                        <input
                            type="text" required
                            value={formData.country_name}
                            onChange={e => setFormData({ ...formData, country_name: e.target.value })}
                            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-3 focus:ring-indigo-500 focus:border-indigo-500"
                            placeholder="e.g. Nigeria"
                        />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">ISO Code</label>
                            <input
                                type="text"
                                value={formData.iso_code}
                                onChange={e => setFormData({ ...formData, iso_code: e.target.value })}
                                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-3"
                                placeholder="e.g. NG"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Region</label>
                            <input
                                type="text"
                                value={formData.region}
                                onChange={e => setFormData({ ...formData, region: e.target.value })}
                                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-3"
                                placeholder="e.g. West Africa"
                            />
                        </div>
                    </div>
                    <div className="flex justify-end space-x-3 mt-6 pt-4 border-t border-gray-100">
                        <button
                            type="button"
                            onClick={() => setIsModalOpen(false)}
                            className="px-4 py-2 text-gray-700 hover:text-gray-900 border border-transparent hover:bg-gray-100 rounded-lg transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors shadow-sm font-medium"
                        >
                            {editingCountry ? 'Update Country' : 'Create Country'}
                        </button>
                    </div>
                </form>
            </Modal>

            {/* Input Modal */}
            <Modal
                isOpen={inputModal.isOpen}
                onClose={() => setInputModal(prev => ({ ...prev, isOpen: false }))}
                title={inputModal.title}
                maxWidth="max-w-md"
            >
                <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">{inputModal.label}</label>
                    <input
                        autoFocus
                        type="text"
                        defaultValue={inputModal.initialValue || ''}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter') {
                                inputModal.onConfirm(e.currentTarget.value);
                            }
                        }}
                        className="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
                    />
                    <div className="flex justify-end space-x-3 mt-6">
                        <button
                            onClick={() => setInputModal(prev => ({ ...prev, isOpen: false }))}
                            className="px-4 py-2 text-gray-600 font-medium hover:bg-gray-50 rounded-lg transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            onClick={(e) => {
                                const input = (e.currentTarget.parentElement?.previousElementSibling as HTMLInputElement);
                                inputModal.onConfirm(input.value);
                            }}
                            className="px-6 py-2 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition-colors"
                        >
                            Confirm
                        </button>
                    </div>
                </div>
            </Modal>

            {/* Confirmation Modal */}
            <Modal
                isOpen={confirmModal.isOpen}
                onClose={() => setConfirmModal(prev => ({ ...prev, isOpen: false }))}
                title={confirmModal.title}
                maxWidth="max-w-sm"
            >
                <div className="text-center">
                    <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-red-100 mb-4">
                        <FiTrash2 className="h-6 w-6 text-red-600" />
                    </div>
                    <p className="text-sm text-gray-500 mb-6">{confirmModal.message}</p>
                    <div className="flex justify-center space-x-3">
                        <button
                            onClick={() => setConfirmModal(prev => ({ ...prev, isOpen: false }))}
                            className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors font-medium"
                        >
                            Cancel
                        </button>
                        <button
                            onClick={confirmModal.onConfirm}
                            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium shadow-sm"
                        >
                            Delete
                        </button>
                    </div>
                </div>
            </Modal>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {countries.map((country) => (
                    <div key={country.country_id} className="bg-white shadow rounded-lg border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
                        <div className="p-4 border-b border-gray-100 flex justify-between items-center bg-gray-50">
                            <div className="flex items-center">
                                <FiMapPin className="text-indigo-500 mr-2" />
                                <span className="font-bold text-gray-900">{country.country_name}</span>
                            </div>
                            <div className="flex space-x-2">
                                <button
                                    onClick={() => openEditCountry(country)}
                                    className="text-indigo-600 hover:text-indigo-900 p-1 hover:bg-indigo-100 rounded transition-colors"
                                >
                                    <FiEdit2 size={16} />
                                </button>
                                <button
                                    onClick={() => handleDeleteCountry(country.country_id)}
                                    className="text-red-600 hover:text-red-900 p-1 hover:bg-red-100 rounded transition-colors"
                                >
                                    <FiTrash2 size={16} />
                                </button>
                            </div>
                        </div>
                        <div className="p-4 bg-white">
                            <div className="grid grid-cols-2 gap-4 text-sm mb-4">
                                <div className="text-gray-500">ISO Code: <span className="text-gray-900 font-medium">{country.iso_code || 'N/A'}</span></div>
                                <div className="text-gray-500">Region: <span className="text-gray-900 font-medium">{country.region || 'N/A'}</span></div>
                            </div>
                            <button
                                onClick={() => handleManageCountry(country)}
                                className="w-full mt-2 inline-flex justify-center items-center px-4 py-2 bg-indigo-50 border border-transparent rounded-lg font-semibold text-indigo-700 hover:bg-indigo-100 transition-colors"
                            >
                                <FiBook className="mr-2" /> Manage Curricula
                            </button>
                        </div>
                    </div>
                ))}
            </div>
            {countries.length === 0 && !isLoading && (
                <div className="text-center py-12 bg-white rounded-xl border-2 border-dashed border-gray-200">
                    <FiMapPin className="mx-auto h-12 w-12 text-gray-300 mb-3" />
                    <h3 className="text-lg font-medium text-gray-900">No Countries Defined</h3>
                    <p className="text-gray-500 mt-1">Get started by adding a country to the system.</p>
                    <button
                        onClick={openCreateCountry}
                        className="mt-4 inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors shadow-sm"
                    >
                        <FiPlus className="mr-2" /> Add Country
                    </button>
                </div>
            )}
        </div>
    );
};

export default CurriculumManager;

