import { Database, Save } from "lucide-react";
import { useEffect, useState } from "react";
import { MetricCard } from "../components/MetricCard.jsx";
import { createDemoFeature } from "../lib/features.js";
import { gestureName } from "../lib/gestureLabels.js";
import { getJson, postJson } from "../lib/api.js";

export function CollectView() {
  const [labels, setLabels] = useState({ static: [], dynamic: [] });
  const [counts, setCounts] = useState({ static: {}, dynamic: {} });
  const [mode, setMode] = useState("static");
  const [label, setLabel] = useState("palm");
  const [saved, setSaved] = useState(null);

  useEffect(() => {
    getJson("/api/labels").then((data) => {
      setLabels(data);
      setLabel(data.static[0] ?? "palm");
    });
    refreshCounts();
  }, []);

  async function refreshCounts() {
    setCounts(await getJson("/api/samples/counts"));
  }

  async function saveSample() {
    const feature =
      mode === "static"
        ? createDemoFeature(label)
        : Array.from({ length: 30 }, () => createDemoFeature(label));
    const res = await postJson("/api/samples", { mode, label, feature });
    setSaved(res.id);
    await refreshCounts();
  }

  return (
    <section className="pageBand">
      <div className="sectionHeader">
        <Database size={24} />
        <div>
          <h2>数据采集</h2>
          <p>PostgreSQL 样本库</p>
        </div>
      </div>
      <div className="formGrid">
        <label>
          模式
          <select value={mode} onChange={(event) => setMode(event.target.value)}>
            <option value="static">static</option>
            <option value="dynamic">dynamic</option>
          </select>
        </label>
        <label>
          标签
          <select value={label} onChange={(event) => setLabel(event.target.value)}>
            {(labels[mode] ?? []).map((item) => (
              <option key={item} value={item}>
                {gestureName(item)}
              </option>
            ))}
          </select>
        </label>
        <button className="primaryButton" onClick={saveSample}>
          <Save size={18} />
          保存样本
        </button>
      </div>
      <div className="metricsGrid wide">
        {Object.entries(counts[mode] ?? {}).map(([key, value]) => (
          <MetricCard key={key} label={gestureName(key)} value={value} />
        ))}
      </div>
      {saved && <p className="notice">样本 #{saved} 已入库</p>}
    </section>
  );
}
