#!/usr/bin/env python3
import os
import glob
import datetime

# 基础路径设置
#BASE_DIR = r"D:\AppSoft\Sy2077\2077\2077\CDPR2077\r6\depot\base\quest\main_quests\epilogue"
#TARGET_FOLDERS = ["q200", "q201", "q202", "q203", "q204"]  # 要统计的目标文件夹
#OUTPUT_FILE = r"D:\Data\PYh\AmountSy\Out\main_quests_statistics.txt"
#CSV_FILE = r"D:\Data\PYh\AmountSy\Out\main_quests_statistics.csv"
#BASE_DIR = r"D:\AppSoft\Sy2077\2077\2077\CDPR2077\r6\depot\base\quest\main_quests\part1"
#TARGET_FOLDERS = ["q101", "q103", "q104", "q105", "q108","q110","q112",'q113',"q114","q115","q116"]  # 要统计的目标文件夹
#OUTPUT_FILE = r"D:\Data\PYh\AmountSy\Out\main_quests_Part1_statistics.txt"
#CSV_FILE = r"D:\Data\PYh\AmountSy\Out\main_quests_Part1_statistics.csv"
#BASE_DIR = r"D:\AppSoft\Sy2077\2077\2077\CDPR2077\r6\depot\base\quest\main_quests\prologue"
#TARGET_FOLDERS = ["q000", "q001", "q003", "q004", "q005"]  # 要统计的目标文件夹
#OUTPUT_FILE = r"D:\Data\PYh\AmountSy\Out\main_quests_prologue_statistics.txt"
#CSV_FILE = r"D:\Data\PYh\AmountSy\Out\main_quests_prologue_statistics.csv"
# !/usr/bin/env python3
import os
import glob
import datetime

# 路径设置
BASE_DIR = r"D:\AppSoft\Sy2077\2077\2077\CDPR2077\r6\depot\base\quest\main_quests\epilogue"
OUTPUT_FILE = r"D:\Data\PYh\AmountSy\Out\epilogue_quests_statistics.txt"
CSV_FILE = r"D:\Data\PYh\AmountSy\Out\epilogue_quests_statistics.csv"


def count_files(folder_path):
    """统计指定文件夹及其子文件夹中目标文件的数量"""
    questphase = len(glob.glob(os.path.join(folder_path, "**", "*.questphase"), recursive=True))
    scenesolution = len(glob.glob(os.path.join(folder_path, "**", "*.scenesolution"), recursive=True))
    return questphase, scenesolution


def main():
    # 动态获取BASE_DIR下的第一层子文件夹名称（仅文件夹，排除文件）
    TARGET_FOLDERS = []
    if os.path.isdir(BASE_DIR):
        # 遍历BASE_DIR下的所有条目
        for item in os.listdir(BASE_DIR):
            item_path = os.path.join(BASE_DIR, item)
            # 只保留文件夹，且是第一层子目录
            if os.path.isdir(item_path) and not os.path.islink(item_path):
                TARGET_FOLDERS.append(item)

    # 如果没有找到子文件夹，直接退出
    if not TARGET_FOLDERS:
        print(f"警告：在 {BASE_DIR} 下未找到任何子文件夹")
        return

    # 确保输出目录存在
    output_dir = os.path.dirname(OUTPUT_FILE)
    os.makedirs(output_dir, exist_ok=True)

    # 初始化输出文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("Side Quests 文件夹统计报告\n")
        f.write(f"生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"统计根目录: {BASE_DIR}\n")
        f.write("========================================\n\n")

    # 初始化CSV文件
    with open(CSV_FILE, 'w', encoding='utf-8') as f:
        f.write("文件夹名称,QuestPhase文件数,SceneSolution文件数\n")

    # 统计每个目标文件夹
    total_questphase = 0
    total_scenesolution = 0

    with open(OUTPUT_FILE, 'a', encoding='utf-8') as txt_f:
        for folder in TARGET_FOLDERS:
            folder_path = os.path.join(BASE_DIR, folder)

            # 再次确认文件夹存在（防止遍历后被删除的极端情况）
            if not os.path.isdir(folder_path):
                print(f"警告: 文件夹 {folder} 不存在，已跳过")
                txt_f.write(f"警告: 文件夹 {folder} 不存在，已跳过\n")
                continue

            # 统计文件
            qp_count, ss_count = count_files(folder_path)
            total_questphase += qp_count
            total_scenesolution += ss_count

            # 写入文本报告
            txt_f.write(f"文件夹: {folder}\n")
            txt_f.write(f"  路径: {folder_path}\n")  # 增加路径显示，方便核对
            txt_f.write(f"  QuestPhase 文件数: {qp_count}\n")
            txt_f.write(f"  SceneSolution 文件数: {ss_count}\n")
            txt_f.write("----------------------------------------\n")

            # 写入CSV
            with open(CSV_FILE, 'a', encoding='utf-8') as csv_f:
                csv_f.write(f"{folder},{qp_count},{ss_count}\n")

    # 写入总计
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        f.write("\n========================================\n")
        f.write("总计\n")
        f.write("========================================\n")
        f.write(f"总文件夹数: {len(TARGET_FOLDERS)}\n")
        f.write(f"总 QuestPhase 文件数: {total_questphase}\n")
        f.write(f"总 SceneSolution 文件数: {total_scenesolution}\n")

    # 控制台输出结果
    print("\n统计完成！")
    print(f"共统计 {len(TARGET_FOLDERS)} 个文件夹")
    print(f"目标文件夹: {', '.join(TARGET_FOLDERS)}")
    print(f"总 QuestPhase 文件数: {total_questphase}")
    print(f"总 SceneSolution 文件数: {total_scenesolution}")
    print(f"详细报告: {OUTPUT_FILE}")
    print(f"CSV数据: {CSV_FILE}")


if __name__ == "__main__":
    main()