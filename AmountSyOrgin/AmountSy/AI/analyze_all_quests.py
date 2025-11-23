import json
import os
from pathlib import Path

def analyze_scnlocjson(file_path):
    """分析单个scnlocjson文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        total_lines = 0
        choice_sections = 0
        total_sections = 0

        sections = data.get('SectionsInScene', [])
        total_sections = len(sections)

        for section in sections:
            lines = section.get('LinesInSection', [])
            total_lines += len(lines)

            if section.get('IsChoiceSection', False):
                choice_sections += 1

        return {
            'total_sections': total_sections,
            'total_lines': total_lines,
            'choice_sections': choice_sections,
            'success': True
        }
    except Exception as e:
        return {
            'total_sections': 0,
            'total_lines': 0,
            'choice_sections': 0,
            'success': False,
            'error': str(e)
        }

def analyze_quest_folder(quest_path):
    """分析任务文件夹"""
    scenes_path = os.path.join(quest_path, 'scenes')

    if not os.path.exists(scenes_path):
        return None

    total_lines = 0
    total_choices = 0
    total_scenes = 0
    total_sections = 0

    for file in os.listdir(scenes_path):
        if file.endswith('.scnlocjson'):
            file_path = os.path.join(scenes_path, file)
            stats = analyze_scnlocjson(file_path)
            # 关键改动：跳过versions文件夹（无论是否为目录）
            if file == 'versions':
                continue
            if stats['success']:
                total_lines += stats['total_lines']
                total_choices += stats['choice_sections']
                total_sections += stats['total_sections']
                total_scenes += 1

    if total_scenes == 0:
        return None

    return {
        'total_scenes': total_scenes,
        'total_lines': total_lines,
        'total_choices': total_choices,
        'total_sections': total_sections
    }

def scan_quest_directory(base_path):
    """扫描任务目录"""
    results = []

    if not os.path.exists(base_path):
        return results

    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)

        if os.path.isdir(item_path) and (item.startswith('q') or item.startswith('sq')or item.startswith('mq')or item.startswith('gym_smoketest')):
            stats = analyze_quest_folder(item_path)

            if stats:
                stats['quest_code'] = item
                stats['quest_path'] = item_path
                results.append(stats)

    return results

def main():
    # 扫描不同目录
    quest_types = [
        ('序章 (Prologue)',  r"D:\AppSoft\Sy2077\2077\2077\CDPR2077\r6\depot\base\quest\main_quests\prologue"),
        ('主线第一章 (Part 1)',  r"D:\AppSoft\Sy2077\2077\2077\CDPR2077\r6\depot\base\quest\main_quests\part1"),
        ('终章 (Epilogue)', r"D:\AppSoft\Sy2077\2077\2077\CDPR2077\r6\depot\base\quest\main_quests\epilogue"),
        ('支线 (Side Quests)', r"D:\AppSoft\Sy2077\2077\2077\CDPR2077\r6\depot\base\quest\side_quests"),
        ('小任务 (minor_quests Quests)', r"D:\AppSoft\Sy2077\2077\2077\CDPR2077\r6\depot\base\quest\minor_quests"),
        ('smok (smok_quests Quests)', r"D:\AppSoft\Sy2077\2077\2077\CDPR2077\r6\depot\non_production\gyms")
    ]

    all_results = {}

    for type_name, path in quest_types:
        if os.path.exists(path):
            results = scan_quest_directory(path)
            if results:
                all_results[type_name] = results

    # 打印结果
    print("=" * 100)
    print("《赛博朋克2077》任务对话与选择统计")
    print("=" * 100)
    print()

    for type_name, results in all_results.items():
        print(f"\n{'='*100}")
        print(f"{type_name}")
        print(f"{'='*100}")
        print(f"{'任务代码':<12} | {'Scene数':<8} | {'Section数':<10} | {'对话数':<10} | {'选择数':<8} | {'平均对话/Scene':<15}")
        print("-" * 100)

        total_scenes = 0
        total_lines = 0
        total_choices = 0
        total_sections = 0

        for result in sorted(results, key=lambda x: x['quest_code']):
            avg_lines = result['total_lines'] / result['total_scenes'] if result['total_scenes'] > 0 else 0

            print(f"{result['quest_code']:<12} | {result['total_scenes']:<8} | {result['total_sections']:<10} | "
                  f"{result['total_lines']:<10} | {result['total_choices']:<8} | {avg_lines:<15.1f}")

            total_scenes += result['total_scenes']
            total_lines += result['total_lines']
            total_choices += result['total_choices']
            total_sections += result['total_sections']

        print("-" * 100)
        avg_total = total_lines / total_scenes if total_scenes > 0 else 0
        print(f"{'小计':<12} | {total_scenes:<8} | {total_sections:<10} | "
              f"{total_lines:<10} | {total_choices:<8} | {avg_total:<15.1f}")
        print()

    # 总统计
    print("\n" + "=" * 100)
    print("总统计汇总")
    print("=" * 100)

    grand_total_scenes = 0
    grand_total_lines = 0
    grand_total_choices = 0
    grand_total_sections = 0

    for type_name, results in all_results.items():
        type_scenes = sum(r['total_scenes'] for r in results)
        type_lines = sum(r['total_lines'] for r in results)
        type_choices = sum(r['total_choices'] for r in results)
        type_sections = sum(r['total_sections'] for r in results)

        grand_total_scenes += type_scenes
        grand_total_lines += type_lines
        grand_total_choices += type_choices
        grand_total_sections += type_sections

        avg = type_lines / type_scenes if type_scenes > 0 else 0
        print(f"{type_name:<25} | Scenes: {type_scenes:<6} | 对话: {type_lines:<8} | 选择: {type_choices:<6} | 平均: {avg:.1f}")

    print("-" * 100)
    grand_avg = grand_total_lines / grand_total_scenes if grand_total_scenes > 0 else 0
    print(f"{'全游戏总计':<25} | Scenes: {grand_total_scenes:<6} | 对话: {grand_total_lines:<8} | 选择: {grand_total_choices:<6} | 平均: {grand_avg:.1f}")
    print()

if __name__ == '__main__':
    main()
