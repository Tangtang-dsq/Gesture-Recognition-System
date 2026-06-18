# 手势识别系统的设计与实现

基于 B/S 架构的手势识别系统：浏览器端用 MediaPipe 提取 21 个手部关键点，WebSocket 上传 63 维归一化特征，FastAPI 后端完成分类、采集、训练任务和模型管理。数据库与 Redis 使用 Docker Compose 启动。

## 快速启动

```powershell
docker compose up -d

cd backend
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
$env:PYTHONPATH="."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

cd ..\\frontend
npm install
npm run dev
```

打开 `http://localhost:5173`。

## 验证

```powershell
cd backend
$env:PYTHONPATH="."
pytest

cd ..\\frontend
npm test
npm run build
```

## 模型训练

采集足量样本后运行：

```powershell
cd backend
$env:PYTHONPATH="."
python scripts/train_static.py
python scripts/train_dynamic.py
```

训练产物会保存到 `backend/app/models/`，后端启动时自动加载；没有模型文件时会使用规则分类器兜底，便于先联调端到端链路。
