import React from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";

// Meme-style edit (after a reference Ilya sent): big red stacked hook words with an emoji, a white text card with a
// handwritten word and lines that come out of a blur, full-screen photo inserts with coloured words, small grey
// subtitles. Rendered on a transparent background and laid over the HDR video with ffmpeg.
export type MemeWord = { t: number; text: string };
export type MemeEditProps = {
  duration: number;
  hook: { words: { t: number; text: string; size: number }[]; end: number; emoji?: { t: number; char: string } };
  cards: { start: number; end: number; script: { t: number; text: string }; lines: MemeWord[] }[];
  photos: { start: number; end: number; src: string }[];
  colorWords: { start: number; end: number; text: string; color: string; top?: number; size?: number }[];
  subs: { start: number; end: number; text: string; top?: number }[];
  scripts: { start: number; end: number; text: string; color?: string; top?: number }[];
  emojis: { t: number; end: number; char: string; x: number; y: number; size: number }[];
};

const RED = "#E3191C";
const blurIn = (f: number, fps: number, dur = 0.28) => {
  const p = interpolate(f, [0, dur * fps], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return { opacity: p, filter: `blur(${(1 - p) * 16}px)` };
};
const fadeOut = (f: number, end: number, fps: number, d = 0.12) =>
  interpolate(f, [(end - d) * fps, end * fps], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

export const MemeEdit: React.FC<MemeEditProps> = (p) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const at = (s: number) => frame - s * fps;
  return (
    <AbsoluteFill style={{ backgroundColor: "transparent" }}>
      <style>{`@font-face{font-family:'Marck';src:url(${staticFile("jirafik/MarckScript-cyr.woff2")}) format('woff2');unicode-range:U+0400-04FF;}
@font-face{font-family:'Marck';src:url(${staticFile("jirafik/MarckScript-lat.woff2")}) format('woff2');}`}</style>

      {/* photo inserts (full screen, hard cuts) */}
      {p.photos.map((ph, i) =>
        t >= ph.start && t < ph.end ? (
          <AbsoluteFill key={`ph${i}`}>
            <Img src={staticFile(ph.src)} style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${1 + (t - ph.start) * 0.025})` }} />
          </AbsoluteFill>
        ) : null,
      )}

      {/* white text cards */}
      {p.cards.map((c, i) => {
        if (t < c.start || t >= c.end) return null;
        const inn = interpolate(at(c.start), [0, 0.12 * fps], [0, 1], { extrapolateRight: "clamp" });
        const out = fadeOut(frame, c.end, fps, 0.25);
        return (
          <AbsoluteFill key={`c${i}`} style={{ backgroundColor: "#F2F2F2", opacity: Math.min(inn, out), alignItems: "center", paddingTop: 560 }}>
            {t >= c.script.t && (
              <div style={{ fontFamily: "Marck, cursive", fontSize: 190, color: "#111", lineHeight: 1, ...blurIn(at(c.script.t), fps, 0.35),
                transform: `scale(${interpolate(at(c.script.t), [0, 0.35 * fps], [0.8, 1], { extrapolateRight: "clamp" })})` }}>
                {c.script.text}
              </div>
            )}
            <div style={{ marginTop: 40, display: "flex", flexDirection: "column", alignItems: "center", gap: 6 }}>
              {c.lines.map((l, j) =>
                t >= l.t ? (
                  <div key={j} style={{ fontFamily: "Inter", fontWeight: 800, fontSize: 104, lineHeight: 1.05, color: j === c.lines.length - 1 ? "#5A0E0E" : "#A3171A", ...blurIn(at(l.t), fps) }}>
                    {l.text}
                  </div>
                ) : null,
              )}
            </div>
          </AbsoluteFill>
        );
      })}

      {/* hook: big red stacked words */}
      {t < p.hook.end && (
        <AbsoluteFill style={{ alignItems: "center", paddingTop: 150, opacity: fadeOut(frame, p.hook.end, fps) }}>
          {p.hook.words.map((w, i) => {
            if (t < w.t) return <div key={i} style={{ height: w.size * 1.02 }} />;
            const s = spring({ frame: at(w.t), fps, config: { damping: 12, stiffness: 320 } });
            return (
              <div key={i} style={{ fontFamily: "Oswald", fontWeight: 700, fontSize: w.size, lineHeight: 1.02, color: RED, letterSpacing: -2,
                transform: `scale(${1.35 - 0.35 * s})`, opacity: Math.min(1, s * 2), textShadow: "0 6px 18px rgba(0,0,0,0.35)" }}>
                {w.text}
              </div>
            );
          })}
          {p.hook.emoji && t >= p.hook.emoji.t && (() => {
            const e = p.hook.emoji!;
            const s = spring({ frame: at(e.t), fps, config: { damping: 9, stiffness: 260 } });
            const shake = Math.sin(at(e.t) * 0.9) * 10;
            return (
              <div style={{ position: "absolute", top: 330, fontSize: 210, transform: `scale(${s}) rotate(${shake}deg)`, fontFamily: "Noto Color Emoji" }}>{e.char}</div>
            );
          })()}
        </AbsoluteFill>
      )}

      {/* coloured words over photos / video */}
      {p.colorWords.map((w, i) =>
        t >= w.start && t < w.end ? (
          <AbsoluteFill key={`w${i}`} style={{ alignItems: "center", paddingTop: w.top ?? 1180 }}>
            <div style={{ fontFamily: "Oswald", fontWeight: 700, fontSize: w.size ?? 150, color: w.color, lineHeight: 1, textAlign: "center",
              textShadow: "0 4px 16px rgba(0,0,0,0.45)", WebkitTextStroke: "5px #111", paintOrder: "stroke fill", ...blurIn(at(w.start), fps, 0.18), opacity: Math.min(blurIn(at(w.start), fps, 0.18).opacity, fadeOut(frame, w.end, fps)) }}>
              {w.text}
            </div>
          </AbsoluteFill>
        ) : null,
      )}

      {/* handwritten words over the video */}
      {p.scripts.map((s, i) =>
        t >= s.start && t < s.end ? (
          <AbsoluteFill key={`s${i}`} style={{ alignItems: "center", paddingTop: s.top ?? 1150 }}>
            <div style={{ fontFamily: "Marck, cursive", fontSize: 180, color: s.color ?? "#fff", lineHeight: 1, textShadow: s.color === "#111" ? "0 0 18px rgba(255,255,255,0.95), 0 0 6px #fff" : "0 4px 20px rgba(0,0,0,0.6)",
              ...blurIn(at(s.start), fps, 0.3), opacity: Math.min(blurIn(at(s.start), fps, 0.3).opacity, fadeOut(frame, s.end, fps)) }}>
              {s.text}
            </div>
          </AbsoluteFill>
        ) : null,
      )}

      {/* small grey subtitles */}
      {p.subs.map((s, i) =>
        t >= s.start && t < s.end ? (
          <AbsoluteFill key={`u${i}`} style={{ alignItems: "center", paddingTop: s.top ?? 1220 }}>
            <div style={{ fontFamily: "Oswald", fontWeight: 600, fontSize: 64, color: "#D9D9D9", textShadow: "0 2px 10px rgba(0,0,0,0.7)",
              ...blurIn(at(s.start), fps, 0.25), opacity: Math.min(blurIn(at(s.start), fps, 0.25).opacity, fadeOut(frame, s.end, fps)) }}>
              {s.text}
            </div>
          </AbsoluteFill>
        ) : null,
      )}

      {p.emojis.map((e, i) =>
        t >= e.t && t < e.end ? (
          <div key={`e${i}`} style={{ position: "absolute", left: e.x, top: e.y, fontSize: e.size, fontFamily: "Noto Color Emoji",
            transform: `scale(${spring({ frame: at(e.t), fps, config: { damping: 9, stiffness: 260 } })}) rotate(${Math.sin(at(e.t) * 0.8) * 8}deg)` }}>
            {e.char}
          </div>
        ) : null,
      )}
    </AbsoluteFill>
  );
};
