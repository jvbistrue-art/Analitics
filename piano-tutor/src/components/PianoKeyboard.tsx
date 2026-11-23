import { useState } from "react";
import {
  BLACK_NOTES,
  WHITE_NOTES,
  usePianoAudio,
} from "../hooks/usePianoAudio";

type Props = {
  highlight?: string[];
  label?: string;
  onPlayNote?: (note: string) => void;
};

export function PianoKeyboard({ highlight = [], label, onPlayNote }: Props) {
  const { play } = usePianoAudio();
  const [active, setActive] = useState<string | null>(null);

  const press = (note: string) => {
    setActive(note);
    play(note);
    onPlayNote?.(note);
    window.setTimeout(() => setActive(null), 180);
  };

  return (
    <div className="piano-wrap">
      {label ? <p className="piano-label">{label}</p> : null}
      <div className="piano" role="group" aria-label="Интерактивная клавиатура">
        <div className="piano-whites">
          {WHITE_NOTES.map((note) => {
            const lit = highlight.includes(note) || active === note;
            return (
              <button
                key={note}
                type="button"
                className={`key white${lit ? " lit" : ""}`}
                onClick={() => press(note)}
                aria-label={note}
              >
                <span>{note.replace(/\d/, "")}</span>
              </button>
            );
          })}
        </div>
        <div className="piano-blacks">
          {BLACK_NOTES.map(({ note, afterWhiteIndex }) => {
            const lit = highlight.includes(note) || active === note;
            const left = `calc(${(afterWhiteIndex + 1) * (100 / WHITE_NOTES.length)}% - 1.1%)`;
            return (
              <button
                key={note}
                type="button"
                className={`key black${lit ? " lit" : ""}`}
                style={{ left }}
                onClick={() => press(note)}
                aria-label={note}
              />
            );
          })}
        </div>
      </div>
    </div>
  );
}
