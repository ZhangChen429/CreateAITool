#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析.scnlocjson文件中的Section统计信息（含图表可视化）
- 主线任务（main_quests）：按 qxxx 级别统计（向上两层）
- 支线任务（side_quests）/小任务（minor_quests）：保持原层级统计
- 所有结果统一输出到一个表格
"""

import json
import os
from pathlib import Path
from collections import defaultdict
import csv
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import font_manager

# -------------------------- 图表配置（可按需调整）--------------------------
# 设置中文字体（解决中文显示乱码问题）
try:
    # Windows系统
    font = font_manager.FontProperties(fname='C:/Windows/Fonts/simhei.ttf')  # 黑体
except:
    try:
        # macOS系统
        font = font_manager.FontProperties(fname='/System/Library/Fonts/PingFang.ttc')  # 苹方
    except:
        # Linux系统
        font = font_manager.FontProperties(fname='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
        print("警告：未找到中文字体，将使用英文显示")

# 图表样式配置
plt.rcParams['figure.figsize'] = (16, 12)  # 图表总大小
plt.rcParams['font.size'] = 10  # 基础字体大小
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
plt.rcParams['savefig.dpi'] = 300  # 图片分辨率
plt.rcParams['figure.constrained_layout.use'] = True  # 自动调整子图间距


def analyze_scene_file(file_path):
    """分析单个.scnlocjson文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        scene_name = data.get('SceneName', '')
        sections = data.get('SectionsInScene', [])

        choice_sections = 0
        normal_sections = 0
        total_lines = 0

        for section in sections:
            if section.get('IsChoiceSection', False):
                choice_sections += 1
            else:
                normal_sections += 1

            # 统计对话行数
            total_lines += len(section.get('LinesInSection', []))

        return {
            'scene_name': scene_name,
            'choice_sections': choice_sections,
            'normal_sections': normal_sections,
            'total_sections': choice_sections + normal_sections,
            'total_lines': total_lines,
            'file_path': str(file_path)
        }
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None


def get_quest_category(file_path):
    """
    根据文件路径确定quest类别（修复支线/小任务层级错误）
    - main_quests：向上两层，按 qxxx 级别统计（如 main_quests/part1/q105）
    - side_quests/minor_quests：保持原层级（如 side_quests/sq027，过滤scenes目录）
    """
    path = Path(file_path)
    path_parts = path.parts

    try:
        quest_idx = path_parts.index('quest')
        if quest_idx + 1 >= len(path_parts):
            return 'unknown'

        level1 = path_parts[quest_idx + 1]  # main_quests/side_quests/minor_quests

        # 主线任务：向上两层，统计到 qxxx 级别（level1/level2/level3）
        if level1 == 'main_quests':
            if quest_idx + 3 < len(path_parts):
                level2 = path_parts[quest_idx + 2]  # part1/prologue/epilogue
                level3 = path_parts[quest_idx + 3]  # q001/q105等
                if level3.startswith('q'):
                    return f"{level1}/{level2}/{level3}"
            elif quest_idx + 2 < len(path_parts):
                return f"{level1}/{path_parts[quest_idx + 2]}"

        # 支线/小任务：保持原层级（过滤scenes目录，只保留任务文件夹）
        else:
            task_parts = []
            for part in path_parts[quest_idx + 1:]:
                # 停止条件：遇到scenes目录或文件（含后缀）
                if part == 'scenes' or '.' in part or len(task_parts) >= 2:
                    break
                task_parts.append(part)
            return '/'.join(task_parts) if task_parts else level1

    except ValueError:
        pass

    return 'unknown'


def generate_charts(quest_stats, all_results, output_dir):
    """生成统计图表并保存（适配混合层级显示）"""
    print("\n开始生成统计图表...")

    # 1. 处理数据（筛选有效数据，避免空值）
    # 按对话总量排序，取Top20任务类别
    sorted_quests = sorted(quest_stats.items(), key=lambda x: x[1]['total_lines'], reverse=True)[:20]
    # 处理标签显示：换行分隔层级，避免过长
    quest_names = [q[0].replace('/', '\n') for q, _ in sorted_quests]
    quest_totals = [s['total_lines'] for _, s in sorted_quests]
    quest_choice = [s['choice_sections'] for _, s in sorted_quests]
    quest_normal = [s['normal_sections'] for _, s in sorted_quests]

    # 总体数据
    total_scenes = len(all_results)
    total_choice = sum(r['choice_sections'] for r in all_results)
    total_normal = sum(r['normal_sections'] for r in all_results)
    total_sections = total_choice + total_normal

    # 2. 创建子图（2行2列，共4个图表）
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 14))

    # -------------------------- 图表1：Top20任务对话总量柱状图 --------------------------
    colors1 = ['#2E86AB' if 'main_quests' in name else '#F18F01' for name, _ in sorted_quests]  # 主线蓝色，其他橙色
    bars1 = ax1.bar(range(len(quest_names)), quest_totals, color=colors1, alpha=0.8, edgecolor='white', linewidth=1)
    ax1.set_title('Top20任务对话总量分布（主线按qxxx统计）', fontproperties=font, fontsize=14, fontweight='bold', pad=20)
    ax1.set_xlabel('任务类别', fontproperties=font, fontsize=12)
    ax1.set_ylabel('对话总行数', fontproperties=font, fontsize=12)
    ax1.set_xticks(range(len(quest_names)))
    ax1.set_xticklabels(quest_names, fontproperties=font, rotation=0, fontsize=8)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')

    # 添加图例
    main_patch = mpatches.Patch(color='#2E86AB', label='主线任务')
    other_patch = mpatches.Patch(color='#F18F01', label='支线/小任务')
    ax1.legend(handles=[main_patch, other_patch], prop=font, fontsize=10, loc='upper right')

    # 在柱子上添加数值标签
    for bar, value in zip(bars1, quest_totals):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2., height + max(quest_totals) * 0.01,
                 f'{int(value)}', ha='center', va='bottom', fontsize=8, fontweight='bold')

    # -------------------------- 图表2：Top20任务选择段vs普通段堆叠柱状图 --------------------------
    ax2.bar(range(len(quest_names)), quest_choice, label='选择段', color='#A23B72', alpha=0.8, edgecolor='white',
            linewidth=1)
    ax2.bar(range(len(quest_names)), quest_normal, bottom=quest_choice, label='普通段', color='#3F88C5', alpha=0.8,
            edgecolor='white', linewidth=1)
    ax2.set_title('Top20任务对话段类型分布', fontproperties=font, fontsize=14, fontweight='bold', pad=20)
    ax2.set_xlabel('任务类别', fontproperties=font, fontsize=12)
    ax2.set_ylabel('段数', fontproperties=font, fontsize=12)
    ax2.set_xticks(range(len(quest_names)))
    ax2.set_xticklabels(quest_names, fontproperties=font, rotation=0, fontsize=8)
    ax2.legend(prop=font, fontsize=11, loc='upper right')
    ax2.grid(axis='y', alpha=0.3, linestyle='--')

    # -------------------------- 图表3：总体对话段类型占比饼图 --------------------------
    labels3 = ['选择段', '普通段']
    sizes3 = [total_choice, total_normal]
    colors3 = ['#A23B72', '#3F88C5']
    wedges, texts, autotexts = ax3.pie(sizes3, labels=labels3, colors=colors3, autopct='%1.1f%%',
                                       startangle=90, textprops={'fontproperties': font, 'fontsize': 12})
    ax3.set_title(f'总体对话段类型占比\n（总计{total_sections}段）', fontproperties=font, fontsize=14, fontweight='bold',
                  pad=20)

    # 美化饼图文字
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')

    # -------------------------- 图表4：任务场景数vs对话数散点图 --------------------------
    quest_scene_counts = [s['scenes'] for _, s in sorted_quests]
    # 主线和其他任务用不同颜色
    scatter_colors = ['#2E86AB' if 'main_quests' in name else '#F18F01' for name, _ in sorted_quests]
    scatter = ax4.scatter(quest_scene_counts, quest_totals, c=scatter_colors,
                          s=120, alpha=0.7, edgecolors='white', linewidth=1)
    ax4.set_title('任务场景数 vs 对话总量（颜色区分任务类型）', fontproperties=font, fontsize=14, fontweight='bold', pad=20)
    ax4.set_xlabel('场景数', fontproperties=font, fontsize=12)
    ax4.set_ylabel('对话总行数', fontproperties=font, fontsize=12)
    ax4.grid(alpha=0.3, linestyle='--')

    # 添加图例
    ax4.legend(handles=[main_patch, other_patch], prop=font, fontsize=10, loc='upper left')

    # 3. 保存图表
    output_path = output_dir / 'quest_analysis_charts_final.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    print(f"最终图表已保存到: {output_path}")


def main():
    # -------------------------- 配置指定的5个路径 --------------------------
    base_dir_epilogue = Path(r'D:\AppSoft\Sy2077\2077\2077\CDPR2077\r6\depot\base\quest\main_quests\epilogue')
    base_dir_part1 = Path(r'D:\AppSoft\Sy2077\2077\2077\CDPR2077\r6\depot\base\quest\main_quests\part1')
    base_dir_prologue = Path(r'D:\AppSoft\Sy2077\2077\2077\CDPR2077\r6\depot\base\quest\main_quests\prologue')
    base_dir_sidequest = Path(r'D:\AppSoft\Sy2077\2077\2077\CDPR2077\r6\depot\base\quest\side_quests')
    base_dir_minor_quests = Path(r'D:\AppSoft\Sy2077\2077\2077\CDPR2077\r6\depot\base\quest\minor_quests')

    # 存储所有要处理的路径
    target_dirs = [
        base_dir_epilogue,
        base_dir_part1,
        base_dir_prologue,
        base_dir_sidequest,
        base_dir_minor_quests
    ]

    # -------------------------- 查找目标文件（核心修改：开启递归+屏蔽Versions） --------------------------
    scene_files = []
    excluded_folder = 'Versions'  # 要排除的文件夹名（不区分大小写）
    print("开始扫描 5 个指定路径下的【任务文件夹/scenes】结构...")
    print("层级规则：根目录 → 任务文件夹（1层）→ scenes 文件夹 → 递归所有子目录（排除Versions）")
    print("=" * 160)

    for root_dir in target_dirs:
        root_dir_name = root_dir.name  # 根目录名称（如 epilogue、side_quests）
        if not root_dir.exists():
            print(f"⚠️  根路径 {root_dir} 不存在，跳过")
            print("-" * 160)
            continue

        found_count = 0  # 当前根目录下找到的有效文件数
        excluded_count = 0  # 当前根目录下被排除的文件数
        print(f"🔍 正在扫描根目录：{root_dir}")

        # 第一层遍历：根目录下的所有【任务文件夹】（仅1层，不递归）
        for quest_dir in root_dir.iterdir():
            # 只处理文件夹（排除文件、符号链接等），即“中间的任务文件夹”
            if quest_dir.is_dir():
                # 拼接层级路径：任务文件夹 → scenes 文件夹（核心层级）
                target_scene_dir = quest_dir / 'scenes'

                # 检查 scenes 文件夹是否存在且是目录
                if target_scene_dir.exists() and target_scene_dir.is_dir():
                    # 核心修改1：开启递归扫描（** 表示遍历所有子目录）
                    all_files = list(target_scene_dir.glob('**/*.scnlocjson'))
                    filtered_files = []  # 存储过滤后（排除Versions）的有效文件

                    # 核心修改2：过滤Versions文件夹下的文件
                    for file in all_files:
                        # 不区分大小写判断：文件路径是否包含 Versions 文件夹
                        if excluded_folder.lower() not in str(file.parent).lower():
                            filtered_files.append(file)
                        else:
                            excluded_count += 1
                            # 可选：打印被排除的文件路径（注释掉简化输出）
                            # print(f"  ❌ 排除 Versions 下的文件：{file}")

                    # 统计当前任务文件夹的有效文件
                    if filtered_files:
                        scene_files.extend(filtered_files)
                        found_count += len(filtered_files)
                        # 打印详细信息（可注释简化输出）
                        print(f"  ✅ 任务文件夹：{quest_dir.name}")
                        print(f"      → scenes 路径：{target_scene_dir}")
                        print(f"      → 递归找到 {len(all_files)} 个文件，排除 {len(all_files)-len(filtered_files)} 个，保留 {len(filtered_files)} 个")
                        # 可选：打印保留的文件名（注释掉简化输出）
                        # print(f"      → 保留文件：{[f.name for f in filtered_files[:5]]}{'...' if len(filtered_files)>5 else ''}")
                    else:
                        # 可选：打印无有效文件的任务文件夹（注释掉减少输出）
                        print(f"  ❌ 任务文件夹：{quest_dir.name} → scenes 文件夹无有效 .scnlocjson 文件")
                else:
                    # 可选：打印无 scenes 文件夹的任务文件夹（注释掉减少输出）
                    print(f"  ⚠️  任务文件夹：{quest_dir.name} → 无 scenes 文件夹，跳过")

        print(f"📊 该根目录总计：找到 {found_count + excluded_count} 个文件，排除 {excluded_count} 个，有效文件 {found_count} 个")
        print("-" * 160)

    # 最终统计
    print(f"\n🎉 所有路径扫描完成！")
    print(f"📈 总计找到 {len(scene_files)} 个符合条件的 .scnlocjson 文件（已排除 Versions 子文件夹）")

    # -------------------------- 文件分析逻辑（统计对话/选择数） --------------------------
    # 分析每个文件
    all_results = []
    quest_stats = defaultdict(lambda: {
        'scenes': 0,
        'choice_sections': 0,
        'normal_sections': 0,
        'total_sections': 0,
        'total_lines': 0,
        'files': []
    })

    for i, scene_file in enumerate(scene_files, 1):
        if i % 50 == 0:
            print(f"处理进度: {i}/{len(scene_files)}")

        result = analyze_scene_file(scene_file)
        if result:
            all_results.append(result)

            # 按自定义分类逻辑统计
            quest = get_quest_category(scene_file)
            quest_stats[quest]['scenes'] += 1
            quest_stats[quest]['choice_sections'] += result['choice_sections']
            quest_stats[quest]['normal_sections'] += result['normal_sections']
            quest_stats[quest]['total_sections'] += result['total_sections']
            quest_stats[quest]['total_lines'] += result['total_lines']
            quest_stats[quest]['files'].append(result['scene_name'])

    # 定义输出目录（自动创建，避免权限错误）
    output_dir = Path(r'D:\Data\PYh\AmountSy\scnScene')
    output_dir.mkdir(exist_ok=True)  # 确保目录存在

    # 输出详细结果到CSV
    output_csv = output_dir / 'scene_analysis_detailedDDD_final.csv'
    with open(output_csv, 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = ['scene_name', 'quest_category', 'choice_sections', 'normal_sections',
                      'total_sections', 'total_lines', 'file_path']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for result in all_results:
            row = result.copy()
            row['quest_category'] = get_quest_category(result['file_path'])
            writer.writerow(row)

    print(f"\n详细结果已保存到: {output_csv}")

    # 输出Quest级别统计（混合层级）
    output_quest_csv = output_dir / 'quest_analysis_summaryYYYY_final.csv'
    with open(output_quest_csv, 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = ['quest_category', 'task_type', 'scene_count', 'choice_sections', 'normal_sections',
                      'total_sections', 'total_lines', 'avg_sections_per_scene', 'avg_lines_per_scene',
                      'choice_ratio']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        # 按总对话数排序
        sorted_quests = sorted(quest_stats.items(),
                               key=lambda x: x[1]['total_lines'],
                               reverse=True)

        for quest, stats in sorted_quests:
            avg_sections = stats['total_sections'] / stats['scenes'] if stats['scenes'] > 0 else 0
            avg_lines = stats['total_lines'] / stats['scenes'] if stats['scenes'] > 0 else 0
            choice_ratio = stats['choice_sections'] / stats['total_sections'] if stats['total_sections'] > 0 else 0
            # 标记任务类型
            task_type = '主线任务' if 'main_quests' in quest else '支线/小任务'

            writer.writerow({
                'quest_category': quest,
                'task_type': task_type,
                'scene_count': stats['scenes'],
                'choice_sections': stats['choice_sections'],
                'normal_sections': stats['normal_sections'],
                'total_sections': stats['total_sections'],
                'total_lines': stats['total_lines'],
                'avg_sections_per_scene': f"{avg_sections:.2f}",
                'avg_lines_per_scene': f"{avg_lines:.2f}",
                'choice_ratio': f"{choice_ratio:.2%}"
            })

    print(f"最终Quest统计已保存到: {output_quest_csv}")

    # 生成最终统计图表
    generate_charts(quest_stats, all_results, output_dir)

    # 控制台输出Top 30 Quest（按对话总量排序）
    print("\n" + "=" * 100)
    print("Top 30 Quest（按对话总量排序 | 主线按qxxx统计，支线/小任务保持原层级）")
    print("=" * 100)
    print(f"{'Quest类别':<60} {'任务类型':<10} {'场景数':>8} {'对话数':>8} {'选择段':>8} {'总段数':>8} {'选择率':>8}")
    print("-" * 100)

    for quest, stats in sorted_quests[:30]:
        choice_ratio = stats['choice_sections'] / stats['total_sections'] if stats['total_sections'] > 0 else 0
        task_type = '主线任务' if 'main_quests' in quest else '支线/小任务'
        # 截断过长的类别名称
        quest_display = quest[:57] + "..." if len(quest) > 60 else quest
        print(f"{quest_display:<60} {task_type:<10} {stats['scenes']:>8} {stats['total_lines']:>8} "
              f"{stats['choice_sections']:>8} {stats['total_sections']:>8} {choice_ratio:>7.1%}")

    # 输出总体统计（按任务类型分组）
    print("\n" + "=" * 100)
    print("总体统计（按任务类型分组）")
    print("=" * 100)

    # 分组统计
    main_stats = {
        'scenes': 0, 'choice_sections': 0, 'normal_sections': 0, 'total_sections': 0, 'total_lines': 0
    }
    other_stats = {
        'scenes': 0, 'choice_sections': 0, 'normal_sections': 0, 'total_sections': 0, 'total_lines': 0
    }

    for quest, stats in quest_stats.items():
        if 'main_quests' in quest:
            for key in main_stats.keys():
                main_stats[key] += stats[key]
        else:
            for key in other_stats.keys():
                other_stats[key] += stats[key]

    # 输出分组统计
    for task_type, stats in [('主线任务', main_stats), ('支线/小任务', other_stats)]:
        if stats['scenes'] == 0:
            continue
        avg_sections = stats['total_sections'] / stats['scenes']
        avg_lines = stats['total_lines'] / stats['scenes']
        choice_ratio = stats['choice_sections'] / stats['total_sections'] if stats['total_sections'] > 0 else 0

        print(f"\n{task_type}:")
        print(f"  场景数: {stats['scenes']}")
        print(f"  总段数: {stats['total_sections']}（选择段: {stats['choice_sections']}, 普通段: {stats['normal_sections']}）")
        print(f"  总对话数: {stats['total_lines']}")
        print(f"  平均每场景段数: {avg_sections:.2f}")
        print(f"  平均每场景对话数: {avg_lines:.2f}")
        print(f"  选择段占比: {choice_ratio:.2%}")

    # 输出整体统计
    total_scenes = len(all_results)
    total_choice = sum(r['choice_sections'] for r in all_results)
    total_normal = sum(r['normal_sections'] for r in all_results)
    total_sections = total_choice + total_normal
    total_lines = sum(r['total_lines'] for r in all_results)

    print(f"\n整体统计:")
    print(f"  总场景数: {total_scenes}")
    print(f"  总段数: {total_sections}（选择段占比: {total_choice/total_sections:.2%}）")
    print(f"  总对话数: {total_lines}")
    print(f"  平均每场景对话数: {total_lines/total_scenes:.2f}")


if __name__ == '__main__':
    # 安装依赖提示（首次运行时）
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("检测到未安装matplotlib，正在自动安装...")
        import subprocess
        import sys

        subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib"])
        print("matplotlib安装完成，重启脚本...")
        sys.exit()

    main()
