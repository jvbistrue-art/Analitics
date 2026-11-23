export type QuizQuestion = {
  id: string;
  prompt: string;
  choices: string[];
  answer: number;
  explain?: string;
};

export type Quiz = {
  id: string;
  title: string;
  questions: QuizQuestion[];
};

/** Мини-проверка после урока. Ключ = quizId из catalog. */
export const quizzes: Record<string, Quiz> = {
  "find-keys": {
    id: "find-keys",
    title: "Клавиатура и посадка",
    questions: [
      {
        id: "q1",
        prompt: "Где сидеть относительно клавиш?",
        choices: [
          "Глубоко на стуле, откинувшись",
          "На передней трети стула, предплечья примерно параллельны полу",
          "Стоя у инструмента",
        ],
        answer: 1,
      },
      {
        id: "q2",
        prompt: "Сколько чёрных клавиш в группе «двойка»?",
        choices: ["1", "2", "3"],
        answer: 1,
      },
      {
        id: "q3",
        prompt: "Большой палец — это палец номер…",
        choices: ["1", "3", "5"],
        answer: 0,
      },
    ],
  },
  "treble-c": {
    id: "treble-c",
    title: "Скрипичный ключ",
    questions: [
      {
        id: "q1",
        prompt: "Скрипичный ключ указывает на ноту…",
        choices: ["Фа", "Соль", "До"],
        answer: 1,
        explain: "Ключ Соль — завиток вокруг второй линии (соль).",
      },
      {
        id: "q2",
        prompt: "В C-позиции правой большой палец (1) стоит на…",
        choices: ["До (C)", "Ми (E)", "Соль (G)"],
        answer: 0,
      },
    ],
  },
  "ode-joy": {
    id: "ode-joy",
    title: "Ритм: четверть и половина",
    questions: [
      {
        id: "q1",
        prompt: "Четвертная нота в размере 4/4 длится…",
        choices: ["1 долю", "2 доли", "4 доли"],
        answer: 0,
      },
      {
        id: "q2",
        prompt: "Половинная нота длится…",
        choices: ["1 долю", "2 доли", "½ доли"],
        answer: 1,
      },
    ],
  },
  "whole-note": {
    id: "whole-note",
    title: "Целая нота",
    questions: [
      {
        id: "q1",
        prompt: "Целая нота в 4/4 держится…",
        choices: ["2 доли", "3 доли", "4 доли"],
        answer: 2,
      },
    ],
  },
  "bass-c": {
    id: "bass-c",
    title: "Басовый ключ",
    questions: [
      {
        id: "q1",
        prompt: "Басовый ключ — это ключ…",
        choices: ["Соль", "Фа", "До"],
        answer: 1,
      },
      {
        id: "q2",
        prompt: "В C-позиции левой мизинец (5) обычно на…",
        choices: ["До ниже середины", "Соль выше середины", "Ля"],
        answer: 0,
      },
    ],
  },
  "grand-staff": {
    id: "grand-staff",
    title: "Большой стан",
    questions: [
      {
        id: "q1",
        prompt: "Размер 4/4 означает…",
        choices: [
          "4 доли в такте, четверть = 1 доля",
          "4 такта в пьесе",
          "Только 4 ноты подряд",
        ],
        answer: 0,
      },
    ],
  },
  "int-23": {
    id: "int-23",
    title: "Секунды и терции",
    questions: [
      {
        id: "q1",
        prompt: "Интервал от C до D — это…",
        choices: ["секунда (2)", "терция (3)", "кварта (4)"],
        answer: 0,
      },
      {
        id: "q2",
        prompt: "Интервал от C до E — это…",
        choices: ["секунда", "терция", "квинта"],
        answer: 1,
      },
    ],
  },
  "harm-23": {
    id: "harm-23",
    title: "Гармонические интервалы",
    questions: [
      {
        id: "q1",
        prompt: "Гармонический интервал — это когда ноты…",
        choices: ["играются по очереди", "звучат одновременно", "только в левой руке"],
        answer: 1,
      },
    ],
  },
  "int-45": {
    id: "int-45",
    title: "Кварты и квинты",
    questions: [
      {
        id: "q1",
        prompt: "От C до F — это…",
        choices: ["терция", "кварта", "квинта"],
        answer: 1,
      },
      {
        id: "q2",
        prompt: "От C до G — это…",
        choices: ["кварта", "квинта", "секста"],
        answer: 1,
      },
    ],
  },
  jingle: {
    id: "jingle",
    title: "Практика двумя руками",
    questions: [
      {
        id: "q1",
        prompt: "Лучший порядок разбора новой пьесы?",
        choices: [
          "Сразу двумя руками в темпе",
          "Правая → левая → вместе, медленно",
          "Только левая рука до конца курса",
        ],
        answer: 1,
      },
    ],
  },
  "chord-c": {
    id: "chord-c",
    title: "Аккорд C",
    questions: [
      {
        id: "q1",
        prompt: "Трезвучие C major состоит из…",
        choices: ["C–D–E", "C–E–G", "C–F–G"],
        answer: 1,
      },
    ],
  },
  "chord-g7": {
    id: "chord-g7",
    title: "Аккорд G7",
    questions: [
      {
        id: "q1",
        prompt: "G7 (упрощённо часто) включает ноты вокруг…",
        choices: ["G–B–D–F", "G–A–B", "C–E–G"],
        answer: 0,
      },
    ],
  },
  waltz: {
    id: "waltz",
    title: "Размер 3/4",
    questions: [
      {
        id: "q1",
        prompt: "В размере 3/4 в такте…",
        choices: ["2 доли", "3 доли", "4 доли"],
        answer: 1,
      },
    ],
  },
  legato: {
    id: "legato",
    title: "Легато",
    questions: [
      {
        id: "q1",
        prompt: "Легато означает…",
        choices: ["отрывисто", "связно, плавно", "только педалью"],
        answer: 1,
      },
    ],
  },
  "chord-f": {
    id: "chord-f",
    title: "Аккорд F",
    questions: [
      {
        id: "q1",
        prompt: "F major — это…",
        choices: ["F–A–C", "F–G–A", "E–G–C"],
        answer: 0,
      },
    ],
  },
  "g-pos": {
    id: "g-pos",
    title: "G-позиция",
    questions: [
      {
        id: "q1",
        prompt: "В G-позиции правой большой палец на…",
        choices: ["C", "G", "F"],
        answer: 1,
      },
    ],
  },
  sharp: {
    id: "sharp",
    title: "Диез",
    questions: [
      {
        id: "q1",
        prompt: "Диез ♯ делает ноту…",
        choices: ["ниже на полтона", "выше на полтона", "тише"],
        answer: 1,
      },
    ],
  },
  "pedal-d7": {
    id: "pedal-d7",
    title: "Педаль",
    questions: [
      {
        id: "q1",
        prompt: "Правая (демпферная) педаль…",
        choices: [
          "делает звук короче",
          "поднимает демпферы — звук дольше «звучит»",
          "меняет октаву",
        ],
        answer: 1,
      },
    ],
  },
  "c-inv": {
    id: "c-inv",
    title: "Обращения",
    questions: [
      {
        id: "q1",
        prompt: "Обращение аккорда — это…",
        choices: [
          "другая тональность",
          "тот же аккорд с другой нижней нотой",
          "только минор",
        ],
        answer: 1,
      },
    ],
  },
  "middle-c": {
    id: "middle-c",
    title: "Middle C",
    questions: [
      {
        id: "q1",
        prompt: "До¹ (middle C) лежит…",
        choices: [
          "между скрипичным и басовым станами",
          "только в басовом ключе",
          "на самой высокой клавише",
        ],
        answer: 0,
      },
    ],
  },
  cresc: {
    id: "cresc",
    title: "Динамика",
    questions: [
      {
        id: "q1",
        prompt: "Crescendo означает…",
        choices: ["тише", "громче постепенно", "быстрее"],
        answer: 1,
      },
    ],
  },
  birthday: {
    id: "birthday",
    title: "Фермата",
    questions: [
      {
        id: "q1",
        prompt: "Фермата — это…",
        choices: ["ускорение", "свободная задержка на ноте/паузе", "педаль"],
        answer: 1,
      },
    ],
  },
  eighths: {
    id: "eighths",
    title: "Восьмые",
    questions: [
      {
        id: "q1",
        prompt: "Две восьмые равны…",
        choices: ["половине", "одной четверти", "целой"],
        answer: 1,
      },
    ],
  },
  dotted: {
    id: "dotted",
    title: "Пунктир",
    questions: [
      {
        id: "q1",
        prompt: "Точка у ноты добавляет…",
        choices: [
          "половину длительности ноты",
          "ещё одну такую же ноту",
          "паузу",
        ],
        answer: 0,
      },
    ],
  },
  sixths: {
    id: "sixths",
    title: "Сексты",
    questions: [
      {
        id: "q1",
        prompt: "От C до A — это…",
        choices: ["квинта", "секста", "септима"],
        answer: 1,
      },
    ],
  },
  twofour: {
    id: "twofour",
    title: "2/4",
    questions: [
      {
        id: "q1",
        prompt: "В 2/4 в такте…",
        choices: ["2 доли", "4 доли", "3 доли"],
        answer: 0,
      },
    ],
  },
  staccato: {
    id: "staccato",
    title: "Стаккато",
    questions: [
      {
        id: "q1",
        prompt: "Стаккато — это…",
        choices: ["связно", "коротко, отрывисто", "с ферматой"],
        answer: 1,
      },
    ],
  },
  octaves: {
    id: "octaves",
    title: "Октавы",
    questions: [
      {
        id: "q1",
        prompt: "Октава — интервал в…",
        choices: ["5 ступеней", "8 ступеней (от C до следующего C)", "3 ступени"],
        answer: 1,
      },
    ],
  },
  flat: {
    id: "flat",
    title: "Бемоль",
    questions: [
      {
        id: "q1",
        prompt: "Бемоль ♭ делает ноту…",
        choices: ["выше на полтона", "ниже на полтона", "громче"],
        answer: 1,
      },
    ],
  },
  steps: {
    id: "steps",
    title: "Тоны и полутоны",
    questions: [
      {
        id: "q1",
        prompt: "От E до F — это…",
        choices: ["целый тон", "полутон", "терция"],
        answer: 1,
      },
    ],
  },
  "scale-c": {
    id: "scale-c",
    title: "Гамма C",
    questions: [
      {
        id: "q1",
        prompt: "Формула мажорной гаммы (Т = тон, п = полутон):",
        choices: ["Т Т п Т Т Т п", "Т п Т Т п Т Т", "п Т Т п Т Т Т"],
        answer: 0,
      },
    ],
  },
  "blues-c": {
    id: "blues-c",
    title: "I–IV–V7",
    questions: [
      {
        id: "q1",
        prompt: "В тональности C: I, IV, V7 — это…",
        choices: ["C, F, G7", "C, G, Am", "Dm, G, C"],
        answer: 0,
      },
    ],
  },
  natural: {
    id: "natural",
    title: "Бекар",
    questions: [
      {
        id: "q1",
        prompt: "Бекар ♮…",
        choices: [
          "отменяет диез или бемоль",
          "всегда повышает ноту",
          "меняет размер",
        ],
        answer: 0,
      },
    ],
  },
  "scale-g": {
    id: "scale-g",
    title: "Гамма G",
    questions: [
      {
        id: "q1",
        prompt: "В гамме G major есть…",
        choices: ["B♭", "F♯", "C♯"],
        answer: 1,
      },
    ],
  },
  "chords-g": {
    id: "chords-g",
    title: "Аккорды G",
    questions: [
      {
        id: "q1",
        prompt: "В G major V7 — это…",
        choices: ["G7", "D7", "C7"],
        answer: 1,
      },
    ],
  },
  "scale-f": {
    id: "scale-f",
    title: "Гамма F",
    questions: [
      {
        id: "q1",
        prompt: "В гамме F major есть…",
        choices: ["B♭", "F♯", "G♯"],
        answer: 0,
      },
    ],
  },
  "a-minor": {
    id: "a-minor",
    title: "Ля минор",
    questions: [
      {
        id: "q1",
        prompt: "Относительный минор к C major — это…",
        choices: ["A minor", "E minor", "D minor"],
        answer: 0,
      },
    ],
  },
  overlap: {
    id: "overlap",
    title: "Педаль overlapping",
    questions: [
      {
        id: "q1",
        prompt: "Overlapping pedal помогает…",
        choices: [
          "играть стаккато",
          "связывать гармонии без «грязи»",
          "ускорить темп",
        ],
        answer: 1,
      },
    ],
  },
  "chords-am": {
    id: "chords-am",
    title: "Аккорды a-moll",
    questions: [
      {
        id: "q1",
        prompt: "В A minor часто V7 — это…",
        choices: ["Am", "E7", "F"],
        answer: 1,
      },
    ],
  },
  "d-minor": {
    id: "d-minor",
    title: "Ре минор",
    questions: [
      {
        id: "q1",
        prompt: "В гармоническом миноре VII ступень…",
        choices: ["понижается", "повышается", "убирается"],
        answer: 1,
      },
    ],
  },
  arpeggio: {
    id: "arpeggio",
    title: "Арпеджио-аккорд",
    questions: [
      {
        id: "q1",
        prompt: "Rolled / arpeggiated chord — это когда…",
        choices: [
          "все ноты разом жёстко",
          "ноты аккорда быстро «перебираются» снизу вверх",
          "играется только одна нота",
        ],
        answer: 1,
      },
    ],
  },
};
