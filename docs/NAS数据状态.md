# NAS 数据状态

更新时间：2026-06-18

## 已放入 NAS 的原始数据

| 数据集 | 路径 | 文件 | 状态 |
| --- | --- | --- | --- |
| HaGRID 384p 样本版 | `Z:/zhangxu/shoushi_data/raw/hagrid/` | `hagrid-sample-500k-384p.zip` | 已到位，约 13.4GB |

## 下一步

## 已生成的训练特征

| 特征文件 | 数据来源 | 状态 |
| --- | --- | --- |
| `features/static/gesture_data.csv` | HaGRID 已解压类别抽样：`fist`、`like`、`ok`、`one`、`four` | 已生成 1977 条有效样本 |

## 已训练模型

| 模型 | 类别 | 测试准确率 | 状态 |
| --- | --- | --- | --- |
| `backend/app/models/static_classifier.joblib` | `fist`、`thumbs_up`、`ok`、`number_1`、`number_4` | 0.9232 | 第二版可用模型 |

## 下一步

1. 等待 `raw/hagrid/hagrid-sample-500k-384p.zip` 完整解压完成。
2. 扩大静态特征提取类别和每类样本数。
3. 重新运行 `backend/scripts/train_static.py` 训练更完整的静态手势模型。
4. 继续下载/整理动态手势数据集，用于训练动态模型。
