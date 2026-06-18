# NAS 数据状态

更新时间：2026-06-18

## 已放入 NAS 的原始数据

| 数据集 | 路径 | 文件 | 状态 |
| --- | --- | --- | --- |
| HaGRID 384p 样本版 | `Z:/zhangxu/shoushi_data/raw/hagrid/` | `hagrid-sample-500k-384p.zip` | 已到位，约 13.4GB |

## 下一步

1. 解压 `raw/hagrid/hagrid-sample-500k-384p.zip`。
2. 对图片运行 MediaPipe Hands，提取 21 个关键点。
3. 按系统一致规则归一化为 63 维特征。
4. 输出到 `features/static/gesture_data.csv`。
5. 运行 `backend/scripts/train_static.py` 训练静态手势模型。
