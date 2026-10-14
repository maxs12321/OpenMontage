import React from "react";
import {
  AbsoluteFill,
  Audio,
  CalculateMetadataFunction,
  Img,
  OffthreadVideo,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { resolveAsset } from "./lib/resolveAsset";

// Brand-styled vlog edit for "Жирафик Трафик" (styles/jirafik-trafik.yaml).
// Takes an already cut voice-led video and adds the motion layer: per-shot
// push-ins, punch transitions on cuts, keyword stickers, word-timed captions,
// a progress bar, a hook title and an animated end card.

const NAVY = "#14183A";
const ORANGE = "#F28A2E";
const GOLD = "#E3B341";
const LIGHT = "#F5F5F7";
const HEAD = "Lora, serif";
const BODY = "Inter, 'Noto Color Emoji', sans-serif";

export type VlogWord = { text: string; start: number; end: number };
export type VlogSticker = {
  text: string;
  start: number;
  duration: number;
  variant?: "orange" | "navy" | "avatar";
};

export type JirafikVlogProps = {
  videoSrc: string;
  videoDuration: number;
  cuts: number[];
  whooshAt: number[];
  emphasis: { start: number; end: number }[];
  words: VlogWord[];
  stickers: VlogSticker[];
  hook: { tag: string; line1: string; line2: string; until: number };
  captionsFrom: number;
  endCard: { seconds: number; question: string; handles: string[] };
};

export const calculateJirafikVlogMetadata: CalculateMetadataFunction<
  JirafikVlogProps
> = ({ props }) => ({
  durationInFrames: Math.ceil((props.videoDuration + props.endCard.seconds) * 30),
});

const easeOut = (x: number) => 1 - Math.pow(1 - Math.min(Math.max(x, 0), 1), 3);

// ---------------------------------------------------------------------------
// Video layer: slow push per shot, punch-in + blur on every cut, emphasis zoom
// ---------------------------------------------------------------------------
const MovingVideo: React.FC<JirafikVlogProps> = (p) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const bounds = [0, ...p.cuts, p.videoDuration];
  let i = 0;
  while (i < bounds.length - 2 && t >= bounds[i + 1]) i++;
  const shotStart = bounds[i];
  const shotLen = Math.max(bounds[i + 1] - shotStart, 0.1);
  const local = t - shotStart;
  const prog = Math.min(local / shotLen, 1);
  const push = i % 2 === 0 ? 1.03 + 0.06 * prog : 1.09 - 0.06 * prog;
  const punchT = Math.min(local / 0.22, 1);
  const punch = i === 0 ? 0 : 0.14 * Math.pow(1 - punchT, 2);
  const blur = i === 0 ? 0 : 7 * Math.pow(1 - punchT, 2);
  let emph = 0;
  for (const e of p.emphasis) {
    if (t >= e.start && t <= e.end + 0.3) {
      const inn = easeOut((t - e.start) / 0.18);
      const out = 1 - easeOut((t - e.end) / 0.3);
      emph = Math.max(emph, 0.1 * Math.min(inn, out));
    }
  }
  const flash = i > 0 && t < p.hook.until ? Math.max(0, 0.55 - local * 5) : 0;
  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#000" }}>
      <AbsoluteFill
        style={{
          transform: `scale(${push + punch + emph})`,
          filter: blur > 0.2 ? `blur(${blur}px)` : undefined,
        }}
      >
        <OffthreadVideo
          src={resolveAsset(p.videoSrc)}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      </AbsoluteFill>
      {/* soft vignette keeps text readable on bright shots */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse at center, rgba(0,0,0,0) 55%, rgba(10,12,30,0.45) 100%)",
        }}
      />
      {flash > 0 && <AbsoluteFill style={{ backgroundColor: `rgba(255,255,255,${flash})` }} />}
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------
// Hook title (cold open)
// ---------------------------------------------------------------------------
const Hook: React.FC<{ hook: JirafikVlogProps["hook"] }> = ({ hook }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pop = spring({ frame, fps, config: { damping: 11, stiffness: 160 } });
  const line2 = spring({ frame: frame - 7, fps, config: { damping: 10, stiffness: 180 } });
  const outStart = hook.until * fps - 8;
  const out = interpolate(frame, [outStart, outStart + 8], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill style={{ alignItems: "center", top: 470 }}>
      <div
        style={{
          transform: `scale(${(0.6 + 0.4 * pop) * (0.85 + 0.15 * out)})`,
          opacity: out,
          background: "rgba(20,24,58,0.92)",
          borderLeft: `14px solid ${ORANGE}`,
          borderRadius: 30,
          padding: "34px 56px 40px",
          textAlign: "center",
          boxShadow: "0 18px 50px rgba(0,0,0,0.45)",
        }}
      >
        <div style={{ fontFamily: BODY, fontWeight: 700, fontSize: 38, letterSpacing: 4, color: ORANGE }}>
          {hook.tag}
        </div>
        <div style={{ fontFamily: HEAD, fontWeight: 700, fontSize: 92, color: "#fff", lineHeight: 1.1, marginTop: 8 }}>
          {hook.line1}
        </div>
        <div
          style={{
            fontFamily: HEAD,
            fontWeight: 700,
            fontSize: 104,
            color: ORANGE,
            lineHeight: 1.1,
            transform: `translateY(${(1 - line2) * 40}px) scale(${0.7 + 0.3 * line2})`,
            opacity: Math.min(1, line2 * 1.5),
          }}
        >
          {hook.line2}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------
// Captions: pages of up to 3 words, active word orange + bounce
// ---------------------------------------------------------------------------
type Page = { words: VlogWord[]; start: number; end: number };
const buildPages = (words: VlogWord[]): Page[] => {
  const pages: Page[] = [];
  let cur: VlogWord[] = [];
  const flush = () => {
    if (cur.length) pages.push({ words: cur, start: cur[0].start, end: cur[cur.length - 1].end });
    cur = [];
  };
  words.forEach((w, i) => {
    const prev = words[i - 1];
    if (cur.length && (cur.length >= 3 || (prev && w.start - prev.end > 0.35))) flush();
    cur.push(w);
    if (/[.,:!?…]$/.test(w.text)) flush();
  });
  flush();
  for (let i = 0; i < pages.length - 1; i++) {
    if (pages[i + 1].start - pages[i].end < 0.5) pages[i].end = pages[i + 1].start;
  }
  return pages;
};

const Captions: React.FC<{ words: VlogWord[]; from: number }> = ({ words, from }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const pages = React.useMemo(() => buildPages(words.filter((w) => w.start >= from)), [words, from]);
  // Latest page that has started, so the next page replaces the current one
  // exactly on its first word instead of after the linger window.
  const page = [...pages].reverse().find((pg) => t >= pg.start - 0.04);
  if (!page || t >= page.end + 0.12) return null;
  const pf = Math.round((t - page.start) * fps);
  const pagePop = spring({ frame: pf, fps, config: { damping: 12, stiffness: 220 } });
  return (
    <AbsoluteFill style={{ justifyContent: "flex-start", alignItems: "center", top: 1290 }}>
      <div
        style={{
          transform: `scale(${0.82 + 0.18 * pagePop})`,
          background: "rgba(20,24,58,0.86)",
          borderRadius: 22,
          padding: "16px 30px 20px",
          maxWidth: 960,
          textAlign: "center",
          boxShadow: "0 10px 30px rgba(0,0,0,0.35)",
        }}
      >
        {page.words.map((w, i) => {
          const active = t >= w.start - 0.04 && (i === page.words.length - 1 ? true : t < page.words[i + 1].start - 0.04);
          const wf = Math.round((t - w.start) * fps);
          const bounce = active ? spring({ frame: wf, fps, config: { damping: 9, stiffness: 260 } }) : 1;
          const spoken = t >= w.start - 0.04;
          return (
            <span
              key={i}
              style={{
                display: "inline-block",
                margin: "0 12px",
                fontFamily: BODY,
                fontWeight: 800,
                fontSize: 74,
                lineHeight: 1.15,
                color: active ? ORANGE : spoken ? "#fff" : "rgba(255,255,255,0.55)",
                transform: active ? `scale(${1 + 0.12 * (1 - Math.abs(1 - bounce))})` : undefined,
              }}
            >
              {w.text.replace(/[,:]$/, "")}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------
// Stickers
// ---------------------------------------------------------------------------
const Sticker: React.FC<{ s: VlogSticker; index: number }> = ({ s, index }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const inn = spring({ frame, fps, config: { damping: 10, stiffness: 200 } });
  const total = s.duration * fps;
  const out = interpolate(frame, [total - 7, total], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const tilt = (index % 2 === 0 ? -1 : 1) * 4;
  if (s.variant === "avatar") {
    const slide = interpolate(inn, [0, 1], [420, 0]);
    return (
      <AbsoluteFill>
        <div
          style={{
            position: "absolute",
            right: 50,
            top: 760,
            transform: `translateX(${slide + (1 - out) * 420}px) rotate(${-8 + 8 * inn}deg)`,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          <Img
            src={staticFile("jirafik/avatar.png")}
            style={{ width: 300, height: 300, borderRadius: "50%", border: `10px solid ${ORANGE}`, boxShadow: "0 14px 40px rgba(0,0,0,0.45)" }}
          />
          <div
            style={{
              marginTop: -26,
              background: ORANGE,
              color: NAVY,
              fontFamily: BODY,
              fontWeight: 800,
              fontSize: 46,
              padding: "8px 26px",
              borderRadius: 16,
            }}
          >
            {s.text}
          </div>
        </div>
      </AbsoluteFill>
    );
  }
  const orange = s.variant !== "navy";
  return (
    <AbsoluteFill style={{ alignItems: "center", top: 330 }}>
      <div
        style={{
          transform: `scale(${(0.4 + 0.6 * inn) * (0.6 + 0.4 * out)}) rotate(${tilt * inn}deg)`,
          opacity: out,
          background: orange ? ORANGE : NAVY,
          color: orange ? NAVY : "#fff",
          border: orange ? "none" : `6px solid ${ORANGE}`,
          fontFamily: BODY,
          fontWeight: 800,
          fontSize: 70,
          padding: "18px 44px",
          borderRadius: 26,
          boxShadow: "0 16px 40px rgba(0,0,0,0.4)",
          whiteSpace: "nowrap",
        }}
      >
        {s.text}
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------
// Progress bar
// ---------------------------------------------------------------------------
const Progress: React.FC<{ total: number }> = ({ total }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const w = Math.min(1, frame / (total * fps));
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 12, background: "rgba(20,24,58,0.55)" }} />
      <div style={{ position: "absolute", top: 0, left: 0, height: 12, width: `${w * 100}%`, background: ORANGE, boxShadow: `0 0 14px ${ORANGE}` }} />
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------
// End card
// ---------------------------------------------------------------------------
const EndCard: React.FC<{ card: JirafikVlogProps["endCard"] }> = ({ card }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const fadeIn = interpolate(frame, [0, 9], [0, 1], { extrapolateRight: "clamp" });
  const av = spring({ frame: frame - 3, fps, config: { damping: 10, stiffness: 140 } });
  const item = (delay: number) => {
    const s = spring({ frame: frame - delay, fps, config: { damping: 14, stiffness: 170 } });
    return { opacity: s, transform: `translateY(${(1 - s) * 40}px)` };
  };
  const line = interpolate(frame, [12, 24], [0, 140], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ backgroundColor: NAVY, opacity: fadeIn, alignItems: "center", paddingTop: 300 }}>
      <Img
        src={staticFile("jirafik/avatar.png")}
        style={{
          width: 540,
          height: 540,
          borderRadius: "50%",
          border: `16px solid ${ORANGE}`,
          transform: `scale(${0.5 + 0.5 * av}) rotate(${(1 - av) * -12}deg)`,
        }}
      />
      <div style={{ ...item(8), fontFamily: HEAD, fontWeight: 700, fontSize: 100, color: "#fff", marginTop: 46 }}>
        Жирафик Трафик
      </div>
      <div style={{ width: line, height: 9, background: ORANGE, marginTop: 14, borderRadius: 5 }} />
      <div style={{ ...item(13), fontFamily: HEAD, fontWeight: 700, fontSize: 60, color: GOLD, marginTop: 30, textAlign: "center", lineHeight: 1.25 }}>
        Зарабатываю на банках.
        <br />
        Учу тебя тому же.
      </div>
      <div style={{ ...item(18), fontFamily: BODY, fontWeight: 700, fontSize: 50, color: "#fff", marginTop: 60 }}>
        {card.question}
      </div>
      <div style={{ ...item(22), fontFamily: BODY, fontWeight: 500, fontSize: 42, color: LIGHT, marginTop: 70, textAlign: "center", lineHeight: 1.5 }}>
        {card.handles.map((h) => (
          <div key={h}>{h}</div>
        ))}
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------
export const JirafikVlog: React.FC<JirafikVlogProps> = (p) => {
  const { fps } = useVideoConfig();
  const vf = Math.round(p.videoDuration * fps);
  const f = (s: number) => Math.round(s * fps);
  return (
    <AbsoluteFill style={{ backgroundColor: NAVY }}>
      <Sequence durationInFrames={vf}>
        <MovingVideo {...p} />
        {p.stickers.map((s, i) => (
          <Sequence key={`st${i}`} from={f(s.start)} durationInFrames={f(s.duration)}>
            <Sticker s={s} index={i} />
            <Audio src={staticFile("jirafik/pop.wav")} volume={0.35} />
          </Sequence>
        ))}
        <Captions words={p.words} from={p.captionsFrom} />
        <Sequence durationInFrames={f(p.hook.until)}>
          <Hook hook={p.hook} />
        </Sequence>
        <Progress total={p.videoDuration} />
      </Sequence>
      {p.whooshAt.map((t, i) => (
        <Sequence key={`wh${i}`} from={Math.max(0, f(t - 0.18))} durationInFrames={f(0.4)}>
          <Audio src={staticFile("jirafik/whoosh.wav")} volume={0.22} />
        </Sequence>
      ))}
      <Sequence from={vf - f(0.3)}>
        <EndCard card={p.endCard} />
      </Sequence>
    </AbsoluteFill>
  );
};
