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
| `features/static/gesture_data.csv` | HaGRID 抽样并按标注框裁剪提取：`fist`、`like`、`ok`、`one`、`two_up`、`three`、`four`、`palm`、`stop`、`peace` | 已生成 7228 条有效样本 |

## 已训练模型

| 模型 | 类别 | 测试准确率 | 状态 |
| --- | --- | --- | --- |
| `backend/app/models/static_classifier.joblib` | `fist`、`thumbs_up`、`ok`、`number_1`、`number_2`、`number_3`、`number_4`、`palm`、`peace` | 0.9734 | 当前静态模型 |

## 下一步

1. 继续补充 `number_5`、`point` 等 HaGRID 当前样本包未覆盖或映射不足的静态类别。
2. 继续下载/整理动态手势数据集，用于训练动态模型。
3. 用本项目采集页补采本地摄像头样本，微调模型以适配答辩环境。
