import { useMemo, useState } from "react";
import catalog from "./data/catalog.json";
import { LessonView } from "./components/LessonView";
import { useProgress } from "./hooks/useProgress";

type View =
  | { kind: "home" }
  | { kind: "lesson"; id: number };

export default function App() {
  const { progress, markLessonComplete, saveQuizScore, setLastLesson, reset } =
    useProgress();
  const [view, setView] = useState<View>({ kind: "home" });

  const doneCount = progress.completedLessons.length;
  const pct = Math.round((doneCount / catalog.lessons.length) * 100);

  const continueId = progress.lastLessonId ?? 1;

  const openLesson = (id: number) => {
    setLastLesson(id);
    setView({ kind: "lesson", id });
  };

  const currentLesson = useMemo(
    () =>
      view.kind === "lesson"
        ? catalog.lessons.find((l) => l.id === view.id)
        : null,
    [view],
  );

  if (view.kind === "lesson" && currentLesson) {
    const idx = catalog.lessons.findIndex((l) => l.id === currentLesson.id);
    return (
      <div className="app">
        <LessonView
          lesson={currentLesson}
          completed={progress.completedLessons.includes(currentLesson.id)}
          quizScore={progress.quizScores[currentLesson.quizId]}
          onBack={() => setView({ kind: "home" })}
          onPrev={
            idx > 0
              ? () => openLesson(catalog.lessons[idx - 1].id)
              : undefined
          }
          onNext={
            idx < catalog.lessons.length - 1
              ? () => openLesson(catalog.lessons[idx + 1].id)
              : undefined
          }
          onComplete={() => markLessonComplete(currentLesson.id)}
          onQuiz={(score) => saveQuizScore(currentLesson.quizId, score, currentLesson.id)}
        />
      </div>
    );
  }

  return (
    <div className="app">
      <header className="hero">
        <p className="brand">Клавиши</p>
        <h1>Интерактивный учебник пианино</h1>
        <p className="lede">
          41 урок от простого к сложному: русские конспекты по транскриптам
          бесплатного курса Online Piano University, встроенное видео, практика
          на клавиатуре и квизы. Видеофайлы не скачиваются — только официальный
          плеер YouTube.
        </p>
        <div className="hero-actions">
          <button
            type="button"
            className="btn primary"
            onClick={() => openLesson(continueId)}
          >
            {doneCount ? `Продолжить · урок ${continueId}` : "Начать с урока 1"}
          </button>
          <a
            className="btn ghost"
            href={catalog.source.coursePage}
            target="_blank"
            rel="noreferrer"
          >
            Источник курса
          </a>
        </div>
        <div className="progress-bar" aria-label="Прогресс курса">
          <div className="progress-fill" style={{ width: `${pct}%` }} />
        </div>
        <p className="progress-label">
          Пройдено {doneCount} из {catalog.lessons.length} ({pct}%)
        </p>
      </header>

      <section className="path">
        <h2>Путь обучения</h2>
        <ol className="modules">
          {catalog.modules.map((mod) => {
            const lessons = catalog.lessons.filter((l) => l.moduleId === mod.id);
            const done = lessons.filter((l) =>
              progress.completedLessons.includes(l.id),
            ).length;
            return (
              <li key={mod.id} className="module">
                <div className="module-head">
                  <div>
                    <span className="module-level">Уровень {mod.level}</span>
                    <h3>{mod.title}</h3>
                    <p>
                      Уроки {mod.fromLesson}–{mod.toLesson} · {done}/
                      {lessons.length} готово
                    </p>
                  </div>
                </div>
                <div className="lesson-grid">
                  {lessons.map((lesson) => {
                    const isDone = progress.completedLessons.includes(lesson.id);
                    return (
                      <button
                        key={lesson.id}
                        type="button"
                        className={`lesson-card${isDone ? " done" : ""}`}
                        onClick={() => openLesson(lesson.id)}
                      >
                        <img
                          src={lesson.thumb}
                          alt=""
                          loading="lazy"
                          width={320}
                          height={180}
                        />
                        <div className="lesson-card-body">
                          <span className="num">#{lesson.id}</span>
                          <strong>{lesson.titleRu}</strong>
                          <span className="dur">
                            {Math.round(lesson.durationSec / 60)} мин
                          </span>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </li>
            );
          })}
        </ol>
      </section>

      <section className="howto panel">
        <h2>Как заниматься</h2>
        <ul>
          <li>20–30 минут почти каждый день лучше, чем редкие марафоны.</li>
          <li>Идите по порядку: каждый урок опирается на предыдущий.</li>
          <li>После видео — руки на своём инструменте, потом квиз здесь.</li>
          <li>
            Не скачивайте и не перезаливайте видео курса — используйте встроенный
            плеер или YouTube автора.
          </li>
        </ul>
        <button type="button" className="btn ghost danger" onClick={reset}>
          Сбросить прогресс
        </button>
      </section>

      <footer className="site-foot">
        Оболочка учебника · видео © {catalog.source.name} ·{" "}
        <a href={catalog.source.playlist} target="_blank" rel="noreferrer">
          плейлист
        </a>
      </footer>
    </div>
  );
}
