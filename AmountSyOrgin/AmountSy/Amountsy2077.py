import os
import re
import csv
from pathlib import Path
from collections import defaultdict

# 配置参数
BASE_DIR = Path(r"D:\AppSoft\Sy2077\2077\2077\CDPR2077\r6\depot\base\quest")
CSV_PATH = Path(r"D:\Data\PYh\AmountSy\Out\quest_assets_report.csv")

# 核心资产类型分类（与原脚本保持一致）
ASSET_TYPES = {
    "任务系统": [".quest", ".questphase", ".gamedef"],
    "场景系统": [".scene", ".scenesolution", ".scnlocjson"],
    "实体系统": [".ent", ".app", ".rig"],
    "世界构建": [".prefab", ".streamingsector", ".world"],
    "AI行为": [".community", ".workspot"],
    "配置系统": [".json", ".tweak", ".script"],
}


def count_assets(path: Path, quest_name: str) -> dict:
    """统计单个任务目录的资产数量"""
    print(f"\n========== {quest_name} ==========")

    category_totals = defaultdict(int)
    grand_total = 0

    for category, exts in ASSET_TYPES.items():
        category_count = 0
        print(f"\n[{category}]")

        for ext in exts:
            # 递归查找所有符合扩展名的文件
            file_count = sum(1 for _ in path.rglob(f"*{ext}"))
            if file_count > 0:
                print(f"  {ext} : {file_count}")
                category_count += file_count

        if category_count > 0:
            category_totals[category] = category_count
            grand_total += category_count
            print(f"  小计: {category_count}")  # 黄色输出可在终端用colorama实现

    print(f"\n总计核心资产: {grand_total}")  # 绿色输出
    return {
        "Name": quest_name,
        "Total": grand_total,
        "Categories": category_totals
    }


def main():
    results = []

    # 1. 主线任务 - Prologue
    print("\n#################### 主线任务 - Prologue ####################")
    prologue_path = BASE_DIR / "main_quests" / "prologue"
    if prologue_path.exists():
        for dir in prologue_path.iterdir():
            if dir.is_dir():
                result = count_assets(dir, f"Prologue/{dir.name}")
                results.append(result)

    # 2. 主线任务 - Part1
    print("\n\n#################### 主线任务 - Part1 ####################")
    part1_path = BASE_DIR / "main_quests" / "part1"
    if part1_path.exists():
        for dir in part1_path.iterdir():
            if dir.is_dir():
                result = count_assets(dir, f"Part1/{dir.name}")
                results.append(result)

    # 3. 主线任务 - Epilogue
    print("\n\n#################### 主线任务 - Epilogue ####################")
    epilogue_path = BASE_DIR / "main_quests" / "epilogue"
    if epilogue_path.exists():
        for dir in epilogue_path.iterdir():
            if dir.is_dir():
                result = count_assets(dir, f"Epilogue/{dir.name}")
                results.append(result)

    # 4. 支线任务（匹配sq开头的目录）
    print("\n\n#################### 支线任务 ####################")
    side_quests_path = BASE_DIR / "side_quests"
    if side_quests_path.exists():
        for dir in side_quests_path.iterdir():
            if dir.is_dir() and re.match(r"^sq\d+", dir.name):
                result = count_assets(dir, f"SideQuest/{dir.name}")
                results.append(result)

    # 5. 次要任务（匹配mq开头的目录）
    print("\n\n#################### 次要任务 ####################")
    minor_quests_path = BASE_DIR / "minor_quests"
    if minor_quests_path.exists():
        for dir in minor_quests_path.iterdir():
            if dir.is_dir() and re.match(r"^mq\d+", dir.name):
                result = count_assets(dir, f"MinorQuest/{dir.name}")
                results.append(result)

    # 生成汇总报告
    print("\n\n#################### 汇总统计 ####################")
    print("\n任务资产量排行榜（Top 20）:")
    # 按资产总数降序排序
    sorted_results = sorted(results, key=lambda x: x["Total"], reverse=True)
    for item in sorted_results[:20]:
        print(f"{item['Name']} : {item['Total']} 个核心资产")

    # 计算总计
    total_assets = sum(item["Total"] for item in results)
    print(f"\n所有任务总计: {total_assets} 个核心资产")
    print(f"任务总数: {len(results)}")

    # 导出到CSV
    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "QuestName", "TotalAssets",
            "TaskSystem", "SceneSystem", "EntitySystem",
            "WorldBuilding", "AIBehavior", "ConfigSystem"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for item in results:
            writer.writerow({
                "QuestName": item["Name"],
                "TotalAssets": item["Total"],
                "TaskSystem": item["Categories"].get("任务系统", 0),
                "SceneSystem": item["Categories"].get("场景系统", 0),
                "EntitySystem": item["Categories"].get("实体系统", 0),
                "WorldBuilding": item["Categories"].get("世界构建", 0),
                "AIBehavior": item["Categories"].get("AI行为", 0),
                "ConfigSystem": item["Categories"].get("配置系统", 0),
            })

    print(f"\n详细报告已导出到: {CSV_PATH}")


if __name__ == "__main__":
    main()