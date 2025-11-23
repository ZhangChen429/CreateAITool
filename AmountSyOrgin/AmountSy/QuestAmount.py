#!/usr/bin/env python3
import os
import glob
import datetime

# 使用原始字符串处理Windows路径，避免转义问题
QUEST_BASE = r"D:\AppSoft\Sy2077\2077\2077\CDPR2077\r6\depot\base\quest"
OUTPUT_FILE = r"D:\Data\PYh\AmountSy\Out\quest_statistics.txt"
CSV_FILE = r"D:\Data\PYh\AmountSy\Out\quest_statistics.csv"

# 初始化计数器
total_questphase = 0
total_scenesolution = 0
total_quests = 0


def count_quest(quest_dir, quest_name, category, output_file, csv_file):
    """统计指定任务目录及其所有子文件夹中的文件数量"""
    global total_questphase, total_scenesolution, total_quests

    # 递归搜索所有子文件夹中的目标文件（**表示所有子目录）
    questphase_count = len(glob.glob(os.path.join(quest_dir, "**", "*.questphase"), recursive=True))
    scenesolution_count = len(glob.glob(os.path.join(quest_dir, "**", "*.scenesolution"), recursive=True))

    # 写入CSV文件
    with open(csv_file, 'a', encoding='utf-8') as f:
        f.write(f"{category},{quest_name},{questphase_count},{scenesolution_count}\n")

    # 写入文本报告
    with open(output_file, 'a', encoding='utf-8') as f:
        line = f"{category:20} {quest_name:15} QuestPhase: {questphase_count:3d}  SceneSolution: {scenesolution_count:3d}\n"
        f.write(line)

    # 更新总计
    total_questphase += questphase_count
    total_scenesolution += scenesolution_count
    total_quests += 1


def main():
    # 确保输出目录存在
    output_dir = os.path.dirname(OUTPUT_FILE)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # 初始化输出文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("任务文件统计报告\n")
        f.write(f"生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("========================================\n\n")

    # 初始化CSV文件
    with open(CSV_FILE, 'w', encoding='utf-8') as f:
        f.write("分类,任务代号,QuestPhase文件数,SceneSolution文件数\n")

    # 扫描序章任务
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        f.write("【主线任务 - 序章 Prologue】\n")
        f.write("----------------------------------------\n")

    prologue_dirs = glob.glob(os.path.join(QUEST_BASE, "main_quests", "prologue", "q*", ""))
    for quest_dir in prologue_dirs:
        if os.path.isdir(quest_dir):
            quest_name = os.path.basename(os.path.dirname(quest_dir))
            count_quest(quest_dir, quest_name, "主线-序章", OUTPUT_FILE, CSV_FILE)

    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        f.write("\n")

    # 扫描第一章任务
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        f.write("【主线任务 - 第一章 Part 1】\n")
        f.write("----------------------------------------\n")

    part1_dirs = glob.glob(os.path.join(QUEST_BASE, "main_quests", "part1", "q*", ""))
    for quest_dir in part1_dirs:
        if os.path.isdir(quest_dir):
            quest_name = os.path.basename(os.path.dirname(quest_dir))
            count_quest(quest_dir, quest_name, "主线-第一章", OUTPUT_FILE, CSV_FILE)

    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        f.write("\n")

    # 扫描结局任务
    epilogue_base = os.path.join(QUEST_BASE, "main_quests", "epilogue")
    if os.path.isdir(epilogue_base):
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
            f.write("【主线任务 - 结局 Epilogue】\n")
            f.write("----------------------------------------\n")

        epilogue_dirs = glob.glob(os.path.join(epilogue_base, "ep*", ""))
        for quest_dir in epilogue_dirs:
            if os.path.isdir(quest_dir):
                quest_name = os.path.basename(os.path.dirname(quest_dir))
                count_quest(quest_dir, quest_name, "主线-结局", OUTPUT_FILE, CSV_FILE)

        with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
            f.write("\n")

    # 扫描支线任务
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        f.write("【支线任务 Side Quests】\n")
        f.write("----------------------------------------\n")

    side_dirs = glob.glob(os.path.join(QUEST_BASE, "side_quests", "sq*", ""))
    for quest_dir in side_dirs:
        if os.path.isdir(quest_dir):
            quest_name = os.path.basename(os.path.dirname(quest_dir))
            count_quest(quest_dir, quest_name, "支线任务", OUTPUT_FILE, CSV_FILE)

    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        f.write("\n")

    # 扫描次要任务
    minor_base = os.path.join(QUEST_BASE, "minor_quests")
    if os.path.isdir(minor_base):
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
            f.write("【次要任务 Minor Quests】\n")
            f.write("----------------------------------------\n")

        minor_dirs = glob.glob(os.path.join(minor_base, "mq*", ""))
        for quest_dir in minor_dirs:
            if os.path.isdir(quest_dir):
                quest_name = os.path.basename(os.path.dirname(quest_dir))
                count_quest(quest_dir, quest_name, "次要任务", OUTPUT_FILE, CSV_FILE)

        with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
            f.write("\n")

    # 写入统计汇总
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        f.write("========================================\n")
        f.write("统计汇总\n")
        f.write("========================================\n")
        f.write(f"总任务数: {total_quests}\n")
        f.write(f"总 QuestPhase 文件数: {total_questphase}\n")
        f.write(f"总 SceneSolution 文件数: {total_scenesolution}\n")

    # 输出到控制台
    print("\n统计完成！")
    print(f"总任务数: {total_quests}")
    print(f"总 QuestPhase 文件数: {total_questphase}")
    print(f"总 SceneSolution 文件数: {total_scenesolution}\n")
    print(f"详细报告已保存到: {OUTPUT_FILE}")
    print(f"CSV 文件已保存到: {CSV_FILE}")


if __name__ == "__main__":
    main()