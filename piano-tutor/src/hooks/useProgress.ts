import { useCallback, useEffect, useState } from "react";

const KEY = "piano-tutor-progress-v1";

export type ProgressState = {
  completedLessons: number[];
  quizScores: Record<string, number>;
  lastLessonId: number | null;
};

const defaultState: ProgressState = {
  completedLessons: [],
  quizScores: {},
  lastLessonId: null,
};

function load(): ProgressState {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return defaultState;
    return { ...defaultState, ...JSON.parse(raw) };
  } catch {
    return defaultState;
  }
}

export function useProgress() {
  const [progress, setProgress] = useState<ProgressState>(defaultState);

  useEffect(() => {
    setProgress(load());
  }, []);

  const persist = useCallback((next: ProgressState) => {
    setProgress(next);
    localStorage.setItem(KEY, JSON.stringify(next));
  }, []);

  const markLessonComplete = useCallback(
    (lessonId: number) => {
      const completed = new Set(progress.completedLessons);
      completed.add(lessonId);
      persist({
        ...progress,
        completedLessons: [...completed].sort((a, b) => a - b),
        lastLessonId: lessonId,
      });
    },
    [persist, progress],
  );

  const saveQuizScore = useCallback(
    (quizId: string, score: number, lessonId: number) => {
      persist({
        ...progress,
        quizScores: { ...progress.quizScores, [quizId]: score },
        lastLessonId: lessonId,
        completedLessons:
          score >= 0.67
            ? [...new Set([...progress.completedLessons, lessonId])].sort(
                (a, b) => a - b,
              )
            : progress.completedLessons,
      });
    },
    [persist, progress],
  );

  const setLastLesson = useCallback(
    (lessonId: number) => {
      persist({ ...progress, lastLessonId: lessonId });
    },
    [persist, progress],
  );

  const reset = useCallback(() => {
    persist(defaultState);
  }, [persist]);

  return {
    progress,
    markLessonComplete,
    saveQuizScore,
    setLastLesson,
    reset,
  };
}
