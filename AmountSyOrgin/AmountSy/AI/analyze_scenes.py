import json
import os
import sys
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
            # 统计对话行数
            lines = section.get('LinesInSection', [])
            total_lines += len(lines)

            # 统计选择section
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
    """分析任务文件夹下的所有scene"""
    scenes_path = os.path.join(quest_path, 'scenes')

    if not os.path.exists(scenes_path):
        return []

    results = []

    # 遍历scenes文件夹下的所有scnlocjson文件
    for file in os.listdir(scenes_path):
        if file.endswith('.scnlocjson'):
            file_path = os.path.join(scenes_path, file)
            scene_name = file.replace('.scnlocjson', '')

            stats = analyze_scnlocjson(file_path)
            stats['scene_name'] = scene_name
            stats['file_name'] = file

            results.append(stats)

    return results

def main():
    if len(sys.argv) < 2:
        print("用法: python analyze_scenes.py <quest_folder_path>")
        print("示例: python analyze_scenes.py D:/AppSoft/Sy2077/2077/2077/CDPR2077/r6/depot/non_production/gyms/gym_smoketest")
        sys.exit(1)

    quest_path = sys.argv[1]

    if not os.path.exists(quest_path):
        print(f"错误: 路径不存在 {quest_path}")
        sys.exit(1)

    results = analyze_quest_folder(quest_path)

    if not results:
        print(f"在 {quest_path}/scenes 中没有找到scnlocjson文件")
        sys.exit(1)

    # 打印结果
    print(f"\n{'Scene名称':<40} | {'对话数':<8} | {'选择数':<8} | {'Section数':<10}")
    print("-" * 80)

    total_lines = 0
    total_choices = 0
    total_scenes = 0

    for result in sorted(results, key=lambda x: x['scene_name']):
        if result['success']:
            print(f"{result['scene_name']:<40} | {result['total_lines']:<8} | {result['choice_sections']:<8} | {result['total_sections']:<10}")
            total_lines += result['total_lines']
            total_choices += result['choice_sections']
            total_scenes += 1
        else:
            print(f"{result['scene_name']:<40} | 错误: {result.get('error', 'Unknown')}")

    print("-" * 80)
    print(f"{'总计':<40} | {total_lines:<8} | {total_choices:<8} | {total_scenes} scenes")
    print()
    print(f"平均每个Scene: {total_lines/total_scenes:.1f} 对话, {total_choices/total_scenes:.1f} 选择")

if __name__ == '__main__':
    main()
