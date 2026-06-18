import { Activity, Brain, RefreshCcw } from "lucide-react";
import { useEffect, useState } from "react";
import { MetricCard } from "../components/MetricCard.jsx";
import { getJson, postJson } from "../lib/api.js";

export function AdminView() {
  const [metrics, setMetrics] = useState(null);
  const [models, setModels] = useState([]);
  const [job, setJob] = useState(null);

  async function refresh() {
    setMetrics(await getJson("/api/metrics"));
    setModels(await getJson("/api/models"));
  }

  async function train(mode) {
    setJob(await postJson("/api/train", { mode }));
    window.setTimeout(refresh, 300);
  }

  useEffect(() => {
    refresh();
  }, []);

  return (
    <section className="pageBand">
      <div className="sectionHeader">
        <Brain size={24} />
        <div>
          <h2>模型管理</h2>
          <p>训练任务与服务状态</p>
        </div>
        <button className="iconButton" title="刷新" onClick={refresh}>
          <RefreshCcw size={18} />
        </button>
      </div>
      <div className="metricsGrid">
        <MetricCard label="样本" value={metrics?.samples ?? "-"} tone="green" />
        <MetricCard label="模型" value={metrics?.models ?? "-"} />
        <MetricCard label="Redis" value={metrics?.redis ? "ok" : "off"} tone={metrics?.redis ? "green" : "red"} />
      </div>
      <div className="toolbarRow">
        <button onClick={() => train("static")}>
          <Activity size={16} />
          训练静态
        </button>
        <button onClick={() => train("dynamic")}>
          <Activity size={16} />
          训练动态
        </button>
        {job && <span>Job #{job.jobId}: {job.status}</span>}
      </div>
      <table>
        <thead>
          <tr>
            <th>名称</th>
            <th>模式</th>
            <th>准确率</th>
            <th>状态</th>
          </tr>
        </thead>
        <tbody>
          {models.map((model) => (
            <tr key={model.id}>
              <td>{model.name}</td>
              <td>{model.mode}</td>
              <td>{model.accuracy ?? "-"}</td>
              <td>{model.active ? "active" : "inactive"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
