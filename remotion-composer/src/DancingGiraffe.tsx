import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";

// Goofy meme giraffe for a cameo after the hook (transparent background, laid over the video later). Drawn from
// shapes, so it is ours. Side view, facing right: thrusts the pelvis forward and back on every beat with both arms
// stretched out in front, pumping forward and back against the hips; googly eye, buck teeth, flapping tongue,
// wobbly neck.
export type DancingGiraffeProps = { bpm?: number; transparent?: boolean };

const BODY = "#F4B942";
const BELLY = "#FBE3B0";
const SPOT = "#C4702C";
const DARK = "#5A3416";
const LINE = "#8F531E";
const GOLD = "#E3B341";

const pt = (x: number, y: number, len: number, deg: number): [number, number] => {
  const r = (deg * Math.PI) / 180; // 0 = down, 90 = right, 180 = up
  return [x + Math.sin(r) * len, y + Math.cos(r) * len];
};
const limb = (x: number, y: number, a: number, b: number, l1: number, l2: number): [string, number, number] => {
  const [ex, ey] = pt(x, y, l1, a);
  const [hx, hy] = pt(ex, ey, l2, a + b);
  return [`M${x} ${y} L${ex} ${ey} L${hx} ${hy}`, hx, hy];
};
const Stroke: React.FC<{ d: string; w: number; far?: boolean }> = ({ d, w, far }) => (
  <g opacity={far ? 0.85 : 1}>
    <path d={d} stroke={LINE} strokeWidth={w + 8} fill="none" strokeLinecap="round" strokeLinejoin="round" />
    <path d={d} stroke={far ? "#E3A632" : BODY} strokeWidth={w} fill="none" strokeLinecap="round" strokeLinejoin="round" />
  </g>
);

export const DancingGiraffe: React.FC<DancingGiraffeProps> = ({ bpm = 124, transparent = true }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = (frame / fps) * (bpm / 60); // beats
  const p = t * Math.PI * 2; // one thrust per beat
  // snappy thrust: fast forward, slower back
  const raw = Math.sin(p);
  const thrust = Math.sign(raw) * Math.pow(Math.abs(raw), 0.6); // -1 back .. 1 forward
  const hipX = 270 + thrust * 58;
  const hipY = 600 + Math.abs(thrust) * 6;
  const lean = -thrust * 20; // upper body leans back when the hips go forward
  const pull = (thrust + 1) / 2; // arms pull back as the hips go forward

  // legs: feet planted, knees bend forward when the hips go forward
  const [legFar] = limb(hipX - 6, hipY, -8 + thrust * 24, 18 - thrust * 40, 86, 84);
  const [legNear] = limb(hipX + 6, hipY, 8 + thrust * 28, -4 - thrust * 44, 86, 84);

  // shoulders follow the lean
  const [shx, shy] = pt(hipX, hipY, 150, 180 + lean);
  // arms stretched forward, pumping: reach out when hips go back, bend in when hips go forward
  const [armFar, fhx, fhy] = limb(shx - 8, shy + 6, 86 + pull * 14, -pull * 105, 84, 82);
  const [armNear, nhx, nhy] = limb(shx + 6, shy + 10, 92 + pull * 16, -pull * 112, 86, 84);

  // neck goes up and slightly forward from the shoulders, wobbling
  const wob = Math.sin(p * 0.5) * 16 + Math.sin(p * 1.5) * 6;
  const headX = shx + 70 + wob + thrust * 10;
  const headY = shy - 230 + Math.abs(raw) * 12;
  const pupil = [Math.sin(t * 7.3) * 7, Math.cos(t * 5.9) * 7];
  const tongue = Math.sin(t * Math.PI * 3) * 16;
  const tail = Math.sin(p) * 28;

  return (
    <AbsoluteFill style={{ backgroundColor: transparent ? "transparent" : "#F5F5F7" }}>
      <svg viewBox="0 0 600 800" width="100%" height="100%">
        <ellipse cx={300} cy={778} rx={115} ry={13} fill="#000" opacity={0.16} />
        <Stroke d={armFar} w={22} far />
        <circle cx={fhx} cy={fhy} r={14} fill={DARK} />
        <Stroke d={legFar} w={28} far />
        {/* torso as a rotated egg between hips and shoulders */}
        <g transform={`rotate(${lean} ${hipX} ${hipY})`}>
          <g transform={`rotate(${-tail} ${hipX - 60} ${hipY - 20})`}>
            <path d={`M${hipX - 60} ${hipY - 20} Q${hipX - 100} ${hipY - 5} ${hipX - 105} ${hipY + 40}`} stroke={LINE} strokeWidth={9} fill="none" strokeLinecap="round" />
            <ellipse cx={hipX - 105} cy={hipY + 48} rx={10} ry={15} fill={DARK} />
          </g>
          <ellipse cx={hipX} cy={hipY - 80} rx={78} ry={105} fill={BODY} stroke={LINE} strokeWidth={4} />
          <ellipse cx={hipX + 30} cy={hipY - 70} rx={40} ry={78} fill={BELLY} />
          <ellipse cx={hipX - 40} cy={hipY - 120} rx={14} ry={11} fill={SPOT} />
          <ellipse cx={hipX - 30} cy={hipY - 40} rx={13} ry={10} fill={SPOT} />
          <ellipse cx={hipX - 55} cy={hipY - 75} rx={10} ry={8} fill={SPOT} />
        </g>
        <Stroke d={legNear} w={30} />
        {/* hooves */}
        <ellipse cx={pt(...pt(hipX - 6, hipY, 86, -8 + thrust * 24), 84, -8 + thrust * 24 + 18 - thrust * 40)[0] + 8} cy={764} rx={24} ry={12} fill={DARK} opacity={0.85} />
        <ellipse cx={pt(...pt(hipX + 6, hipY, 86, 8 + thrust * 28), 84, 8 + thrust * 28 - 4 - thrust * 44)[0] + 10} cy={766} rx={26} ry={13} fill={DARK} />
        {/* neck */}
        <path d={`M${shx - 10} ${shy + 20} C${shx - 20} ${shy - 80} ${headX - 40 - wob * 0.5} ${headY + 120} ${headX - 20} ${headY + 30}`} stroke={LINE} strokeWidth={52} fill="none" strokeLinecap="round" />
        <path d={`M${shx - 10} ${shy + 20} C${shx - 20} ${shy - 80} ${headX - 40 - wob * 0.5} ${headY + 120} ${headX - 20} ${headY + 30}`} stroke={BODY} strokeWidth={44} fill="none" strokeLinecap="round" />
        <path d={`M${shx - 30} ${shy + 10} C${shx - 40} ${shy - 80} ${headX - 62 - wob * 0.5} ${headY + 110} ${headX - 44} ${headY + 20}`} stroke={DARK} strokeWidth={9} fill="none" strokeLinecap="round" />
        <path d={`M${shx - 10} ${shy + 20} C${shx - 20} ${shy - 80} ${headX - 40 - wob * 0.5} ${headY + 120} ${headX - 20} ${headY + 30}`} stroke={SPOT} strokeWidth={13} fill="none" strokeDasharray="13 26" strokeLinecap="round" />
        {/* gold chain */}
        <path d={`M${shx - 34} ${shy - 4} Q${shx + 4} ${shy + 34} ${shx + 26} ${shy + 2}`} stroke={GOLD} strokeWidth={7} fill="none" strokeDasharray="9 4" />
        <rect x={shx - 4} y={shy + 14} width={40} height={22} rx={6} fill={GOLD} />
        <text x={shx + 16} y={shy + 30} fontFamily="Russo One, sans-serif" fontSize={15} fill="#7A2E10" textAnchor="middle">RKO</text>
        {/* head in profile, facing right */}
        <g transform={`rotate(${Math.sin(p) * 8} ${headX} ${headY})`}>
          <rect x={headX - 34} y={headY - 96} width={12} height={44} rx={6} fill={BODY} stroke={LINE} strokeWidth={3} transform={`rotate(${-18 + raw * 10} ${headX - 28} ${headY - 52})`} />
          <circle cx={headX - 42} cy={headY - 98} r={11} fill={DARK} />
          <ellipse cx={headX - 58} cy={headY - 30} rx={30} ry={12} fill={BODY} stroke={LINE} strokeWidth={3} transform={`rotate(${-25 + raw * 30} ${headX - 40} ${headY - 30})`} />
          <ellipse cx={headX} cy={headY - 10} rx={62} ry={52} fill={BODY} stroke={LINE} strokeWidth={4} />
          <ellipse cx={headX + 58} cy={headY + 22} rx={54} ry={36} fill={BELLY} stroke={LINE} strokeWidth={3} />
          <ellipse cx={headX + 92} cy={headY + 10} rx={5} ry={7} fill={DARK} />
          <circle cx={headX + 8} cy={headY - 28} r={30} fill="#fff" stroke={LINE} strokeWidth={3} />
          <circle cx={headX + 12 + pupil[0]} cy={headY - 26 + pupil[1]} r={13} fill="#111" />
          <path d={`M${headX + 40} ${headY + 40} Q${headX + 80} ${headY + 60} ${headX + 108} ${headY + 34}`} stroke="#5A1A0C" strokeWidth={6} fill="none" strokeLinecap="round" />
          <rect x={headX + 74} y={headY + 36} width={13} height={17} rx={3} fill="#fff" stroke={LINE} strokeWidth={2} />
          <rect x={headX + 88} y={headY + 33} width={13} height={17} rx={3} fill="#fff" stroke={LINE} strokeWidth={2} />
          <path d={`M${headX + 100} ${headY + 44} Q${headX + 118 + tongue * 0.4} ${headY + 70 + Math.abs(tongue)} ${headX + 126 + tongue} ${headY + 82}`} stroke="#E8607A" strokeWidth={13} fill="none" strokeLinecap="round" />
        </g>
        {/* near arm in front of everything */}
        <Stroke d={armNear} w={24} />
        <circle cx={nhx} cy={nhy} r={15} fill={DARK} />
      </svg>
    </AbsoluteFill>
  );
};
