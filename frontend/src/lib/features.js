export function normalizeLandmarks(landmarks) {
  if (!landmarks || landmarks.length !== 21) {
    throw new Error("landmarks must contain 21 points");
  }
  const wrist = landmarks[0];
  const mid = landmarks[9];
  const base =
    Math.hypot(mid.x - wrist.x, mid.y - wrist.y, (mid.z ?? 0) - (wrist.z ?? 0)) || 1e-6;
  const out = new Array(63);
  for (let i = 0; i < 21; i += 1) {
    out[i * 3] = (landmarks[i].x - wrist.x) / base;
    out[i * 3 + 1] = (landmarks[i].y - wrist.y) / base;
    out[i * 3 + 2] = ((landmarks[i].z ?? 0) - (wrist.z ?? 0)) / base;
  }
  return out;
}

export function createDemoFeature(kind = "palm") {
  const points = Array.from({ length: 21 }, () => ({ x: 0, y: 0, z: 0 }));
  points[0] = { x: 0, y: 0, z: 0 };
  points[9] = { x: 0, y: -1, z: 0 };
  const openTips = {
    palm: [4, 8, 12, 16, 20],
    peace: [8, 12],
    point: [8],
    thumbs_up: [4],
    fist: [],
  }[kind] ?? [4, 8, 12, 16, 20];

  const bases = [2, 5, 9, 13, 17];
  const tips = [4, 8, 12, 16, 20];
  for (let i = 0; i < tips.length; i += 1) {
    points[bases[i]] = { x: (i - 2) * 0.25, y: -0.45, z: 0 };
    const extended = openTips.includes(tips[i]);
    points[tips[i]] = { x: (i - 2) * 0.28, y: extended ? -1.45 : -0.55, z: 0 };
  }
  return points.flatMap((point) => [point.x, point.y, point.z]);
}
