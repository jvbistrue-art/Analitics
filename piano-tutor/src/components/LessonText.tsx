import type { LessonContent } from "../data/lessonsContent";

type Props = {
  content: LessonContent;
};

export function LessonText({ content }: Props) {
  return (
    <section className="lesson-text panel">
      <header className="panel-head">
        <h3>Конспект урока</h3>
        <p>
          По транскрипту видео Online Piano University — читайте до или после
          просмотра, практикуйте на инструменте.
        </p>
      </header>

      <div className="lt-grid">
        <div>
          <h4>Цели</h4>
          <ul>
            {content.goals.map((g) => (
              <li key={g}>{g}</li>
            ))}
          </ul>
        </div>

        <div>
          <h4>Теория</h4>
          <ul className="theory">
            {content.theory.map((t) => (
              <li key={t}>{t}</li>
            ))}
          </ul>
        </div>

        <div>
          <h4>Практика по шагам</h4>
          <ol>
            {content.practiceSteps.map((s) => (
              <li key={s}>{s}</li>
            ))}
          </ol>
        </div>

        {content.pieces.length > 0 ? (
          <div>
            <h4>Пьесы и упражнения</h4>
            <ul className="pieces">
              {content.pieces.map((p) => (
                <li key={p}>{p}</li>
              ))}
            </ul>
          </div>
        ) : null}

        {content.tips.length > 0 ? (
          <div>
            <h4>Советы преподавателя</h4>
            <ul>
              {content.tips.map((t) => (
                <li key={t}>{t}</li>
              ))}
            </ul>
          </div>
        ) : null}

        {content.keyTerms.length > 0 ? (
          <div className="terms">
            <h4>Термины</h4>
            <dl>
              {content.keyTerms.map((k) => (
                <div key={k.term} className="term">
                  <dt>{k.term}</dt>
                  <dd>{k.definition}</dd>
                </div>
              ))}
            </dl>
          </div>
        ) : null}
      </div>
    </section>
  );
}
