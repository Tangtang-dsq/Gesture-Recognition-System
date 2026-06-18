const CONNECTIONS = [
  [0, 1],
  [1, 2],
  [2, 3],
  [3, 4],
  [0, 5],
  [5, 6],
  [6, 7],
  [7, 8],
  [0, 9],
  [9, 10],
  [10, 11],
  [11, 12],
  [0, 13],
  [13, 14],
  [14, 15],
  [15, 16],
  [0, 17],
  [17, 18],
  [18, 19],
  [19, 20],
  [5, 9],
  [9, 13],
  [13, 17],
];

export function drawSkeleton(canvas, landmarks) {
  const ctx = canvas.getContext("2d");
  const { width, height } = canvas;
  ctx.clearRect(0, 0, width, height);
  if (!landmarks?.length) return;

  ctx.save();
  ctx.lineWidth = 3;
  ctx.strokeStyle = "#2f7d73";
  ctx.fillStyle = "#f3b23c";
  for (const [from, to] of CONNECTIONS) {
    ctx.beginPath();
    ctx.moveTo(landmarks[from].x * width, landmarks[from].y * height);
    ctx.lineTo(landmarks[to].x * width, landmarks[to].y * height);
    ctx.stroke();
  }
  for (const point of landmarks) {
    ctx.beginPath();
    ctx.arc(point.x * width, point.y * height, 4, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.restore();
}
