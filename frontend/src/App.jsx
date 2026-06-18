import { Database, Gauge, HandMetal, LayoutDashboard, Presentation } from "lucide-react";
import { useState } from "react";
import { AdminView } from "./views/AdminView.jsx";
import { CollectView } from "./views/CollectView.jsx";
import { DemoView } from "./views/DemoView.jsx";
import { RecognizeView } from "./views/RecognizeView.jsx";

const NAV = [
  { id: "recognize", label: "识别", icon: HandMetal },
  { id: "collect", label: "采集", icon: Database },
  { id: "demo", label: "演示", icon: Presentation },
  { id: "admin", label: "管理", icon: LayoutDashboard },
];

export default function App() {
  const [view, setView] = useState("recognize");
  const Active = {
    recognize: RecognizeView,
    collect: CollectView,
    demo: DemoView,
    admin: AdminView,
  }[view];

  return (
    <main className="appShell">
      <header className="appHeader">
        <div className="brand">
          <Gauge size={28} />
          <div>
            <h1>手势识别系统</h1>
            <span>关键点实时识别工作台</span>
          </div>
        </div>
        <nav>
          {NAV.map((item) => {
            const Icon = item.icon;
            return (
              <button key={item.id} className={view === item.id ? "active" : ""} onClick={() => setView(item.id)}>
                <Icon size={18} />
                {item.label}
              </button>
            );
          })}
        </nav>
      </header>
      <Active />
    </main>
  );
}
