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


const Duck: React.FC<{ f: number; fps: number }> = ({ f, fps }) => {
  // giraffe in the same round-emoji style as the reference duck: one brow raised, loading spinner on the forehead
  const spin = Math.floor((f / fps) * 12) % 12;
  return (
    <svg viewBox="-200 -230 400 420" width={430} height={452}>
      <defs>
        <radialGradient id="gf" cx="40%" cy="35%" r="70%">
          <stop offset="0%" stopColor="#FFD873" />
          <stop offset="70%" stopColor="#F4B23A" />
          <stop offset="100%" stopColor="#DE9424" />
        </radialGradient>
      </defs>
      {/* ossicones */}
      <rect x={-78} y={-215} width={22} height={80} rx={11} fill="#E9A630" stroke="#B26A12" strokeWidth={5} transform="rotate(-12 -67 -140)" />
      <rect x={56} y={-215} width={22} height={80} rx={11} fill="#E9A630" stroke="#B26A12" strokeWidth={5} transform="rotate(12 67 -140)" />
      <circle cx={-82} cy={-212} r={20} fill="#6B3E14" />
      <circle cx={82} cy={-212} r={20} fill="#6B3E14" />
      {/* ears */}
      <ellipse cx={-168} cy={-70} rx={46} ry={22} fill="#F4B23A" stroke="#B26A12" strokeWidth={5} transform="rotate(-25 -168 -70)" />
      <ellipse cx={168} cy={-70} rx={46} ry={22} fill="#F4B23A" stroke="#B26A12" strokeWidth={5} transform="rotate(25 168 -70)" />
      {/* face */}
      <circle r={160} fill="url(#gf)" stroke="#B26A12" strokeWidth={6} />
      <ellipse cx={-110} cy={-40} rx={22} ry={18} fill="#B8642A" opacity={0.75} />
      <ellipse cx={118} cy={-20} rx={18} ry={15} fill="#B8642A" opacity={0.75} />
      <ellipse cx={-120} cy={40} rx={14} ry={12} fill="#B8642A" opacity={0.75} />
      <path d="M60 -128 A150 150 0 0 1 140 -40" stroke="#fff" strokeWidth={12} fill="none" strokeLinecap="round" opacity={0.6} />
      {[...Array(12)].map((_, i) => (
        <rect key={i} x={-5} y={-62} width={10} height={26} rx={5} fill="#6B4A16"
          opacity={0.15 + 0.85 * (((i - spin + 12) % 12) / 11)} transform={`translate(-10 -62) rotate(${i * 30})`} />
      ))}
      <path d="M-100 8 L-38 24" stroke="#2A1608" strokeWidth={10} strokeLinecap="round" />
      <path d="M38 -4 Q70 -32 100 -6" stroke="#2A1608" strokeWidth={10} fill="none" strokeLinecap="round" />
      <ellipse cx={-62} cy={48} rx={19} ry={23} fill="#1A1A1A" />
      <ellipse cx={62} cy={44} rx={19} ry={23} fill="#1A1A1A" />
      <circle cx={-56} cy={40} r={6} fill="#fff" />
      <circle cx={68} cy={36} r={6} fill="#fff" />
      {/* snout */}
      <ellipse cx={0} cy={112} rx={88} ry={50} fill="#FBE3B0" stroke="#B26A12" strokeWidth={5} />
      <ellipse cx={-28} cy={104} rx={9} ry={12} fill="#5A3416" />
      <ellipse cx={28} cy={104} rx={9} ry={12} fill="#5A3416" />
      <path d="M-30 138 Q0 148 34 134" stroke="#5A3416" strokeWidth={6} fill="none" strokeLinecap="round" />
    </svg>
  );
};

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
          <AbsoluteFill key={`c${i}`} style={{ backgroundColor: "#F2F2F2", opacity: Math.min(inn, out), alignItems: "center", paddingTop: 470, paddingRight: 100 }}>
            {t >= c.script.t && (
              <div style={{ fontFamily: "Marck, cursive", fontSize: 255, color: "#111", lineHeight: 1, ...blurIn(at(c.script.t), fps, 0.35),
                transform: `scale(${interpolate(at(c.script.t), [0, 0.35 * fps], [0.8, 1], { extrapolateRight: "clamp" })})` }}>
                {c.script.text}
              </div>
            )}
            <div style={{ marginTop: 40, display: "flex", flexDirection: "column", alignItems: "center", gap: 6 }}>
              {c.lines.map((l, j) =>
                t >= l.t ? (
                  <div key={j} style={{ fontFamily: "Inter", fontWeight: 800, fontSize: 118, lineHeight: 1.06, color: j === c.lines.length - 1 ? "#5A0E0E" : "#A3171A", ...blurIn(at(l.t), fps) }}>
                    {l.text}
                  </div>
                ) : null,
              )}
            </div>
          </AbsoluteFill>
        );
      })}

      {/* hook: huge red stacked words over a darkened picture, like the reference */}
      {t < p.hook.end && (
        <AbsoluteFill style={{ opacity: fadeOut(frame, p.hook.end, fps) }}>
          <svg viewBox="0 0 1080 1920" width="100%" height="100%" style={{ position: "absolute" }}>
            {p.hook.words.map((w, i) => {
              if (t < w.t) return null;
              const sp = spring({ frame: at(w.t), fps, config: { damping: 12, stiffness: 320 } });
              const ys = [640, 1090, 1400]; // inside the TikTok safe zone (top bar, right buttons, caption at the bottom)
              const fit = w.text.length > 4 ? 820 : undefined;
              return (
                <text key={i} x={490} y={ys[i]} textAnchor="middle" fontFamily="Oswald" fontWeight={700} fontSize={w.size} fill={RED}
                  {...(fit ? { textLength: fit, lengthAdjust: "spacingAndGlyphs" } : {})}
                  style={{ transformOrigin: `490px ${ys[i] - w.size * 0.35}px`, transform: `scale(${1.3 - 0.3 * sp})`, opacity: Math.min(1, sp * 2),
                    filter: "drop-shadow(0 8px 18px rgba(0,0,0,0.5))" }}>
                  {w.text}
                </text>
              );
            })}
          </svg>
          {p.hook.emoji && t >= p.hook.emoji.t && (() => {
            const e = p.hook.emoji!;
            const sp = spring({ frame: at(e.t), fps, config: { damping: 9, stiffness: 260 } });
            return (
              <div style={{ position: "absolute", left: 285, top: 640, transform: `scale(${sp}) rotate(${Math.sin(at(e.t) * 0.5) * 4}deg)` }}>
                <Duck f={at(e.t)} fps={fps} />
              </div>
            );
          })()}
        </AbsoluteFill>
      )}

      {/* coloured words over photos / video */}
      {p.colorWords.map((w, i) =>
        t >= w.start && t < w.end ? (
          <AbsoluteFill key={`w${i}`} style={{ alignItems: "center", paddingTop: w.top ?? 860, paddingRight: 100 }}>
            <div style={{ fontFamily: "Oswald", fontWeight: 700, fontSize: w.size ?? 170, color: w.color, lineHeight: 1, textAlign: "center",
              textShadow: "0 0 3px rgba(0,0,0,0.9), 0 4px 18px rgba(0,0,0,0.7)", ...blurIn(at(w.start), fps, 0.18), opacity: Math.min(blurIn(at(w.start), fps, 0.18).opacity, fadeOut(frame, w.end, fps)) }}>
              {w.text}
            </div>
          </AbsoluteFill>
        ) : null,
      )}

      {/* handwritten words over the video */}
      {p.scripts.map((s, i) =>
        t >= s.start && t < s.end ? (
          <AbsoluteFill key={`s${i}`} style={{ alignItems: "center", paddingTop: s.top ?? 760 }}>
            <div style={{ fontFamily: "Marck, cursive", fontSize: 165, color: s.color ?? "#fff", lineHeight: 1, whiteSpace: "nowrap", textShadow: s.color === "#111" ? "0 0 18px rgba(255,255,255,0.95), 0 0 6px #fff" : "0 4px 20px rgba(0,0,0,0.6)",
              ...blurIn(at(s.start), fps, 0.3), opacity: Math.min(blurIn(at(s.start), fps, 0.3).opacity, fadeOut(frame, s.end, fps)) }}>
              {s.text}
            </div>
          </AbsoluteFill>
        ) : null,
      )}

      {/* small grey subtitles */}
      {p.subs.map((s, i) =>
        t >= s.start && t < s.end ? (
          <AbsoluteFill key={`u${i}`} style={{ alignItems: "center", paddingTop: s.top ?? 900, paddingRight: 100 }}>
            <div style={{ fontFamily: "Oswald", fontWeight: 600, fontSize: 92, color: "rgba(225,225,225,0.85)", textShadow: "0 2px 10px rgba(0,0,0,0.7)",
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
