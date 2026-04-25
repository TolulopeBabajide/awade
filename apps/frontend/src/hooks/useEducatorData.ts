import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiService from '../services/api';
import { useAuth } from '../contexts/AuthContext';

// ─── Query Keys ────────────────────────────────────────────────
export const educatorKeys = {
  all: ['educator'] as const,
  countries: () => [...educatorKeys.all, 'countries'] as const,
  curriculums: (countryId: number) => [...educatorKeys.all, 'curriculums', countryId] as const,
  curriculumStructures: (curriculaId: number) => [...educatorKeys.all, 'structures', curriculaId] as const,
  subjects: () => [...educatorKeys.all, 'subjects'] as const,
  gradeLevels: () => [...educatorKeys.all, 'gradeLevels'] as const,
  topics: (structureId: number) => [...educatorKeys.all, 'topics', structureId] as const,
  lessonPlans: () => [...educatorKeys.all, 'lessonPlans'] as const,
  lessonPlan: (id: string) => [...educatorKeys.all, 'lessonPlan', id] as const,
  lessonResources: () => [...educatorKeys.all, 'lessonResources'] as const,
  lessonResource: (id: string) => [...educatorKeys.all, 'lessonResource', id] as const,
};

// ─── Curriculum Queries ────────────────────────────────────────

export function useCountries() {
  const { user } = useAuth();
  return useQuery({
    queryKey: educatorKeys.countries(),
    queryFn: async () => {
      const response = await apiService.getCountries();
      if (response.error) throw new Error(response.error);
      return response.data ?? [];
    },
    enabled: !!user,
    staleTime: 10 * 60 * 1000, // countries rarely change
  });
}

export function useCurriculums(countryId: number | null) {
  return useQuery({
    queryKey: educatorKeys.curriculums(countryId!),
    queryFn: async () => {
      const response = await apiService.getCurriculums(countryId!);
      if (response.error) throw new Error(response.error);
      return response.data ?? [];
    },
    enabled: !!countryId,
    staleTime: 10 * 60 * 1000,
  });
}

export function useCurriculumStructures(curriculaId: number | null) {
  return useQuery({
    queryKey: educatorKeys.curriculumStructures(curriculaId!),
    queryFn: async () => {
      const response = await apiService.getCurriculumStructures(curriculaId!);
      if (response.error) throw new Error(response.error);
      return response.data ?? [];
    },
    enabled: !!curriculaId,
    staleTime: 10 * 60 * 1000,
  });
}

export function useSubjects() {
  return useQuery({
    queryKey: educatorKeys.subjects(),
    queryFn: async () => {
      const response = await apiService.getSubjects();
      if (response.error) throw new Error(response.error);
      return response.data ?? [];
    },
    staleTime: 10 * 60 * 1000,
  });
}

export function useGradeLevels() {
  return useQuery({
    queryKey: educatorKeys.gradeLevels(),
    queryFn: async () => {
      const response = await apiService.getGradeLevels();
      if (response.error) throw new Error(response.error);
      return response.data ?? [];
    },
    staleTime: 10 * 60 * 1000,
  });
}

export function useTopics(structureId: number | null) {
  return useQuery({
    queryKey: educatorKeys.topics(structureId!),
    queryFn: async () => {
      const response = await apiService.getTopicsByCurriculumStructure(structureId!);
      if (response.error) throw new Error(response.error);
      return response.data ?? [];
    },
    enabled: !!structureId,
    staleTime: 5 * 60 * 1000,
  });
}

// ─── Lesson Plan Queries ───────────────────────────────────────

export function useLessonPlans() {
  const { user } = useAuth();
  return useQuery({
    queryKey: educatorKeys.lessonPlans(),
    queryFn: async () => {
      const response = await apiService.getLessonPlans();
      if (response.error) throw new Error(response.error);
      return response.data ?? [];
    },
    enabled: !!user,
  });
}

export function useLessonPlan(id: string | undefined) {
  return useQuery({
    queryKey: educatorKeys.lessonPlan(id!),
    queryFn: async () => {
      const response = await apiService.getLessonPlan(id!);
      if (response.error) throw new Error(response.error);
      return response.data;
    },
    enabled: !!id,
  });
}

// ─── Lesson Resource Queries ───────────────────────────────────

export function useAllLessonResources() {
  const { user } = useAuth();
  return useQuery({
    queryKey: educatorKeys.lessonResources(),
    queryFn: async () => {
      const response = await apiService.getAllLessonResources();
      if (response.error) throw new Error(response.error);
      return response.data ?? [];
    },
    enabled: !!user,
  });
}

// ─── Mutations ─────────────────────────────────────────────────

export function useGenerateLessonPlan() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (planData: {
      subject: string;
      grade_level: string;
      topic: string;
      user_id?: number;
    }) => {
      const response = await apiService.generateLessonPlan(planData);
      if (response.error) throw new Error(response.error);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: educatorKeys.lessonPlans() });
      queryClient.invalidateQueries({ queryKey: educatorKeys.lessonResources() });
    },
  });
}
