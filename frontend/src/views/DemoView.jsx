import { ChevronLeft, ChevronRight, Presentation } from "lucide-react";
import { useState } from "react";

const slides = [
  { title: "实时关键点", body: "浏览器端 MediaPipe 输出 21 点骨架" },
  { title: "低带宽传输", body: "WebSocket 上行 63 维归一化特征" },
  { title: "后端分类", body: "FastAPI 管理静态与动态识别链路" },
];

export function DemoView() {
  const [index, setIndex] = useState(0);
  const slide = slides[index];

  function next() {
    setIndex((value) => (value + 1) % slides.length);
  }

  function prev() {
    setIndex((value) => (value - 1 + slides.length) % slides.length);
  }

  return (
    <section className="demoBand">
      <div className="demoSlide">
        <Presentation size={34} />
        <h2>{slide.title}</h2>
        <p>{slide.body}</p>
      </div>
      <div className="demoControls">
        <button className="iconButton large" onClick={prev} title="上一页">
          <ChevronLeft />
        </button>
        <span>
          {index + 1} / {slides.length}
        </span>
        <button className="iconButton large" onClick={next} title="下一页">
          <ChevronRight />
        </button>
      </div>
    </section>
  );
}
