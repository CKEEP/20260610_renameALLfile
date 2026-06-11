import os
import json
from datetime import datetime

SCRIPT_NAME = os.path.basename(__file__)
folder = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(folder, ".rename_log.json")


def do_rename():
    """将文件夹内所有文件重命名为修改日期时间"""
    log = {}  # new_name -> old_name

    for filename in os.listdir(folder):
        filepath = os.path.join(folder, filename)
        if not os.path.isfile(filepath):
            continue
        if filename == SCRIPT_NAME or filename.startswith(".rename_log"):
            continue

        mtime = os.path.getmtime(filepath)
        dt = datetime.fromtimestamp(mtime)
        new_name = dt.strftime("%Y%m%d%H%M")
        _, ext = os.path.splitext(filename)
        new_filepath = os.path.join(folder, new_name + ext)

        # 处理重名冲突
        counter = 1
        base_new = os.path.join(folder, new_name)
        while os.path.exists(new_filepath):
            new_filepath = f"{base_new}_{counter}{ext}"
            counter += 1

        os.rename(filepath, new_filepath)
        log[os.path.basename(new_filepath)] = filename
        print(f"{filename} -> {os.path.basename(new_filepath)}")

    if log:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(log, f, ensure_ascii=False, indent=2)
        print(f"\n重命名完成！共处理 {len(log)} 个文件。")
        print(f"如需撤回，请再次运行本脚本并选择「撤回」。")
    else:
        print("没有需要重命名的文件。")


def do_undo():
    """根据日志文件撤回所有重命名操作"""
    if not os.path.exists(LOG_FILE):
        print("没有找到重命名记录，无法撤回。")
        return

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        log = json.load(f)  # new_name -> old_name

    if not log:
        print("重命名记录为空，无需撤回。")
        return

    success = 0
    failed = 0

    for new_name, old_name in log.items():
        new_path = os.path.join(folder, new_name)
        old_path = os.path.join(folder, old_name)

        if not os.path.exists(new_path):
            print(f"[跳过] {new_name} 不存在，可能已被移动或删除")
            failed += 1
            continue

        if os.path.exists(old_path):
            print(f"[跳过] {new_name} -> {old_name} 目标已存在，冲突")
            failed += 1
            continue

        os.rename(new_path, old_path)
        print(f"{new_name} -> {old_name}")
        success += 1

    # 撤回成功后删除日志
    if failed == 0:
        os.remove(LOG_FILE)
        print(f"\n撤回完成！共恢复 {success} 个文件。重命名记录已清除。")
    else:
        print(f"\n撤回部分完成：成功 {success} 个，失败 {failed} 个。")
        print("重命名记录已保留，解决冲突后可再次尝试撤回。")


if __name__ == "__main__":
    print("=" * 50)
    print("  文件批量重命名（按修改日期时间）")
    print("=" * 50)

    # 检测检测是否存在撤回记录
    has_log = os.path.exists(LOG_FILE)

    if has_log:
        print(f"\n检测到上次重命名记录（{LOG_FILE}）")
        print("  [1] 执行重命名")
        print("  [2] 撤回上次重命名")
        choice = input("\n请选择 (1/2): ").strip()
        if choice == "2":
            do_undo()
        else:
            # 删除旧日志，重新开始
            os.remove(LOG_FILE)
            do_rename()
    else:
        print(f"\n目标文件夹: {folder}")
        confirm = input("确认重命名所有文件？(y/n): ").strip().lower()
        if confirm == "y":
            do_rename()
        else:
            print("已取消。")