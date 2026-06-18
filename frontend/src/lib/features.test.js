import { describe, expect, it } from "vitest";
import { normalizeLandmarks } from "./features.js";

describe("normalizeLandmarks", () => {
  it("is invariant to translation and scale", () => {
    const landmarks = Array.from({ length: 21 }, (_, i) => ({ x: i + 1, y: (i % 5) + 2, z: i * 0.1 }));
    const changed = landmarks.map((point) => ({
      x: point.x * 4 + 8,
      y: point.y * 4 - 3,
      z: point.z * 4 + 2,
    }));

    const actual = normalizeLandmarks(changed);
    const expected = normalizeLandmarks(landmarks);
    actual.forEach((value, index) => {
      expect(value).toBeCloseTo(expected[index], 10);
    });
  });
});
