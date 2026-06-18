import argparse
from dataclasses import dataclass

from app.core.config import settings


@dataclass(frozen=True)
class DatasetInfo:
    name: str
    purpose: str
    size: str
    url: str
    command: str | None = None
    note: str = ""


DATASETS = {
    "hagrid": DatasetInfo(
        name="HaGRID",
        purpose="静态手势训练",
        size="约 552,992 张 FullHD 图像，Kaggle 页面标注约 716GB",
        url="https://www.kaggle.com/datasets/kapitanov/hagrid",
        command="kaggle datasets download -d kapitanov/hagrid -p data/raw/hagrid --unzip",
        note="需要 Kaggle 账号和 kaggle.json；建议先按类别抽样，不要直接全量训练。",
    ),
    "jester": DatasetInfo(
        name="20BN-Jester",
        purpose="动态手势训练",
        size="约 148,092 个视频目录，下载约 22.8GB",
        url="https://www.qualcomm.com/developer/software/jester-dataset",
        command=None,
        note="官方页面通常需要注册/同意许可；下载后放入 data/raw/jester。",
    ),
    "egogesture": DatasetInfo(
        name="EgoGesture",
        purpose="动态/静态混合训练",
        size="2,081 RGB-D 视频，24,161 手势样本，2,953,224 帧，83 类",
        url="https://nlpr.ia.ac.cn/iva/yfzhang/datasets/egogesture.html",
        command=None,
        note="研究用途数据集，按官方页面申请/下载。",
    ),
    "shrec": DatasetInfo(
        name="SHREC'17 / DHG-14/28",
        purpose="骨架动态手势基线",
        size="常用基准为 2,800 条序列，14/28 类，22 个手部关节",
        url="http://www-rech.telecom-lille.fr/shrec2017-hand/",
        command=None,
        note="适合做骨架序列论文实验；需把 22 关节映射/裁剪到本系统 21 点或单独训练基线。",
    ),
    "nvgesture": DatasetInfo(
        name="NVGesture",
        purpose="动态手势扩展",
        size="约 1,532 个动态手势，25 类，RGB/Depth/IR",
        url="https://research.nvidia.com/publication/2016-06_online-detection-and-classification-dynamic-hand-gestures-recurrent-3d",
        command=None,
        note="适合车载/非接触交互扩展，下载源可能需要按论文页入口申请。",
    ),
}


def print_dataset(info: DatasetInfo) -> None:
    print(f"\n[{info.name}]")
    print(f"用途: {info.purpose}")
    print(f"规模: {info.size}")
    print(f"入口: {info.url}")
    if info.command:
        print(f"下载命令: {info.command}")
    print(f"说明: {info.note}")
    print(f"建议保存到: {settings.dataset_root / 'raw' / info.name.lower().replace(' ', '_').replace('/', '_')}")


def main() -> None:
    parser = argparse.ArgumentParser(description="公开手势数据集下载入口和命令提示")
    parser.add_argument("--dataset", choices=[*DATASETS.keys(), "all"], default="all")
    parser.add_argument("--dry-run", action="store_true", help="只打印入口和命令，不执行下载")
    args = parser.parse_args()

    selected = DATASETS.values() if args.dataset == "all" else [DATASETS[args.dataset]]
    for info in selected:
        print_dataset(info)
        if not args.dry_run and info.command:
            print("\n为避免误下载超大数据集，本脚本默认不自动执行命令。请确认磁盘空间和许可后手动运行上面的命令。")


if __name__ == "__main__":
    main()
