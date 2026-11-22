import catalog from "../data/catalog.json";
import { quizzes } from "../data/quizzes";
import { PracticePad } from "./PracticePad";
import { QuizPanel } from "./QuizPanel";

type Lesson = (typeof catalog.lessons)[number];

type Props = {
  lesson: Lesson;
  completed: boolean;
  quizScore?: number;
  onBack: () => void;
  onPrev?: () => void;
  onNext?: () => void;
  onComplete: () => void;
  onQuiz: (score: number) => void;
};

function fmt(sec: number) {
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
}

export function LessonView({
  lesson,
  completed,
  quizScore,
  onBack,
  onPrev,
  onNext,
  onComplete,
  onQuiz,
}: Props) {
  const mod = catalog.modules.find((m) => m.id === lesson.moduleId);
  const quiz = quizzes[lesson.quizId];

  return (
    <article className="lesson">
      <button type="button" className="back-link" onClick={onBack}>
        ← Все уроки
      </button>

      <header className="lesson-hero">
        <div className="lesson-meta">
          <span className="pill">Модуль {mod?.level}: {mod?.title}</span>
          <span className="pill muted">Урок {lesson.id} / 41</span>
          <span className="pill muted">{fmt(lesson.durationSec)}</span>
          {completed ? <span className="pill ok">Пройден</span> : null}
        </div>
        <h1>{lesson.titleRu}</h1>
        <p className="lede">{lesson.summaryRu}</p>
        <p className="en-title">{lesson.titleEn}</p>
        <div className="skills">
          {lesson.skills.map((s) => (
            <span key={s} className="skill">
              {s}
            </span>
          ))}
        </div>
      </header>

      <div className="video-frame">
        <iframe
          title={lesson.titleRu}
          src={`https://www.youtube-nocookie.com/embed/${lesson.youtubeId}?rel=0`}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
        />
      </div>
      <p className="credit">
        Видео:{" "}
        <a
          href={`https://www.youtube.com/watch?v=${lesson.youtubeId}`}
          target="_blank"
          rel="noreferrer"
        >
          {catalog.source.name}
        </a>{" "}
        · встроено с YouTube (не скачивалось)
      </p>

      <div className="steps">
        <div className="step">
          <strong>1. Смотрите</strong>
          <span>Один раз целиком, не торопясь повторять руками.</span>
        </div>
        <div className="step">
          <strong>2. Повторите на инструменте</strong>
          <span>Медленно, руки отдельно, затем вместе.</span>
        </div>
        <div className="step">
          <strong>3. Закрепите здесь</strong>
          <span>Клавиатура + мини-тест ниже.</span>
        </div>
      </div>

      <PracticePad lessonId={lesson.id} />

      {quiz ? (
        <QuizPanel
          key={lesson.id}
          quiz={quiz}
          onComplete={(score) => onQuiz(score)}
        />
      ) : null}

      {typeof quizScore === "number" ? (
        <p className="saved-score">
          Лучший результат теста: {Math.round(quizScore * 100)}%
        </p>
      ) : null}

      <footer className="lesson-footer">
        <button type="button" className="btn ghost" disabled={!onPrev} onClick={onPrev}>
          ← Предыдущий
        </button>
        <button type="button" className="btn primary" onClick={onComplete}>
          {completed ? "Урок отмечен" : "Отметить пройденным"}
        </button>
        <button type="button" className="btn ghost" disabled={!onNext} onClick={onNext}>
          Следующий →
        </button>
      </footer>
    </article>
  );
}
