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
const TITLE = "Oswald, Inter, sans-serif";

export type VlogWord = { text: string; start: number; end: number; key?: boolean };
export type VlogSticker = {
  text: string;
  start: number;
  duration: number;
  variant?: "orange" | "navy" | "avatar";
};

export type VlogInsert = {
  src: string; // file in public/
  start: number;
  duration: number;
  label?: string;
  width?: number; // card width, px
  aspect?: number; // width / height
};

export type VlogReveal = {
  start: number;
  duration: number;
  title: string;
  items: { src: string; amount: number }[];
  caption?: string;
  fadeOut?: boolean; // false keeps the reveal on screen to the last frame
  typeTitleSeconds?: number; // type the title out letter by letter (pairs with a typing SFX)
  counterDelay?: number; // seconds before the counter starts climbing
  climbSeconds?: number; // how long the counter climbs (pairs with a gauge SFX)
  cardWidth?: number; // reveal card width, px (wider for landscape screenshots)
};

export type JirafikVlogProps = {
  videoSrc: string;
  videoDuration: number;
  cuts: number[];
  whooshAt: number[];
  emphasis: { start: number; end: number }[];
  words: VlogWord[];
  stickers: VlogSticker[];
  hook: {
    tag: string;
    line1: string;
    line2: string;
    until: number;
    teaser?: string;
    // optional result flash before the title: shows the payoff first
    flash?: { value: string; label: string; until: number };
  };
  captionStyle?: "plate" | "bold" | "word";
  // "lower" hook: short two-line condensed title in the lower third that holds
  // while the speaker says it (reference style); default is the centred card.
  hookStyle?: "card" | "lower";
  sfx?: { at: number; src: string; volume?: number }[];
  inserts?: VlogInsert[];
  // list videos: "№1 Альфа-Банк · 14 000 ₽" chip at the top while that item is discussed
  chapters?: { start: number; end: number; kicker: string; title: string; value?: string }[];
  // one-off sum card, e.g. 14 000 + 9 000 + 20 000 = 43 000 ₽
  calc?: { start: number; end: number; parts: string[]; total: string };
  // call to action pill at the end
  cta?: { start: number; end: number; label: string; handle: string };
  // giant words placed BEHIND the speaker (needs personSrc: transparent webm cut-out of the same video)
  personSrc?: string;
  bigWords?: {
    start: number;
    end: number;
    lines: string[]; // stacked, e.g. ["НИ","КО","ГДА"]; lines pop in one after another
    color?: string;
    top?: number; // px from frame top (un-zoomed); place so the head overlaps the text
    align?: "left" | "center";
    size?: number;
  }[];
  // plates on light footage: "light" = white cards, "dark" = navy cards
  plateTheme?: "light" | "dark";
  reveal?: VlogReveal;
  captionsFrom: number;
  endCard: { seconds: number; question: string; handles: string[] };
  // Camera feel. Defaults are the calm look the brand asked for; raise them
  // only for deliberately energetic edits.
  motion?: {
    push?: number; // total slow push-in per shot (0.04 = 4 %)
    alternate?: boolean; // alternate push-in / pull-out between shots
    punch?: number; // extra zoom kick on each cut
    blur?: number; // motion blur on each cut, px
    flash?: boolean; // white flash on cold-open cuts
    emphasisZoom?: number; // zoom on emphasis words
    vignette?: boolean; // dark edge vignette (off for bright footage)
    jumpZoom?: number; // static punch-in on every other shot (reference "jump zoom"), e.g. 0.12
  };
};

const DEFAULT_MOTION = {
  push: 0.04,
  alternate: false,
  punch: 0,
  blur: 0,
  flash: false,
  emphasisZoom: 0.05,
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
const BigWord: React.FC<{ w: NonNullable<JirafikVlogProps["bigWords"]>[number] }> = ({ w }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const total = (w.end - w.start) * fps;
  const out = interpolate(frame, [total - 5, total], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const longest = Math.max(...w.lines.map((l) => l.length));
  const size = w.size ?? Math.min(470, Math.floor(1500 / Math.max(longest, 2)));
  const left = (w.align ?? "left") === "left";
  const step = Math.max(2, Math.min(5, Math.floor((total * 0.35) / Math.max(w.lines.length, 1))));
  return (
    <AbsoluteFill
      style={{
        alignItems: left ? "flex-start" : "center",
        justifyContent: "flex-start",
        paddingTop: w.top ?? 520,
        paddingLeft: left ? 50 : 0,
        opacity: out,
      }}
    >
      {w.lines.map((l, i) => {
        const shown = frame >= i * step;
        const s = spring({ frame: frame - i * step, fps, config: { damping: 14, stiffness: 260 } });
        return (
          <div
            key={i}
            style={{
              fontFamily: TITLE,
              fontWeight: 700,
              fontSize: size,
              lineHeight: 0.86,
              color: w.color ?? ORANGE,
              textTransform: "uppercase",
              letterSpacing: "-0.01em",
              opacity: shown ? 1 : 0,
              transform: `scale(${1.25 - 0.25 * s})`,
              transformOrigin: left ? "left center" : "center",
              whiteSpace: "nowrap",
            }}
          >
            {l}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

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
  const m = { ...DEFAULT_MOTION, vignette: true, ...p.motion };
  // Ease the push so a shot starts and settles gently instead of drifting linearly.
  const prog = Math.min(local / shotLen, 1);
  const eased = prog * prog * (3 - 2 * prog);
  const pullOut = m.alternate && i % 2 === 1;
  const jump = m.jumpZoom && i % 2 === 1 ? m.jumpZoom : 0;
  const push = (pullOut ? 1.01 + m.push * (1 - eased) : 1.01 + m.push * eased) + jump;
  const punchT = Math.min(local / 0.22, 1);
  const punch = i === 0 ? 0 : m.punch * Math.pow(1 - punchT, 2);
  const blur = i === 0 ? 0 : m.blur * Math.pow(1 - punchT, 2);
  let emph = 0;
  for (const e of p.emphasis) {
    if (t >= e.start && t <= e.end + 0.45) {
      const inn = easeOut((t - e.start) / 0.35);
      const out = 1 - easeOut((t - e.end) / 0.45);
      emph = Math.max(emph, m.emphasisZoom * Math.min(inn, out));
    }
  }
  const flash = m.flash && i > 0 && t < p.hook.until ? Math.max(0, 0.55 - local * 5) : 0;
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
        {p.personSrc &&
          (p.bigWords ?? []).map((w, i) => {
            const from = Math.round(w.start * fps);
            const dur = Math.round((w.end - w.start) * fps);
            return (
              <Sequence key={`bw${i}`} from={from} durationInFrames={dur}>
                <BigWord w={w} />
                <AbsoluteFill>
                  <OffthreadVideo
                    src={resolveAsset(p.personSrc!)}
                    startFrom={from}
                    transparent
                    muted
                    style={{ width: "100%", height: "100%", objectFit: "cover" }}
                  />
                </AbsoluteFill>
              </Sequence>
            );
          })}
      </AbsoluteFill>
      {/* soft vignette keeps text readable on bright shots */}
      {m.vignette && (
        <AbsoluteFill
          style={{
            background:
              "radial-gradient(ellipse at center, rgba(0,0,0,0) 55%, rgba(10,12,30,0.45) 100%)",
          }}
        />
      )}
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
  const pop = spring({ frame, fps, config: { damping: 12, stiffness: 180 } });
  const line2 = spring({ frame: frame - 6, fps, config: { damping: 10, stiffness: 170 } });
  const outStart = (hook.until - (hook.flash?.until ?? 0)) * fps - 8;
  const out = interpolate(frame, [outStart, outStart + 8], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const shadow = "0 6px 24px rgba(0,0,0,0.7), 0 0 3px rgba(0,0,0,0.9)";
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", opacity: out }}>
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at center, rgba(10,12,30,0.55) 0%, rgba(10,12,30,0) 65%)" }} />
      <div style={{ textAlign: "center", transform: `scale(${(0.7 + 0.3 * pop) * (0.9 + 0.1 * out)})` }}>
        <div style={{ fontFamily: BODY, fontWeight: 700, fontSize: 36, letterSpacing: 5, color: ORANGE, textShadow: shadow }}>
          {hook.tag}
        </div>
        <div style={{ fontFamily: BODY, fontWeight: 900, fontSize: 96, color: "#fff", textTransform: "uppercase", lineHeight: 1.0, marginTop: 10, textShadow: shadow }}>
          {hook.line1}
        </div>
        <div
          style={{
            fontFamily: HEAD,
            fontStyle: "italic",
            fontWeight: 700,
            fontSize: 140,
            color: ORANGE,
            lineHeight: 1.05,
            textShadow: `0 0 30px rgba(242,138,46,0.75), ${shadow}`,
            WebkitTextStroke: `5px ${NAVY}`,
            paintOrder: "stroke fill",
            transform: `translateY(${(1 - line2) * 40}px) scale(${0.7 + 0.3 * line2})`,
            opacity: Math.min(1, line2 * 1.5),
          }}
        >
          {hook.line2}
        </div>
        {hook.teaser && (
          <div
            style={{
              display: "inline-block",
              marginTop: 30,
              opacity: Math.min(1, Math.max(0, (frame - 12) / 6)),
              background: ORANGE,
              color: NAVY,
              fontFamily: BODY,
              fontWeight: 800,
              fontSize: 44,
              padding: "12px 30px",
              borderRadius: 40,
              boxShadow: "0 10px 30px rgba(0,0,0,0.35)",
            }}
          >
            {hook.teaser}
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------
// Lower hook: small italic kicker + two big condensed lines, held long enough to read
// ---------------------------------------------------------------------------
const HookLower: React.FC<{ hook: JirafikVlogProps["hook"] }> = ({ hook }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const l1 = spring({ frame, fps, config: { damping: 18, stiffness: 140 } });
  const l2 = spring({ frame: frame - 5, fps, config: { damping: 18, stiffness: 140 } });
  const kick = spring({ frame: frame - 10, fps, config: { damping: 20, stiffness: 120 } });
  const total = hook.until * fps;
  const out = interpolate(frame, [total - 10, total], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const shadow = "0 4px 18px rgba(0,0,0,0.45)";
  const line = (v: number): React.CSSProperties => ({
    fontFamily: TITLE,
    fontWeight: 700,
    fontSize: 132,
    lineHeight: 0.98,
    textTransform: "uppercase",
    textShadow: shadow,
    transform: `translateY(${(1 - v) * 50}px)`,
    opacity: Math.min(1, v * 1.3),
  });
  return (
    <AbsoluteFill style={{ opacity: out }}>
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(10,12,30,0) 45%, rgba(10,12,30,0.55) 100%)" }} />
      <div style={{ position: "absolute", left: 70, right: 70, bottom: 330 }}>
        {hook.teaser && (
          <div style={{ fontFamily: BODY, fontStyle: "italic", fontWeight: 600, fontSize: 40, color: "#fff", textShadow: shadow, opacity: kick, marginBottom: 6 }}>
            {hook.teaser}
          </div>
        )}
        <div style={{ ...line(l1), color: ORANGE }}>{hook.line1}</div>
        <div style={{ ...line(l2), color: "#fff" }}>{hook.line2}</div>
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------
// Hook flash: result first (big number stamps in), then the title takes over
// ---------------------------------------------------------------------------
const HookFlash: React.FC<{ flash: NonNullable<JirafikVlogProps["hook"]["flash"]> }> = ({ flash }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const stamp = spring({ frame, fps, config: { damping: 9, stiffness: 220 } });
  const total = flash.until * fps;
  const out = interpolate(frame, [total - 5, total], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ opacity: out }}>
      <AbsoluteFill style={{ backgroundColor: "rgba(20,24,58,0.72)" }} />
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
        <div
          style={{
            fontFamily: HEAD,
            fontWeight: 700,
            fontSize: 190,
            color: GOLD,
            transform: `scale(${1.7 - 0.7 * stamp}) rotate(${(1 - stamp) * -6}deg)`,
            textShadow: "0 10px 40px rgba(0,0,0,0.6)",
          }}
        >
          {flash.value}
        </div>
        <div style={{ fontFamily: BODY, fontWeight: 800, fontSize: 52, color: "#fff", textTransform: "uppercase", opacity: stamp }}>
          {flash.label}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------
// Captions: pages of up to 3 words, active word orange + bounce
// ---------------------------------------------------------------------------
type Page = { words: VlogWord[]; start: number; end: number };
const buildPages = (words: VlogWord[], maxWords = 3): Page[] => {
  const pages: Page[] = [];
  let cur: VlogWord[] = [];
  const flush = () => {
    if (cur.length) pages.push({ words: cur, start: cur[0].start, end: cur[cur.length - 1].end });
    cur = [];
  };
  words.forEach((w, i) => {
    const prev = words[i - 1];
    if (cur.length && (cur.length >= maxWords || (w.key && cur.length > 0) || (prev?.key ?? false) || (prev && w.start - prev.end > 0.35))) flush();
    cur.push(w);
    if (/[.,:!?…]$/.test(w.text)) flush();
  });
  flush();
  for (let i = 0; i < pages.length - 1; i++) {
    if (pages[i + 1].start - pages[i].end < 0.5) pages[i].end = pages[i + 1].start;
  }
  return pages;
};

const BOLD_SHADOW = "0 4px 14px rgba(0,0,0,0.75), 0 0 3px rgba(0,0,0,0.9)";

const Captions: React.FC<{ words: VlogWord[]; from: number; variant?: "plate" | "bold" | "word" }> = ({
  words,
  from,
  variant = "plate",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const pages = React.useMemo(
    () => buildPages(words.filter((w) => w.start >= from), variant === "word" ? 1 : variant === "bold" ? 2 : 3),
    [words, from, variant],
  );
  // Latest page that has started, so the next page replaces the current one
  // exactly on its first word instead of after the linger window.
  const page = [...pages].reverse().find((pg) => t >= pg.start - 0.04);
  if (!page || t >= page.end + 0.12) return null;
  const pf = Math.round((t - page.start) * fps);
  const pagePop = spring({ frame: pf, fps, config: { damping: 12, stiffness: 220 } });
  if (variant === "word") {
    // One word at a time; key words sit on a brand-orange box (reference style).
    const w = page.words[page.words.length - 1];
    const text = w.text.replace(/[,:.!?…]$/, "");
    const wf = Math.round((t - w.start) * fps);
    const bounce = spring({ frame: wf, fps, config: { damping: 11, stiffness: 240 } });
    const scale = 0.8 + 0.2 * bounce;
    return (
      <AbsoluteFill style={{ alignItems: "center", top: 1190 }}>
        {w.key ? (
          <span
            style={{
              transform: `scale(${scale * 1.04})`,
              background: ORANGE,
              color: NAVY,
              fontFamily: BODY,
              fontWeight: 800,
              fontSize: 66,
              lineHeight: 1.15,
              padding: "2px 18px 6px",
              borderRadius: 6,
            }}
          >
            {text}
          </span>
        ) : (
          <span
            style={{
              transform: `scale(${scale})`,
              color: "#fff",
              fontFamily: BODY,
              fontStyle: "italic",
              fontWeight: 800,
              fontSize: 62,
              lineHeight: 1.15,
              textShadow: "0 2px 10px rgba(0,0,0,0.45)",
            }}
          >
            {text}
          </span>
        )}
      </AbsoluteFill>
    );
  }
  if (variant === "bold") {
    return (
      <AbsoluteFill style={{ justifyContent: "flex-start", alignItems: "center", top: 1250 }}>
        <div style={{ transform: `scale(${0.85 + 0.15 * pagePop})`, maxWidth: 980, textAlign: "center", lineHeight: 1.05 }}>
          {page.words.map((w, i) => {
            const spoken = t >= w.start - 0.04;
            if (!spoken) return null; // words appear as they are said
            const wf = Math.round((t - w.start) * fps);
            const pop = spring({ frame: wf, fps, config: { damping: 10, stiffness: 260 } });
            const text = w.text.replace(/[,:.]$/, "");
            return (
              <span
                key={i}
                style={{
                  display: "inline-block",
                  margin: "0 14px",
                  transform: `scale(${0.6 + 0.4 * pop}) translateY(${(1 - pop) * 20}px)`,
                  ...(w.key
                    ? {
                        fontFamily: HEAD,
                        fontStyle: "italic",
                        fontWeight: 700,
                        fontSize: 124,
                        color: ORANGE,
                        WebkitTextStroke: `6px ${NAVY}`,
                        paintOrder: "stroke fill",
                      }
                    : { fontFamily: BODY, fontWeight: 900, fontSize: 82, color: "#fff", textTransform: "uppercase" as const }),
                  textShadow: BOLD_SHADOW,
                }}
              >
                {text}
              </span>
            );
          })}
        </div>
      </AbsoluteFill>
    );
  }
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
  const inn = spring({ frame, fps, config: { damping: 16, stiffness: 170 } });
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
// Photo insert: framed card that springs in, drifts slowly, slides out
// ---------------------------------------------------------------------------
const PhotoInsert: React.FC<{ ins: VlogInsert; index: number }> = ({ ins, index }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const inn = spring({ frame, fps, config: { damping: 15, stiffness: 150 } });
  const total = ins.duration * fps;
  const out = interpolate(frame, [total - 8, total], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const w = ins.width ?? 640;
  const h = w / (ins.aspect ?? 0.8);
  const tilt = (index % 2 === 0 ? -1 : 1) * 3;
  const drift = 1 + 0.05 * (frame / total);
  return (
    <AbsoluteFill style={{ alignItems: "center", top: 250 }}>
      <div
        style={{
          transform: `translateY(${(1 - inn) * 120 + (1 - out) * -60}px) scale(${0.85 + 0.15 * inn}) rotate(${tilt * inn}deg)`,
          opacity: Math.min(inn * 1.4, out),
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
        }}
      >
        <div
          style={{
            width: w,
            height: h,
            borderRadius: 28,
            overflow: "hidden",
            border: "10px solid #fff",
            boxShadow: "0 24px 60px rgba(0,0,0,0.5)",
          }}
        >
          <Img src={staticFile(ins.src)} style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${drift})` }} />
        </div>
        {ins.label && (
          <div
            style={{
              marginTop: -30,
              background: ORANGE,
              color: NAVY,
              fontFamily: BODY,
              fontWeight: 800,
              fontSize: 52,
              padding: "10px 32px",
              borderRadius: 18,
              boxShadow: "0 10px 26px rgba(0,0,0,0.35)",
            }}
          >
            {ins.label}
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------
// Reveal: payout screenshots fan in one by one, counter climbs to the last
// ---------------------------------------------------------------------------
const fmt = (n: number) => Math.round(n).toLocaleString("ru-RU").replace(/,/g, " ");
const Reveal: React.FC<{ r: VlogReveal }> = ({ r }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const dim = interpolate(frame, [0, 10], [0, 1], { extrapolateRight: "clamp" });
  const step = Math.round(((r.duration - 1.2) / r.items.length) * fps);
  const shown = Math.min(r.items.length - 1, Math.floor(frame / step));
  const prev = shown > 0 ? r.items[shown - 1].amount : 0;
  const cur = r.items[shown].amount;
  const delayF = (r.counterDelay ?? 0) * fps;
  const climbF = r.climbSeconds ? r.climbSeconds * fps : step * 0.8;
  const climb = easeOut((frame - shown * step - delayF) / climbF);
  const titleChars = r.typeTitleSeconds
    ? Math.floor(r.title.length * Math.min(1, frame / (r.typeTitleSeconds * fps)))
    : r.title.length;
  const value = prev + (cur - prev) * climb;
  const last = shown === r.items.length - 1;
  const total = r.duration * fps;
  const out =
    r.fadeOut === false
      ? 1
      : interpolate(frame, [total - 8, total], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ opacity: out }}>
      <AbsoluteFill style={{ backgroundColor: `rgba(20,24,58,${0.82 * dim})` }} />
      <AbsoluteFill style={{ alignItems: "center", top: 150 }}>
        <div style={{ fontFamily: BODY, fontWeight: 700, fontSize: 44, color: ORANGE, letterSpacing: 3, opacity: dim, textAlign: "center", maxWidth: 980 }}>
          {r.title.slice(0, titleChars)}
          <span style={{ opacity: 0 }}>{r.title.slice(titleChars)}</span>
        </div>
        <div
          style={{
            fontFamily: HEAD,
            fontWeight: 700,
            fontSize: 150,
            lineHeight: 1.1,
            color: last && climb > 0.98 ? GOLD : "#fff",
            transform: `scale(${last && climb > 0.98 ? 1.06 : 1})`,
            opacity: dim,
          }}
        >
          {fmt(value)} ₽
        </div>
        {r.caption && (
          <div style={{ fontFamily: BODY, fontWeight: 600, fontSize: 40, color: LIGHT, opacity: dim * 0.9 }}>{r.caption}</div>
        )}
      </AbsoluteFill>
      {r.items.map((it, i) => {
        const f = frame - i * step;
        if (f < 0) return null;
        const s = spring({ frame: f, fps, config: { damping: 14, stiffness: 160 } });
        const x = (i - (r.items.length - 1) / 2) * 250;
        const rot = (i - (r.items.length - 1) / 2) * 7;
        return (
          <AbsoluteFill key={i} style={{ alignItems: "center", top: 640 }}>
            <Img
              src={staticFile(it.src)}
              style={{
                width: r.cardWidth ?? (r.items.length === 1 ? 640 : 520),
                borderRadius: 26,
                border: i === shown ? `8px solid ${ORANGE}` : "8px solid #fff",
                boxShadow: "0 24px 60px rgba(0,0,0,0.55)",
                transform: `translate(${x * s}px, ${(1 - s) * 500}px) rotate(${rot * s}deg) scale(${i === shown ? 1.04 : 0.94})`,
                zIndex: i,
              }}
            />
          </AbsoluteFill>
        );
      })}
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------
// Chapter chip (list videos)
// ---------------------------------------------------------------------------
const Chapter: React.FC<{ c: NonNullable<JirafikVlogProps["chapters"]>[number]; light?: boolean }> = ({ c, light }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const inn = spring({ frame, fps, config: { damping: 16, stiffness: 160 } });
  const total = (c.end - c.start) * fps;
  const out = interpolate(frame, [total - 8, total], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill>
      <div
        style={{
          position: "absolute",
          left: 60,
          top: 150,
          opacity: Math.min(inn, out),
          transform: `translateX(${(1 - inn) * -80}px)`,
          display: "flex",
          alignItems: "stretch",
          borderRadius: 18,
          overflow: "hidden",
          boxShadow: light ? "0 10px 26px rgba(20,24,58,0.18)" : "0 12px 30px rgba(0,0,0,0.35)",
        }}
      >
        <div style={{ background: ORANGE, color: light ? "#fff" : NAVY, fontFamily: TITLE, fontWeight: 700, fontSize: 64, padding: "6px 22px", display: "flex", alignItems: "center" }}>
          {c.kicker}
        </div>
        <div style={{ background: light ? "rgba(255,255,255,0.94)" : "rgba(20,24,58,0.92)", padding: "10px 24px 12px" }}>
          <div style={{ fontFamily: BODY, fontWeight: 800, fontSize: 46, color: light ? NAVY : "#fff", lineHeight: 1.1 }}>{c.title}</div>
          {c.value && <div style={{ fontFamily: BODY, fontWeight: 700, fontSize: 36, color: ORANGE, lineHeight: 1.2 }}>{c.value}</div>}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------
// Sum card: parts appear one by one, then the total
// ---------------------------------------------------------------------------
const Calc: React.FC<{ c: NonNullable<JirafikVlogProps["calc"]>; light?: boolean }> = ({ c, light }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const total = (c.end - c.start) * fps;
  const out = interpolate(frame, [total - 8, total], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const card = spring({ frame, fps, config: { damping: 16, stiffness: 160 } });
  const step = 7;
  const totalIn = spring({ frame: frame - step * c.parts.length - 4, fps, config: { damping: 10, stiffness: 200 } });
  return (
    <AbsoluteFill style={{ alignItems: "center", top: 300, opacity: out }}>
      <div
        style={{
          transform: `scale(${0.85 + 0.15 * card})`,
          opacity: card,
          background: light ? "rgba(255,255,255,0.95)" : "rgba(20,24,58,0.94)",
          border: light ? "none" : `5px solid ${ORANGE}`,
          borderRadius: 28,
          padding: "28px 40px 32px",
          textAlign: "center",
          boxShadow: light ? "0 14px 34px rgba(20,24,58,0.2)" : "0 20px 50px rgba(0,0,0,0.45)",
        }}
      >
        <div style={{ display: "flex", gap: 16, alignItems: "center", justifyContent: "center", fontFamily: BODY, fontWeight: 800, fontSize: 50, color: light ? NAVY : "#fff" }}>
          {c.parts.map((p, i) => {
            const v = spring({ frame: frame - i * step, fps, config: { damping: 14, stiffness: 200 } });
            return (
              <React.Fragment key={i}>
                {i > 0 && <span style={{ color: ORANGE, opacity: v }}>+</span>}
                <span style={{ opacity: v, transform: `translateY(${(1 - v) * 20}px)`, display: "inline-block" }}>{p}</span>
              </React.Fragment>
            );
          })}
        </div>
        <div style={{ fontFamily: TITLE, fontWeight: 700, fontSize: 130, color: light ? ORANGE : GOLD, lineHeight: 1.1, marginTop: 8, opacity: totalIn, transform: `scale(${0.6 + 0.4 * totalIn})` }}>
          = {c.total}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------
// CTA pill
// ---------------------------------------------------------------------------
const Cta: React.FC<{ c: NonNullable<JirafikVlogProps["cta"]>; light?: boolean }> = ({ c, light }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const inn = spring({ frame, fps, config: { damping: 12, stiffness: 170 } });
  return (
    <AbsoluteFill style={{ alignItems: "center", top: 330 }}>
      <div
        style={{
          transform: `scale(${0.7 + 0.3 * inn})`,
          opacity: inn,
          background: light ? "rgba(255,255,255,0.95)" : "rgba(20,24,58,0.94)",
          border: light ? "none" : `5px solid ${ORANGE}`,
          borderRadius: 26,
          padding: "18px 40px 22px",
          textAlign: "center",
          boxShadow: light ? "0 12px 30px rgba(20,24,58,0.2)" : "0 16px 40px rgba(0,0,0,0.4)",
        }}
      >
        <div style={{ fontFamily: BODY, fontWeight: 700, fontSize: 40, color: light ? NAVY : LIGHT }}>{c.label}</div>
        <div style={{ fontFamily: TITLE, fontWeight: 700, fontSize: 92, color: ORANGE, lineHeight: 1.1 }}>{c.handle}</div>
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
            {p.sfx === undefined && <Audio src={staticFile("jirafik/pop.wav")} volume={0.35} />}
          </Sequence>
        ))}
        {(p.inserts ?? []).map((ins, i) => (
          <Sequence key={`in${i}`} from={f(ins.start)} durationInFrames={f(ins.duration)}>
            <PhotoInsert ins={ins} index={i} />
            {p.sfx === undefined && <Audio src={staticFile("jirafik/whoosh.wav")} volume={0.12} />}
          </Sequence>
        ))}
        {(p.chapters ?? []).map((c, i) => (
          <Sequence key={`ch${i}`} from={f(c.start)} durationInFrames={f(c.end - c.start)}>
            <Chapter c={c} light={p.plateTheme === "light"} />
          </Sequence>
        ))}
        {p.calc && (
          <Sequence from={f(p.calc.start)} durationInFrames={f(p.calc.end - p.calc.start)}>
            <Calc c={p.calc} light={p.plateTheme === "light"} />
          </Sequence>
        )}
        {p.cta && (
          <Sequence from={f(p.cta.start)} durationInFrames={f(p.cta.end - p.cta.start)}>
            <Cta c={p.cta} light={p.plateTheme === "light"} />
          </Sequence>
        )}
        <Captions words={p.words} from={p.captionsFrom} variant={p.captionStyle} />
        {p.reveal && (
          <Sequence from={f(p.reveal.start)} durationInFrames={f(p.reveal.duration)}>
            <Reveal r={p.reveal} />
            {(p.sfx === undefined ? p.reveal.items : []).map((_, i) => (
              <Sequence key={`dg${i}`} from={Math.round(i * ((p.reveal!.duration - 1.2) / p.reveal!.items.length) * fps)} durationInFrames={f(0.5)}>
                <Audio src={staticFile("jirafik/ding.wav")} volume={0.18 + 0.06 * i} />
              </Sequence>
            ))}
          </Sequence>
        )}
        {p.hook.flash && (
          <Sequence durationInFrames={f(p.hook.flash.until)}>
            <HookFlash flash={p.hook.flash} />
          </Sequence>
        )}
        <Sequence from={f(p.hook.flash?.until ?? 0)} durationInFrames={f(p.hook.until - (p.hook.flash?.until ?? 0))}>
          {p.hookStyle === "lower" ? <HookLower hook={p.hook} /> : <Hook hook={p.hook} />}
        </Sequence>
        <Progress total={p.videoDuration} />
      </Sequence>
      {(p.sfx ?? []).map((x, i) => (
        <Sequence key={`sfx${i}`} from={Math.max(0, f(x.at))} durationInFrames={f(1.2)}>
          <Audio src={staticFile(x.src)} volume={x.volume ?? 0.3} />
        </Sequence>
      ))}
      {p.whooshAt.map((t, i) => (
        <Sequence key={`wh${i}`} from={Math.max(0, f(t - 0.18))} durationInFrames={f(0.4)}>
          <Audio src={staticFile("jirafik/whoosh.wav")} volume={0.22} />
        </Sequence>
      ))}
      {p.endCard.seconds > 0 && (
        <Sequence from={vf - f(0.3)}>
          <EndCard card={p.endCard} />
        </Sequence>
      )}
    </AbsoluteFill>
  );
};
