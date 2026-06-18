import { Camera, Hand, Pause, Play, Send } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { MetricCard } from "../components/MetricCard.jsx";
import { StatusPill } from "../components/StatusPill.jsx";
import { createDemoFeature, normalizeLandmarks } from "../lib/features.js";
import { gestureName, modeName } from "../lib/gestureLabels.js";
import { createHandLandmarker } from "../lib/handLandmarker.js";
import { createGestureSocket } from "../lib/socket.js";
import { drawSkeleton } from "../lib/draw.js";

export function RecognizeView() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const landmarkerRef = useRef(null);
  const socketRef = useRef(null);
  const rafRef = useRef(null);
  const lastSendRef = useRef(0);
  const lastFrameRef = useRef(performance.now());
  const [mode, setMode] = useState("static");
  const [running, setRunning] = useState(false);
  const [status, setStatus] = useState("idle");
  const [cameraStatus, setCameraStatus] = useState("idle");
  const [modelStatus, setModelStatus] = useState("idle");
  const [result, setResult] = useState({ label: null, rawLabel: null, confidence: 0 });
  const [fps, setFps] = useState(0);
  const [latency, setLatency] = useState(0);

  useEffect(() => {
    socketRef.current = createGestureSocket({
      onStatus: setStatus,
      onResult: (message) => {
        setResult(message);
        if (message.ts) setLatency(Date.now() - message.ts);
      },
    });
    return () => socketRef.current?.close();
  }, []);

  useEffect(() => {
    socketRef.current?.send({ type: "reset" });
  }, [mode]);

  async function start() {
    setRunning(true);
    setCameraStatus("starting");
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { width: 960, height: 540, facingMode: "user" },
      audio: false,
    });
    videoRef.current.srcObject = stream;
    await videoRef.current.play();
    setCameraStatus("ready");

    if (!landmarkerRef.current) {
      setModelStatus("loading");
      landmarkerRef.current = await createHandLandmarker();
      setModelStatus("ready");
    }
    loop();
  }

  function stop() {
    setRunning(false);
    cancelAnimationFrame(rafRef.current);
    const stream = videoRef.current?.srcObject;
    stream?.getTracks().forEach((track) => track.stop());
    setCameraStatus("idle");
  }

  function loop(now = performance.now()) {
    const canvas = canvasRef.current;
    const video = videoRef.current;
    if (!canvas || !video || video.readyState < 2) {
      rafRef.current = requestAnimationFrame(loop);
      return;
    }

    canvas.width = video.videoWidth || 960;
    canvas.height = video.videoHeight || 540;
    const detection = landmarkerRef.current?.detectForVideo(video, now);
    const landmarks = detection?.landmarks?.[0];
    drawSkeleton(canvas, landmarks);

    const frameDelta = now - lastFrameRef.current;
    if (frameDelta > 0) setFps(Math.round(1000 / frameDelta));
    lastFrameRef.current = now;

    if (landmarks && now - lastSendRef.current > 50) {
      socketRef.current?.send({
        type: "frame",
        mode,
        feature: normalizeLandmarks(landmarks),
        ts: Date.now(),
      });
      lastSendRef.current = now;
    }
    rafRef.current = requestAnimationFrame(loop);
  }

  function sendDemo(kind) {
    socketRef.current?.send({ type: "frame", mode: "static", feature: createDemoFeature(kind), ts: Date.now() });
  }

  return (
    <section className="workspace">
      <div className="stage">
        <div className="videoSurface">
          <video ref={videoRef} muted playsInline />
          <canvas ref={canvasRef} />
          <div className="videoTopbar">
            <StatusPill status={status} />
            <StatusPill status={modelStatus} />
          </div>
        </div>
        <div className="controlRail">
          <button className="primaryButton" onClick={running ? stop : start}>
            {running ? <Pause size={18} /> : <Play size={18} />}
            {running ? "停止" : "启动"}
          </button>
          <div className="segmented">
            <button className={mode === "static" ? "active" : ""} onClick={() => setMode("static")}>
              静态
            </button>
            <button className={mode === "dynamic" ? "active" : ""} onClick={() => setMode("dynamic")}>
              动态
            </button>
          </div>
          <button className="iconButton" title="发送掌形样本" onClick={() => sendDemo("palm")}>
            <Send size={18} />
          </button>
        </div>
      </div>

      <aside className="sidePanel">
        <div className="resultBlock">
          <Hand size={26} />
          <div>
            <span>识别结果</span>
            <strong>{gestureName(result.label ?? result.rawLabel)}</strong>
          </div>
        </div>
        <div className="confidence">
          <span>置信度</span>
          <meter min="0" max="1" value={result.confidence ?? 0} />
          <b>{Math.round((result.confidence ?? 0) * 100)}%</b>
        </div>
        <div className="metricsGrid">
          <MetricCard label="FPS" value={fps} tone="green" />
          <MetricCard label="延迟" value={`${latency}ms`} tone="amber" />
          <MetricCard label="摄像头" value={cameraStatus} />
          <MetricCard label="模式" value={modeName(mode)} />
        </div>
        <div className="sampleButtons">
          {["palm", "fist", "peace", "point", "thumbs_up"].map((item) => (
            <button key={item} onClick={() => sendDemo(item)}>
              <Camera size={16} />
              {gestureName(item)}
            </button>
          ))}
        </div>
      </aside>
    </section>
  );
}
