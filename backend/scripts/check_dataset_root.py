from app.core.config import settings


def main() -> None:
    root = settings.dataset_root
    print(f"DATASET_ROOT: {root}")
    try:
        exists = root.exists()
    except OSError as exc:
        print(f"exists: false")
        print(f"访问失败: {exc}")
        print("如果是 WinError 1326，请先用 net use 登录 NAS 共享目录。")
        return

    print(f"exists: {exists}")
    if not exists:
        print("目录不可访问。请检查 NAS SMB 是否开启、共享名是否正确、账号是否已登录。")
        return

    static_csv = root / "features" / "static" / "gesture_data.csv"
    dynamic_dir = root / "features" / "dynamic"
    print(f"static csv: {static_csv} -> {static_csv.exists()}")
    print(f"dynamic dir: {dynamic_dir} -> {dynamic_dir.exists()}")
    if dynamic_dir.exists():
        labels = [path.name for path in dynamic_dir.iterdir() if path.is_dir()]
        print(f"dynamic labels: {labels}")


if __name__ == "__main__":
    main()
