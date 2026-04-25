/** Types for the parent/children feature */

export interface ChildProfile {
  child_id: number;
  parent_id: number;
  name: string;
  age: number | null;
  school_name: string | null;
  country_id: number | null;
  country_name: string | null;
  curricula_id: number | null;
  curricula_title: string | null;
  grade_level_id: number | null;
  grade_level_name: string | null;
  subjects: number[] | null;
  created_at: string;
  updated_at: string;
}

export interface ChildProfileCreate {
  name: string;
  age?: number | null;
  school_name?: string | null;
  country_id?: number | null;
  curricula_id?: number | null;
  grade_level_id?: number | null;
  subjects?: number[] | null;
}

export interface ChildTopic {
  topic_id: number;
  topic_title: string;
  subject_name: string | null;
  subject_id: number | null;
}

export interface ParentGuide {
  guide_id: number;
  child_id: number;
  topic_id: number;
  topic_title: string | null;
  subject_name: string | null;
  ai_generated_content: string | null;
  user_edited_content: string | null;
  is_bookmarked: boolean;
  created_at: string;
  updated_at: string;
}

export interface ParentGuideContent {
  topic_header: {
    topic: string;
    subject: string;
    grade_level: string;
    country: string;
    curriculum: string;
  };
  simple_explanation: {
    what_it_is: string;
    why_it_matters: string;
  };
  home_activity: {
    title: string;
    description: string;
    materials_needed: string[];
    steps: string[];
    what_to_look_for: string;
  };
  conversation_starters: string[];
  common_mistakes: Array<{
    mistake: string;
    why_it_happens: string;
    how_to_help: string;
  }>;
  curriculum_context: {
    what_came_before: string;
    what_comes_next: string;
    how_long_in_school: string;
  };
  encouragement_tips: string[];
}
