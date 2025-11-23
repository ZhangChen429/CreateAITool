import json
import os
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np

# -------------------------- 图表配置（解决中文显示和样式问题）--------------------------
try:
    # Windows系统
    font = font_manager.FontProperties(fname='C:/Windows/Fonts/simhei.ttf')  # 黑体
    font_sans = font_manager.FontProperties(fname='C:/Windows/Fonts/simhei.ttf')  # 用于图例的字体
except:
    try:
        # macOS系统
        font = font_manager.FontProperties(fname='/System/Library/Fonts/PingFang.ttc')  # 苹方
        font_sans = font_manager.FontProperties(fname='/System/Library/Fonts/PingFang.ttc')
    except:
        # Linux系统
        font = font_manager.FontProperties(fname='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
        font_sans = font_manager.FontProperties(fname='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
        print("警告：未找到中文字体，将使用英文显示")

# 图表基础样式
plt.rcParams['figure.figsize'] = (18, 14)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['figure.constrained_layout.use'] = True
plt.rcParams['axes.grid'] = False
plt.rcParams['legend.fontsize'] = 10  # 设置默认图例字体大小


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

        if os.path.isdir(item_path) and (item.startswith('q') or item.startswith('sq') or item.startswith('mq')):
            stats = analyze_quest_folder(item_path)

            if stats:
                stats['quest_code'] = item
                stats['quest_path'] = item_path
                results.append(stats)

    return results


def generate_charts(all_results, output_dir):
    """生成统计图表并保存到指定目录"""
    print(f"\n开始生成图表，保存路径：{output_dir}")

    # 创建目录（如果不存在）
    output_dir.mkdir(exist_ok=True)

    # 整理数据：按任务类型汇总
    type_names = []
    total_scenes_list = []
    total_lines_list = []
    total_choices_list = []
    total_sections_list = []
    avg_lines_list = []

    # 单个任务详情数据（Top20对话数任务）
    task_details = []
    for type_name, results in all_results.items():
        type_scenes = sum(r['total_scenes'] for r in results)
        type_lines = sum(r['total_lines'] for r in results)
        type_choices = sum(r['total_choices'] for r in results)
        type_sections = sum(r['total_sections'] for r in results)
        type_avg = type_lines / type_scenes if type_scenes > 0 else 0

        type_names.append(type_name)
        total_scenes_list.append(type_scenes)
        total_lines_list.append(type_lines)
        total_choices_list.append(type_choices)
        total_sections_list.append(type_sections)
        avg_lines_list.append(type_avg)

        # 收集单个任务数据
        for r in results:
            task_details.append({
                'name': f"{type_name[:4]}-{r['quest_code']}",
                'scenes': r['total_scenes'],
                'lines': r['total_lines'],
                'choices': r['total_choices'],
                'sections': r['total_sections']
            })

    # 筛选Top20对话数任务
    top20_tasks = sorted(task_details, key=lambda x: x['lines'], reverse=True)[:20]
    top20_names = [t['name'] for t in top20_tasks]
    top20_lines = [t['lines'] for t in top20_tasks]
    top20_choices = [t['choices'] for t in top20_tasks]

    # 创建子图（3行2列，共6个子图）
    fig, axes = plt.subplots(3, 2, figsize=(18, 15))
    axes = axes.flatten()

    # 颜色配置
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57']
    choice_color = '#E91E63'
    normal_color = '#3F51B5'

    # -------------------------- 图1：各任务类型对话数对比（柱状图）--------------------------
    ax1 = axes[0]
    bars1 = ax1.bar(range(len(type_names)), total_lines_list, color=colors[:len(type_names)],
                    alpha=0.8, edgecolor='white', linewidth=1.5)
    ax1.set_title('各任务类型对话总数对比', fontproperties=font, fontsize=14, fontweight='bold', pad=20)
    ax1.set_xlabel('任务类型', fontproperties=font, fontsize=12)
    ax1.set_ylabel('对话总行数', fontproperties=font, fontsize=12)
    ax1.set_xticks(range(len(type_names)))
    ax1.set_xticklabels([name.replace(' (', '\n(') for name in type_names], fontproperties=font, rotation=0)
    ax1.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)

    # 添加数值标签
    for bar, value in zip(bars1, total_lines_list):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2, height + max(total_lines_list) * 0.01,
                 f'{int(value):,}', ha='center', va='bottom', fontproperties=font, fontweight='bold')

    # -------------------------- 图2：各任务类型选择数对比（横向柱状图）--------------------------
    ax2 = axes[1]
    bars2 = ax2.barh(range(len(type_names)), total_choices_list, color=choice_color,
                     alpha=0.8, edgecolor='white', linewidth=1.5)
    ax2.set_title('各任务类型选择数对比', fontproperties=font, fontsize=14, fontweight='bold', pad=20)
    ax2.set_xlabel('选择段数量', fontproperties=font, fontsize=12)
    ax2.set_ylabel('任务类型', fontproperties=font, fontsize=12)
    ax2.set_yticks(range(len(type_names)))
    ax2.set_yticklabels([name.replace(' (', '\n(') for name in type_names], fontproperties=font)
    ax2.grid(axis='x', alpha=0.3, linestyle='--', linewidth=0.5)

    # 添加数值标签
    for bar, value in zip(bars2, total_choices_list):
        width = bar.get_width()
        ax2.text(width + max(total_choices_list) * 0.01, bar.get_y() + bar.get_height() / 2,
                 f'{int(value)}', ha='left', va='center', fontproperties=font, fontweight='bold')

    # -------------------------- 图3：Top20任务对话数排名（柱状图）--------------------------
    ax3 = axes[2]
    # 调整标签显示（缩短过长的任务名称）
    top20_display_names = [name[:12] + '...' if len(name) > 12 else name for name in top20_names]
    bars3 = ax3.bar(range(len(top20_names)), top20_lines, color='#FF9800', alpha=0.8,
                    edgecolor='white', linewidth=1.5)
    ax3.set_title('Top20任务对话数排名', fontproperties=font, fontsize=14, fontweight='bold', pad=20)
    ax3.set_xlabel('任务', fontproperties=font, fontsize=12)
    ax3.set_ylabel('对话行数', fontproperties=font, fontsize=12)
    ax3.set_xticks(range(len(top20_names)))
    ax3.set_xticklabels(top20_display_names, fontproperties=font, rotation=45, ha='right')
    ax3.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)

    # 添加数值标签（简化显示）
    for bar, value in zip(bars3, top20_lines):
        height = bar.get_height()
        label = f'{value:,}' if value < 1000 else f'{value // 1000}k'
        ax3.text(bar.get_x() + bar.get_width() / 2, height + max(top20_lines) * 0.01,
                 label, ha='center', va='bottom', fontproperties=font, fontweight='bold', fontsize=9)

    # -------------------------- 图4：各任务类型资源占比（饼图）--------------------------
    ax4 = axes[3]
    # 过滤数量为0的数据
    valid_data = [(name, value) for name, value in zip(type_names, total_lines_list) if value > 0]
    if valid_data:
        valid_names, valid_values = zip(*valid_data)
        # 简化标签
        simple_names = [name.split(' ')[0] for name in valid_names]
        wedges, texts, autotexts = ax4.pie(valid_values, labels=simple_names, colors=colors[:len(valid_names)],
                                           autopct='%1.1f%%', startangle=90,
                                           textprops={'fontproperties': font, 'fontsize': 11})
        ax4.set_title('各任务类型对话数占比', fontproperties=font, fontsize=14, fontweight='bold', pad=20)

        # 美化饼图文字
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')

    # -------------------------- 图5：场景数vs对话数散点图（单个任务）--------------------------
    ax5 = axes[4]
    # 所有任务的散点图
    scenes_all = [t['scenes'] for t in task_details]
    lines_all = [t['lines'] for t in task_details]
    # 按任务类型着色
    task_types = []
    for type_name, results in all_results.items():
        task_types.extend([type_name] * len(results))

    # 为不同类型分配颜色
    type_color_map = {type_names[i]: colors[i] for i in range(len(type_names))}
    scatter_colors = [type_color_map[t] for t in task_types]

    ax5.scatter(scenes_all, lines_all, c=scatter_colors, alpha=0.6, s=60, edgecolors='white', linewidth=0.5)
    ax5.set_title('单个任务：场景数 vs 对话数', fontproperties=font, fontsize=14, fontweight='bold', pad=20)
    ax5.set_xlabel('Scene数量', fontproperties=font, fontsize=12)
    ax5.set_ylabel('对话行数', fontproperties=font, fontsize=12)
    ax5.grid(alpha=0.3, linestyle='--', linewidth=0.5)

    # 修复图例：移除Line2D的fontproperties参数，通过rcParams统一设置字体
    legend_elements = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color,
                                  markersize=8, label=name)
                       for name, color in type_color_map.items()]
    ax5.legend(handles=legend_elements, loc='upper left')

    # -------------------------- 图6：各任务类型平均对话数对比（柱状图）--------------------------
    ax6 = axes[5]
    bars6 = ax6.bar(range(len(type_names)), avg_lines_list, color='#2196F3', alpha=0.8,
                    edgecolor='white', linewidth=1.5)
    ax6.set_title('各任务类型平均对话数（per Scene）', fontproperties=font, fontsize=14, fontweight='bold', pad=20)
    ax6.set_xlabel('任务类型', fontproperties=font, fontsize=12)
    ax6.set_ylabel('平均对话行数/Scene', fontproperties=font, fontsize=12)
    ax6.set_xticks(range(len(type_names)))
    ax6.set_xticklabels([name.replace(' (', '\n(') for name in type_names], fontproperties=font, rotation=0)
    ax6.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)

    # 添加数值标签
    for bar, value in zip(bars6, avg_lines_list):
        height = bar.get_height()
        ax6.text(bar.get_x() + bar.get_width() / 2, height + max(avg_lines_list) * 0.01,
                 f'{value:.1f}', ha='center', va='bottom', fontproperties=font, fontweight='bold')

    # 添加总标题
    fig.suptitle('《赛博朋克2077》任务对话与选择统计分析报告', fontproperties=font, fontsize=18, fontweight='bold',
                 y=0.98)

    # 保存图表
    output_path = output_dir / 'quest_analysis_charts.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    print(f"图表已保存：{output_path}")
    print("图表包含6个子图：")
    print("1. 各任务类型对话总数对比    2. 各任务类型选择数对比")
    print("3. Top20任务对话数排名      4. 各任务类型对话数占比")
    print("5. 场景数vs对话数散点图     6. 各任务类型平均对话数对比")


def main():
    # 扫描不同目录（修复终章路径错误：原路径指向prologue，已修正为epilogue）
    quest_types = [
        ('序章 (Prologue)', r"D:\AppSoft\Sy2077\2077\2077\CDPR2077\r6\depot\base\quest\main_quests\prologue"),
        ('主线第一章 (Part 1)', r"D:\AppSoft\Sy2077\2077\2077\CDPR2077\r6\depot\base\quest\main_quests\part1"),
        ('终章 (Epilogue)', r"D:\AppSoft\Sy2077\2077\2077\CDPR2077\r6\depot\base\quest\main_quests\epilogue"),  # 修复路径
        ('支线 (Side Quests)', r"D:\AppSoft\Sy2077\2077\2077\CDPR2077\r6\depot\base\quest\side_quests"),
        ('小任务 (Minor Quests)', r"D:\AppSoft\Sy2077\2077\2077\CDPR2077\r6\depot\base\quest\minor_quests")  # 修正名称格式
    ]

    all_results = {}

    print("开始扫描任务目录并统计数据...")
    for type_name, path in quest_types:
        if os.path.exists(path):
            results = scan_quest_directory(path)
            if results:
                all_results[type_name] = results
                print(f"✓ {type_name}：找到 {len(results)} 个任务")
            else:
                print(f"✗ {type_name}：未找到有效任务数据")
        else:
            print(f"✗ {type_name}：路径不存在 - {path}")

    # 打印文字结果
    print("\n" + "=" * 100)
    print("《赛博朋克2077》任务对话与选择统计")
    print("=" * 100)
    print()

    for type_name, results in all_results.items():
        print(f"\n{'=' * 100}")
        print(f"{type_name}")
        print(f"{'=' * 100}")
        print(
            f"{'任务代码':<12} | {'Scene数':<8} | {'Section数':<10} | {'对话数':<10} | {'选择数':<8} | {'平均对话/Scene':<15}")
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
        print(
            f"{type_name:<25} | Scenes: {type_scenes:<6} | 对话: {type_lines:<8} | 选择: {type_choices:<6} | 平均: {avg:.1f}")

    print("-" * 100)
    grand_avg = grand_total_lines / grand_total_scenes if grand_total_scenes > 0 else 0
    print(
        f"{'全游戏总计':<25} | Scenes: {grand_total_scenes:<6} | 对话: {grand_total_lines:<8} | 选择: {grand_total_choices:<6} | 平均: {grand_avg:.1f}")
    print()

    # 生成图表（保存到指定目录）
    output_dir = Path(r'D:\Data\PYh\AmountSy\scnScene')  # 目标目录
    if all_results:
        generate_charts(all_results, output_dir)
    else:
        print("警告：未获取到有效统计数据，无法生成图表")


if __name__ == '__main__':
    # 检查并安装依赖
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("检测到未安装必要依赖，正在自动安装...")
        import subprocess
        import sys

        subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib", "numpy"])
        print("依赖安装完成，重启脚本...")
        sys.exit()

    main()