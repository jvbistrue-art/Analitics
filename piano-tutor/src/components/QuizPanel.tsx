import { useMemo, useState } from "react";
import type { Quiz } from "../data/quizzes";

type Props = {
  quiz: Quiz;
  onComplete: (score: number) => void;
};

export function QuizPanel({ quiz, onComplete }: Props) {
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [submitted, setSubmitted] = useState(false);

  const score = useMemo(() => {
    if (!submitted) return 0;
    let ok = 0;
    for (const q of quiz.questions) {
      if (answers[q.id] === q.answer) ok += 1;
    }
    return ok / quiz.questions.length;
  }, [answers, quiz.questions, submitted]);

  const submit = () => {
    setSubmitted(true);
    let ok = 0;
    for (const q of quiz.questions) {
      if (answers[q.id] === q.answer) ok += 1;
    }
    onComplete(ok / quiz.questions.length);
  };

  const allAnswered = quiz.questions.every((q) => answers[q.id] !== undefined);

  return (
    <section className="quiz panel">
      <header className="panel-head">
        <h3>Проверка: {quiz.title}</h3>
        <p>Ответьте на вопросы после просмотра и практики.</p>
      </header>
      <div className="quiz-list">
        {quiz.questions.map((q, i) => {
          const chosen = answers[q.id];
          return (
            <div key={q.id} className="quiz-item">
              <p className="quiz-prompt">
                {i + 1}. {q.prompt}
              </p>
              <div className="quiz-choices">
                {q.choices.map((c, ci) => {
                  let cls = "choice";
                  if (submitted) {
                    if (ci === q.answer) cls += " correct";
                    else if (ci === chosen) cls += " wrong";
                  } else if (chosen === ci) cls += " selected";
                  return (
                    <button
                      key={c}
                      type="button"
                      className={cls}
                      disabled={submitted}
                      onClick={() =>
                        setAnswers((a) => ({ ...a, [q.id]: ci }))
                      }
                    >
                      {c}
                    </button>
                  );
                })}
              </div>
              {submitted && q.explain ? (
                <p className="quiz-explain">{q.explain}</p>
              ) : null}
            </div>
          );
        })}
      </div>
      {!submitted ? (
        <button
          type="button"
          className="btn primary"
          disabled={!allAnswered}
          onClick={submit}
        >
          Проверить
        </button>
      ) : (
        <p className="quiz-score">
          Результат: {Math.round(score * 100)}%
          {score >= 0.67
            ? " — урок можно отметить пройденным."
            : " — пересмотрите видео и попробуйте ещё раз."}
        </p>
      )}
    </section>
  );
}
