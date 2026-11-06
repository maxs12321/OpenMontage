import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";

// Goofy meme giraffe for a cameo after the hook (transparent background, laid over the video later). Drawn from shapes,
// so it is ours. Funny, not cute: noodle neck that whips around, googly eyes looking different ways, buck teeth and a
// flapping tongue, flailing arms, wobbly knees, and a full head spin every 4 beats.
export type DancingGiraffeProps = { bpm?: number; transparent?: boolean };

const BODY = "#F4B942";
const BELLY = "#FBE3B0";
const SPOT = "#C4702C";
const DARK = "#5A3416";
const LINE = "#8F531E";
const GOLD = "#E3B341";

const pt = (x: number, y: number, len: number, deg: number): [number, number] => {
  const r = (deg * Math.PI) / 180;
  return [x + Math.sin(r) * len, y + Math.cos(r) * len];
};

const Limb: React.FC<{ x: number; y: number; a: number; b: number; l1: number; l2: number; w: number }> = ({ x, y, a, b, l1, l2, w }) => {
  const [ex, ey] = pt(x, y, l1, a);
  const [hx, hy] = pt(ex, ey, l2, a + b);
  const d = `M${x} ${y} L${ex} ${ey} L${hx} ${hy}`;
  return (
    <g>
      <path d={d} stroke={LINE} strokeWidth={w + 8} fill="none" strokeLinecap="round" strokeLinejoin="round" />
      <path d={d} stroke={BODY} strokeWidth={w} fill="none" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx={hx} cy={hy} r={w * 0.62} fill={DARK} />
    </g>
  );
};

export const DancingGiraffe: React.FC<DancingGiraffeProps> = ({ bpm = 128, transparent = true }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = (frame / fps) * (bpm / 60); // beats
  const s1 = Math.sin(t * Math.PI);
  const bounce = Math.abs(s1);
  const y = -bounce * 26;
  const sway = Math.sin((t * Math.PI) / 2);

  // noodle neck: the head whips side to side in a figure-eight, the neck follows as a wobbly curve
  const headX = 300 + Math.sin(t * Math.PI * 0.5) * 95 + Math.sin(t * Math.PI * 1.5) * 18;
  const headY = 150 + Math.abs(Math.sin(t * Math.PI)) * 30;
  const c1x = 300 - Math.sin(t * Math.PI * 0.5 + 0.8) * 70;
  const c2x = headX + Math.sin(t * Math.PI + 1.3) * 60;
  // full head spin on the last beat of every 4
  const bar = t % 4;
  const spin = bar > 3.35 ? Math.min(1, (bar - 3.35) / 0.45) * 360 : 0;
  const headTilt = Math.sin(t * Math.PI) * 18 + spin;

  // flailing arms (twice per beat, out of phase), wobbly Elvis knees
  const aL = -110 + Math.sin(t * Math.PI * 2) * 65;
  const bL = -40 + Math.sin(t * Math.PI * 2 + 1.2) * 60;
  const aR = 110 + Math.sin(t * Math.PI * 2 + 2.1) * 65;
  const bR = 40 + Math.sin(t * Math.PI * 2 + 3.0) * 60;
  const kneeL = Math.sin(t * Math.PI * 4) * 22;
  const kneeR = -Math.sin(t * Math.PI * 4 + 0.6) * 22;

  // googly eyes: pupils rattle independently and look in different directions
  const pL = [Math.sin(t * 7.1) * 7 - 4, Math.cos(t * 5.3) * 7 + 3];
  const pR = [Math.sin(t * 6.2 + 2) * 6 + 5, Math.cos(t * 8.4 + 1) * 6 - 2];
  const tongue = Math.sin(t * Math.PI * 3) * 18;

  const hip = sway * 20;
  return (
    <AbsoluteFill style={{ backgroundColor: transparent ? "transparent" : "#F5F5F7" }}>
      <svg viewBox="0 0 600 800" width="100%" height="100%">
        <ellipse cx={300} cy={778} rx={120 - bounce * 20} ry={13} fill="#000" opacity={0.16} />
        <g transform={`translate(${hip} 0)`}>
          {/* legs with shaking knees */}
          <Limb x={262} y={610 + y} a={-6 + kneeL * 0.4} b={12 - kneeL} l1={80} l2={82 + y * 0.3} w={28} />
          <Limb x={338} y={610 + y} a={6 + kneeR * 0.4} b={-12 - kneeR} l1={80} l2={82 + y * 0.3} w={28} />
          <g transform={`translate(0 ${y}) rotate(${sway * 6} 300 600)`}>
            <path d={`M360 590 Q${410 + Math.sin(t * 9) * 20} 600 ${415 + Math.sin(t * 9) * 25} 645`} stroke={LINE} strokeWidth={9} fill="none" strokeLinecap="round" />
            {/* torso */}
            <path d="M300 440 C345 440 378 495 384 552 C390 610 350 635 300 635 C250 635 210 610 216 552 C222 495 255 440 300 440 Z" fill={BODY} stroke={LINE} strokeWidth={4} />
            <path d="M300 482 C326 482 344 520 347 558 C350 598 326 615 300 615 C274 615 250 598 253 558 C256 520 274 482 300 482 Z" fill={BELLY} />
            <ellipse cx={238} cy={530} rx={14} ry={11} fill={SPOT} />
            <ellipse cx={364} cy={545} rx={13} ry={10} fill={SPOT} />
            <ellipse cx={232} cy={595} rx={11} ry={9} fill={SPOT} />
            <Limb x={240} y={478} a={aL} b={bL} l1={68} l2={62} w={24} />
            <Limb x={360} y={478} a={aR} b={bR} l1={68} l2={62} w={24} />
            {/* noodle neck */}
            <path d={`M300 470 C${c1x} 360 ${c2x} ${headY + 110} ${headX} ${headY + 40}`} stroke={LINE} strokeWidth={50} fill="none" strokeLinecap="round" />
            <path d={`M300 470 C${c1x} 360 ${c2x} ${headY + 110} ${headX} ${headY + 40}`} stroke={BODY} strokeWidth={42} fill="none" strokeLinecap="round" />
            <path d={`M300 470 C${c1x} 360 ${c2x} ${headY + 110} ${headX} ${headY + 40}`} stroke={SPOT} strokeWidth={14} fill="none" strokeDasharray="14 26" strokeLinecap="round" />
            <path d="M268 455 Q300 485 332 455" stroke={GOLD} strokeWidth={7} fill="none" strokeDasharray="9 4" />
            <rect x={280} y={472} width={40} height={22} rx={6} fill={GOLD} />
            <text x={300} y={488} fontFamily="Russo One, sans-serif" fontSize={15} fill="#7A2E10" textAnchor="middle">RKO</text>
            {/* head */}
            <g transform={`translate(${headX - 300} ${headY - 150}) rotate(${headTilt} 300 160)`}>
              <rect x={268} y={58} width={12} height={46} rx={6} fill={BODY} stroke={LINE} strokeWidth={3} transform={`rotate(${-12 + s1 * 10} 274 104)`} />
              <rect x={322} y={58} width={12} height={46} rx={6} fill={BODY} stroke={LINE} strokeWidth={3} transform={`rotate(${14 - s1 * 12} 328 104)`} />
              <circle cx={264} cy={62} r={11} fill={DARK} />
              <circle cx={338} cy={62} r={11} fill={DARK} />
              <ellipse cx={226} cy={130} rx={32} ry={13} fill={BODY} stroke={LINE} strokeWidth={3} transform={`rotate(${-30 + s1 * 25} 250 130)`} />
              <ellipse cx={374} cy={130} rx={32} ry={13} fill={BODY} stroke={LINE} strokeWidth={3} transform={`rotate(${30 + s1 * 25} 350 130)`} />
              <ellipse cx={300} cy={150} rx={66} ry={58} fill={BODY} stroke={LINE} strokeWidth={4} />
              {/* long snout */}
              <ellipse cx={312} cy={205} rx={58} ry={40} fill={BELLY} stroke={LINE} strokeWidth={3} />
              <ellipse cx={294} cy={192} rx={5} ry={7} fill={DARK} />
              <ellipse cx={328} cy={192} rx={5} ry={7} fill={DARK} />
              {/* googly eyes, different sizes */}
              <circle cx={272} cy={128} r={26} fill="#fff" stroke={LINE} strokeWidth={3} />
              <circle cx={332} cy={122} r={34} fill="#fff" stroke={LINE} strokeWidth={3} />
              <circle cx={272 + pL[0]} cy={128 + pL[1]} r={11} fill="#111" />
              <circle cx={332 + pR[0]} cy={122 + pR[1]} r={14} fill="#111" />
              {/* goofy mouth: buck teeth + flapping tongue */}
              <path d="M276 222 Q312 246 350 220 Q346 238 312 240 Q282 238 276 222 Z" fill="#5A1A0C" />
              <rect x={300} y={219} width={13} height={17} rx={3} fill="#fff" stroke={LINE} strokeWidth={2} />
              <rect x={314} y={219} width={13} height={17} rx={3} fill="#fff" stroke={LINE} strokeWidth={2} />
              <path d={`M326 234 Q${338 + tongue * 0.4} ${262 + Math.abs(tongue)} ${346 + tongue} 270`} stroke="#E8607A" strokeWidth={14} fill="none" strokeLinecap="round" />
            </g>
          </g>
        </g>
      </svg>
    </AbsoluteFill>
  );
};
