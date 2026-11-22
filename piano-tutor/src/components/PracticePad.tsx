import { PianoKeyboard } from "./PianoKeyboard";
import { usePianoAudio } from "../hooks/usePianoAudio";

type Props = {
  lessonId: number;
};

const PRESETS: Record<
  number,
  { label: string; highlight: string[]; chords?: string[][] }
> = {
  1: { label: "Найдите все C (до) — они слева от группы из двух чёрных", highlight: ["C3", "C4", "C5"] },
  2: { label: "C-позиция правой: C D E F G", highlight: ["C4", "D4", "E4", "F4", "G4"] },
  3: { label: "Наиграйте начало Ode to Joy: E E F G", highlight: ["E4", "F4", "G4"] },
  5: { label: "C-позиция левой: C D E F G ниже середины", highlight: ["C3", "D3", "E3", "F3", "G3"] },
  11: {
    label: "Аккорд C major: C–E–G",
    highlight: ["C4", "E4", "G4"],
    chords: [["C4", "E4", "G4"]],
  },
  12: {
    label: "G7 (упрощённо): G–B–D–F",
    highlight: ["G3", "B3", "D4", "F4"],
    chords: [["G3", "B3", "D4", "F4"]],
  },
  15: {
    label: "F major: F–A–C",
    highlight: ["F3", "A3", "C4"],
    chords: [["F3", "A3", "C4"]],
  },
  17: { label: "Диез: F и F♯ рядом", highlight: ["F4", "F#4"] },
  29: { label: "Бемоль: B и B♭", highlight: ["B4", "A#4"] },
  30: { label: "Полутон E–F и тон C–D", highlight: ["E4", "F4", "C4", "D4"] },
  31: {
    label: "Гамма C: C D E F G A B C",
    highlight: ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"],
  },
  32: {
    label: "I–IV–V7 в C: C, F, G7",
    highlight: ["C4", "E4", "G4", "F3", "A3", "C4"],
    chords: [
      ["C4", "E4", "G4"],
      ["F3", "A3", "C4"],
      ["G3", "B3", "D4", "F4"],
    ],
  },
  34: { label: "В G major есть F♯", highlight: ["G4", "A4", "B4", "C5", "D4", "E4", "F#4"] },
  36: { label: "В F major есть B♭", highlight: ["F4", "G4", "A4", "A#4", "C5"] },
  37: { label: "A minor: A B C D E F G A", highlight: ["A3", "B3", "C4", "D4", "E4", "F4", "G4", "A4"] },
};

export function PracticePad({ lessonId }: Props) {
  const preset = PRESETS[lessonId] ?? {
    label: "Повторите ноты из видео на виртуальной клавиатуре",
    highlight: [],
  };
  const { playChord, play } = usePianoAudio();

  return (
    <section className="practice panel">
      <header className="panel-head">
        <h3>Практика за экраном</h3>
        <p>{preset.label}</p>
      </header>
      <PianoKeyboard highlight={preset.highlight} />
      <div className="practice-actions">
        {preset.chords?.map((chord, i) => (
          <button
            key={i}
            type="button"
            className="btn ghost"
            onClick={() => playChord(chord)}
          >
            Сыграть аккорд {i + 1}
          </button>
        ))}
        {lessonId === 31 ? (
          <button
            type="button"
            className="btn ghost"
            onClick={() => {
              const scale = ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"];
              scale.forEach((n, i) => window.setTimeout(() => play(n, 0.35), i * 280));
            }}
          >
            Проиграть гамму C
          </button>
        ) : null}
      </div>
      <p className="hint">
        Лучше сразу повторять то же на своём инструменте. Экран — для проверки
        нот и слуха.
      </p>
    </section>
  );
}
