# 群晖 NAS 数据挂载与训练

## 推荐方式：SMB 共享挂载到 Windows

1. 在群晖 DSM 中打开 `控制面板 -> 文件服务 -> SMB`，启用 SMB。
2. 新建或确认共享文件夹，例如你当前提供的共享应类似 `aisd`。
3. 给当前训练账号授予读写权限。
4. Windows 本机把共享目录映射为盘符：

```powershell
net use Z: "\\NAS_IP\gesture-data" /user:NAS用户名 * /persistent:yes
```

也可以不用盘符，直接使用 UNC 路径：

```text
\\NAS_IP\gesture-data
```

盘符方式对 Python、PowerShell 和 IDE 更友好，推荐使用 `Z:\gesture-data`。

## 项目配置

在项目根目录创建 `.env`：

```env
DATABASE_URL=postgresql+psycopg://gesture:gesture@localhost:5432/gesture
REDIS_URL=redis://localhost:6379/0
DATASET_ROOT=Z:/gesture-data
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Windows 路径建议在 `.env` 中写成 `/`：

```env
DATASET_ROOT=Z:/gesture-data
```

UNC 路径也可以：

```env
DATASET_ROOT=//NAS_IP/gesture-data
```

## 当前 NAS 示例

你提供的 DSM 管理地址是：

```text
http://192.168.100.235:5000/
```

你提供的 NAS 内部目录是：

```text
/aisd/zhangxu/shoushi_data
```

在 Windows 上，训练脚本不能直接用 DSM 网页地址访问文件，需要通过 SMB 共享访问。若 `aisd` 是群晖共享文件夹名称，则对应路径是：

```text
\\192.168.100.235\aisd\zhangxu\shoushi_data
```

如果不映射盘符，项目 `.env` 可以写成：

```env
DATASET_ROOT=//192.168.100.235/aisd/zhangxu/shoushi_data
```

更推荐先映射为 `Z:` 盘：

```powershell
net use Z: "\\192.168.100.235\aisd" /user:NAS用户名 * /persistent:yes
```

映射成功后 `.env` 写：

```env
DATASET_ROOT=Z:/zhangxu/shoushi_data
```

## NAS 上的数据目录结构

训练脚本会优先读取 PostgreSQL 中 Web 采集页保存的样本。如果数据库里没有样本，就读取 `DATASET_ROOT` 下的离线特征文件：

```text
Z:/gesture-data/
├── raw/
│   ├── hagrid/
│   ├── jester/
│   ├── egogesture/
│   ├── shrec/
│   ├── nvgesture/
│   └── custom/
└── features/
    ├── static/
    │   └── gesture_data.csv
    └── dynamic/
        ├── swipe_left/
        │   ├── seq_0001.npy
        │   └── seq_0002.npy
        ├── swipe_right/
        └── none/
```

当前已经在 NAS `Z:/zhangxu/shoushi_data` 下创建好：

```text
raw/hagrid
raw/jester
raw/egogesture
raw/shrec
raw/nvgesture
raw/custom
features/static
features/dynamic/none
features/dynamic/swipe_left
features/dynamic/swipe_right
features/dynamic/swipe_up
features/dynamic/swipe_down
features/dynamic/zoom_in
features/dynamic/zoom_out
models
reports
tmp
```

静态 CSV 格式：

```csv
label,x0,y0,z0,x1,y1,z1,...,x20,y20,z20
palm,0,0,0,0.1,-0.2,0,...
fist,0,0,0,0.08,-0.1,0,...
```

动态 `.npy` 文件要求每个文件形状为：

```text
(30, 63)
```

## 训练命令

```powershell
cd F:\project\手势识别系统的设计与实现\backend
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH="."
python scripts/train_static.py
python scripts/train_dynamic.py
```

如果临时不想写 `.env`，也可以只在当前 PowerShell 会话设置：

```powershell
$env:DATASET_ROOT="Z:/gesture-data"
python scripts/train_static.py
```

## 注意事项

- 不要把 NAS 原始图片/视频提交到 Git，项目已经忽略 `data/`。
- 大数据训练时，建议先把公开数据转换成 63 维关键点特征再训练；直接从 NAS 反复读取海量图片/视频会很慢。
- 如果训练速度慢，优先把 `features/` 缓存在本机 SSD，原始数据继续放 NAS。
- 如果未来把后端训练也放进 Docker，需要把 NAS 路径作为 volume 挂载进容器。
