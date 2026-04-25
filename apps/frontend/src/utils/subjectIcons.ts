/** Map a subject name to an emoji icon. Used across lesson plan and resource cards. */
export function getSubjectIcon(subject: string): string {
  const lower = subject.toLowerCase();

  const iconMap: [string[], string][] = [
    [['math', 'mathematics'], '📐'],
    [['biology'], '🧪'],
    [['chemistry'], '⚗️'],
    [['physics'], '⚡'],
    [['inter.science', 'science'], '🔬'],
    [['english', 'language'], '📖'],
    [['literature'], '📚'],
    [['history'], '📚'],
    [['social'], '🌍'],
    [['geography'], '🗺️'],
    [['computer'], '💻'],
    [['art', 'music'], '🎨'],
    [['physical', 'pe'], '⚽'],
    [['health'], '🏥'],
  ];

  for (const [keywords, icon] of iconMap) {
    if (keywords.some(kw => lower.includes(kw))) return icon;
  }

  return '📚';
}

/** Parse a lesson resource's AI content and extract subject, topic, grade level. */
export function parseResourceContent(resource: any): {
  subject: string;
  topic: string;
  gradeLevel: string;
} {
  let subject = 'Subject';
  let topic = 'Topic';
  let gradeLevel = 'Grade';

  try {
    if (resource.ai_generated_content) {
      const parsed =
        typeof resource.ai_generated_content === 'string'
          ? JSON.parse(resource.ai_generated_content)
          : resource.ai_generated_content;

      subject = parsed?.title_header?.subject ?? subject;
      topic = parsed?.title_header?.topic ?? topic;
      gradeLevel = parsed?.title_header?.grade_level ?? gradeLevel;
    }
  } catch {
    // If parsing fails, use defaults
  }

  return { subject, topic, gradeLevel };
}
