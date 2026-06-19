export const GESTURE_LABELS = {
  fist: "握拳",
  palm: "张开手掌",
  peace: "剪刀手",
  point: "食指指向",
  thumbs_up: "点赞",
  ok: "OK 手势",
  number_1: "数字 1",
  number_2: "数字 2",
  number_3: "数字 3",
  number_4: "数字 4",
  number_5: "数字 5",
  none: "无动作",
  swipe_left: "左滑",
  swipe_right: "右滑",
  swipe_up: "上滑",
  swipe_down: "下滑",
  zoom_in: "放大",
  zoom_out: "缩小",
  unknown: "未识别",
};

export const MODE_LABELS = {
  static: "静态",
  dynamic: "动态",
};

export const TRAINED_STATIC_GESTURES = [
  "fist",
  "palm",
  "peace",
  "thumbs_up",
  "ok",
  "number_1",
  "number_2",
  "number_3",
  "number_4",
];

export function gestureName(label) {
  if (!label) return "检测中";
  return GESTURE_LABELS[label] ?? label;
}

export function modeName(mode) {
  return MODE_LABELS[mode] ?? mode;
}
