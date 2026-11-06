import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";

// Cool (not cute, not derpy) cartoon giraffe for a cameo: dances on top of the speaker's head. Drawn from shapes, so
// it is ours. Side view, facing right: thrusts the pelvis forward and back on every beat with both arms stretched out
// in front, pumping against the hips. The body, neck, arms and legs are one silhouette: every part's outline is drawn
// first and every fill on top, so there are no seams at the joints. Feet stand on the bottom edge of the frame.
export type DancingGiraffeProps = { bpm?: number; transparent?: boolean };

const BODY = "#F2B33D";
const BODY_FAR = "#DE9F2E";
const BELLY = "#FAE0A8";
const SPOT = "#B9652A";
const DARK = "#4A2A12";
const LINE = "#7C4518";
const GOLD = "#E3B341";

const pt = (x: number, y: number, len: number, deg: number): [number, number] => {
  const r = (deg * Math.PI) / 180; // 0 = down, 90 = right, 180 = up
  return [x + Math.sin(r) * len, y + Math.cos(r) * len];
};
// smooth limb: quadratic curve through the joint, so it bends like one piece
const limb = (x: number, y: number, a: number, b: number, l1: number, l2: number) => {
  const [ex, ey] = pt(x, y, l1, a);
  const [hx, hy] = pt(ex, ey, l2, a + b);
  const cx = 2 * ex - (x + hx) / 2;
  const cy = 2 * ey - (y + hy) / 2;
  return { d: `M${x} ${y} Q${cx} ${cy} ${hx} ${hy}`, hx, hy };
};

export const DancingGiraffe: React.FC<DancingGiraffeProps> = ({ bpm = 124, transparent = true }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = (frame / fps) * (bpm / 60); // beats
  const p = t * Math.PI * 2; // one thrust per beat
  const raw = Math.sin(p);
  const thrust = Math.sign(raw) * Math.pow(Math.abs(raw), 0.6); // -1 back .. 1 forward
  const pull = (thrust + 1) / 2;

  const FOOT = 790; // ground line (the speaker's head top)
  const hipX = 270 + thrust * 52;
  const hipY = 610 + Math.abs(thrust) * 8;
  const lean = -thrust * 18;

  const legFar = limb(hipX - 8, hipY, -10 + thrust * 24, 20 - thrust * 40, 92, 92);
  const legNear = limb(hipX + 8, hipY, 8 + thrust * 28, -2 - thrust * 44, 92, 92);
  const [shx, shy] = pt(hipX, hipY, 150, 180 + lean);
  const armFar = limb(shx - 10, shy + 10, 86 + pull * 14, -pull * 100, 84, 80);
  const armNear = limb(shx + 4, shy + 14, 92 + pull * 16, -pull * 108, 86, 82);
  const wob = Math.sin(p * 0.5) * 10;
  const headX = shx + 64 + wob + thrust * 8;
  const headY = shy - 225 + Math.abs(raw) * 10;
  const neck = `M${shx - 6} ${shy + 30} C${shx - 18} ${shy - 70} ${headX - 44} ${headY + 120} ${headX - 22} ${headY + 24}`;
  const tail = Math.sin(p) * 26;
  const torso = { cx: hipX, cy: hipY - 80, rx: 74, ry: 102 };

  // feet land on the ground line: shift the whole figure so the lower foot touches FOOT
  const lowFoot = Math.max(legFar.hy, legNear.hy);
  const dy = FOOT - 14 - lowFoot;

  const W = { limb: 30, arm: 26, neck: 44, o: 9 };
  return (
    <AbsoluteFill style={{ backgroundColor: transparent ? "transparent" : "#F5F5F7" }}>
      <svg viewBox="0 0 600 800" width="100%" height="100%">
        <g transform={`translate(0 ${dy})`}>
          {/* tail */}
          <g transform={`rotate(${lean - tail} ${hipX - 62} ${hipY - 30})`}>
            <path d={`M${hipX - 62} ${hipY - 30} Q${hipX - 102} ${hipY - 12} ${hipX - 106} ${hipY + 34}`} stroke={LINE} strokeWidth={9} fill="none" strokeLinecap="round" />
            <ellipse cx={hipX - 106} cy={hipY + 42} rx={10} ry={15} fill={DARK} />
          </g>
          {/* outline layer: one silhouette */}
          <g stroke={LINE} fill="none" strokeLinecap="round">
            <path d={armFar.d} strokeWidth={W.arm + W.o} />
            <path d={legFar.d} strokeWidth={W.limb + W.o} />
            <path d={legNear.d} strokeWidth={W.limb + W.o} />
            <path d={neck} strokeWidth={W.neck + W.o} />
            <ellipse {...torso} transform={`rotate(${lean} ${hipX} ${hipY})`} fill={LINE} strokeWidth={W.o} />
            <path d={armNear.d} strokeWidth={W.arm + W.o} />
          </g>
          {/* fill layer */}
          <g fill="none" strokeLinecap="round">
            <path d={armFar.d} stroke={BODY_FAR} strokeWidth={W.arm} />
            <path d={legFar.d} stroke={BODY_FAR} strokeWidth={W.limb} />
            <path d={legNear.d} stroke={BODY} strokeWidth={W.limb} />
            <path d={neck} stroke={BODY} strokeWidth={W.neck} />
            <ellipse {...torso} transform={`rotate(${lean} ${hipX} ${hipY})`} fill={BODY} />
          </g>
          {/* torso details */}
          <g transform={`rotate(${lean} ${hipX} ${hipY})`}>
            <ellipse cx={hipX + 28} cy={hipY - 72} rx={38} ry={76} fill={BELLY} />
            <ellipse cx={hipX - 40} cy={hipY - 120} rx={14} ry={11} fill={SPOT} />
            <ellipse cx={hipX - 30} cy={hipY - 40} rx={13} ry={10} fill={SPOT} />
            <ellipse cx={hipX - 52} cy={hipY - 78} rx={10} ry={8} fill={SPOT} />
          </g>
          {/* mane + neck spots */}
          <path d={`M${shx - 28} ${shy + 18} C${shx - 40} ${shy - 70} ${headX - 66} ${headY + 112} ${headX - 46} ${headY + 16}`} stroke={DARK} strokeWidth={9} fill="none" strokeLinecap="round" />
          <path d={neck} stroke={SPOT} strokeWidth={12} fill="none" strokeDasharray="12 26" strokeLinecap="round" />
          {/* hooves */}
          <ellipse cx={legFar.hx + 8} cy={legFar.hy + 8} rx={22} ry={11} fill={DARK} />
          <ellipse cx={legNear.hx + 10} cy={legNear.hy + 8} rx={24} ry={12} fill={DARK} />
          {/* gold chain */}
          <path d={`M${shx - 34} ${shy + 4} Q${shx + 2} ${shy + 40} ${shx + 26} ${shy + 8}`} stroke={GOLD} strokeWidth={7} fill="none" strokeDasharray="9 4" />
          <rect x={shx - 6} y={shy + 20} width={42} height={22} rx={6} fill={GOLD} />
          <text x={shx + 15} y={shy + 36} fontFamily="Russo One, sans-serif" fontSize={15} fill="#7A2E10" textAnchor="middle">RKO</text>
          {/* head in profile: sunglasses, smirk */}
          <g transform={`rotate(${raw * 6} ${headX} ${headY})`}>
            <rect x={headX - 34} y={headY - 92} width={12} height={42} rx={6} fill={BODY} stroke={LINE} strokeWidth={3} transform={`rotate(-16 ${headX - 28} ${headY - 50})`} />
            <circle cx={headX - 40} cy={headY - 94} r={10} fill={DARK} />
            <ellipse cx={headX - 56} cy={headY - 26} rx={28} ry={11} fill={BODY} stroke={LINE} strokeWidth={3} transform={`rotate(${-20 + raw * 18} ${headX - 40} ${headY - 26})`} />
            <path d={`M${headX - 60} ${headY - 10} C${headX - 60} ${headY - 70} ${headX + 40} ${headY - 70} ${headX + 60} ${headY - 18} C${headX + 120} ${headY - 10} ${headX + 122} ${headY + 46} ${headX + 80} ${headY + 54} C${headX + 30} ${headY + 62} ${headX - 60} ${headY + 50} ${headX - 60} ${headY - 10} Z`} fill={BODY} stroke={LINE} strokeWidth={4} />
            <path d={`M${headX + 40} ${headY + 6} C${headX + 90} ${headY - 4} ${headX + 118} ${headY + 16} ${headX + 112} ${headY + 40} C${headX + 104} ${headY + 58} ${headX + 50} ${headY + 58} ${headX + 34} ${headY + 40} Z`} fill={BELLY} />
            <ellipse cx={headX + 100} cy={headY + 16} rx={4} ry={6} fill={DARK} />
            {/* sunglasses */}
            <path d={`M${headX - 8} ${headY - 30} L${headX + 52} ${headY - 34} L${headX + 46} ${headY - 8} Q${headX + 18} ${headY + 2} ${headX - 4} ${headY - 10} Z`} fill="#14183A" />
            <path d={`M${headX - 8} ${headY - 30} L${headX - 46} ${headY - 24}`} stroke="#14183A" strokeWidth={5} strokeLinecap="round" />
            <path d={`M${headX + 4} ${headY - 26} L${headX + 24} ${headY - 28}`} stroke="#fff" strokeWidth={4} strokeLinecap="round" opacity={0.55} />
            {/* smirk */}
            <path d={`M${headX + 62} ${headY + 44} Q${headX + 84} ${headY + 50} ${headX + 102} ${headY + 36}`} stroke={DARK} strokeWidth={5} fill="none" strokeLinecap="round" />
          </g>
          {/* near arm fill last so it stays in front, with its hoof-hand */}
          <path d={armNear.d} stroke={BODY} strokeWidth={W.arm} fill="none" strokeLinecap="round" />
          <circle cx={armFar.hx} cy={armFar.hy} r={14} fill={DARK} />
          <circle cx={armNear.hx} cy={armNear.hy} r={15} fill={DARK} />
        </g>
      </svg>
    </AbsoluteFill>
  );
};
