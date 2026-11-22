import { useCallback, useRef } from "react";

const NOTE_FREQ: Record<string, number> = {
  C3: 130.81,
  "C#3": 138.59,
  D3: 146.83,
  "D#3": 155.56,
  E3: 164.81,
  F3: 174.61,
  "F#3": 185.0,
  G3: 196.0,
  "G#3": 207.65,
  A3: 220.0,
  "A#3": 233.08,
  B3: 246.94,
  C4: 261.63,
  "C#4": 277.18,
  D4: 293.66,
  "D#4": 311.13,
  E4: 329.63,
  F4: 349.23,
  "F#4": 369.99,
  G4: 392.0,
  "G#4": 415.3,
  A4: 440.0,
  "A#4": 466.16,
  B4: 493.88,
  C5: 523.25,
};

export function usePianoAudio() {
  const ctxRef = useRef<AudioContext | null>(null);

  const ensure = useCallback(() => {
    if (!ctxRef.current) {
      ctxRef.current = new AudioContext();
    }
    if (ctxRef.current.state === "suspended") {
      void ctxRef.current.resume();
    }
    return ctxRef.current;
  }, []);

  const play = useCallback(
    (note: string, duration = 0.45) => {
      const freq = NOTE_FREQ[note];
      if (!freq) return;
      const ctx = ensure();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "triangle";
      osc.frequency.value = freq;
      gain.gain.setValueAtTime(0.0001, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.22, ctx.currentTime + 0.02);
      gain.gain.exponentialRampToValueAtTime(
        0.0001,
        ctx.currentTime + duration,
      );
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + duration + 0.05);
    },
    [ensure],
  );

  const playChord = useCallback(
    (notes: string[]) => {
      notes.forEach((n, i) => {
        window.setTimeout(() => play(n, 0.7), i * 30);
      });
    },
    [play],
  );

  return { play, playChord };
}

export const WHITE_NOTES = [
  "C3",
  "D3",
  "E3",
  "F3",
  "G3",
  "A3",
  "B3",
  "C4",
  "D4",
  "E4",
  "F4",
  "G4",
  "A4",
  "B4",
  "C5",
] as const;

export const BLACK_NOTES: { note: string; afterWhiteIndex: number }[] = [
  { note: "C#3", afterWhiteIndex: 0 },
  { note: "D#3", afterWhiteIndex: 1 },
  { note: "F#3", afterWhiteIndex: 3 },
  { note: "G#3", afterWhiteIndex: 4 },
  { note: "A#3", afterWhiteIndex: 5 },
  { note: "C#4", afterWhiteIndex: 7 },
  { note: "D#4", afterWhiteIndex: 8 },
  { note: "F#4", afterWhiteIndex: 10 },
  { note: "G#4", afterWhiteIndex: 11 },
  { note: "A#4", afterWhiteIndex: 12 },
];
