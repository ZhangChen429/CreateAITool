#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
赛博朋克2077核心美术资产统计图表
- 包含文件格式分布、资产类别统计、核心资源对比等多维度可视化
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import font_manager
from collections import defaultdict
from pathlib import Path

# -------------------------- 全局配置 --------------------------
# 设置中文字体（解决中文显示乱码）
try:
    font = font_manager.FontProperties(fname='C:/Windows/Fonts/simhei.ttf')  # Windows 黑体
except:
    try:
        font = font_manager.FontProperties(fname='/System/Library/Fonts/PingFang.ttc')  # macOS 苹方
    except:
        font = font_manager.FontProperties(fname='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
        print("警告：未找到中文字体，将使用英文显示")

# 图表基础样式
plt.rcParams['figure.figsize'] = (20, 16)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['figure.constrained_layout.use'] = True
plt.rcParams['axes.grid'] = False

# -------------------------- 核心数据（从需求中提取） --------------------------
# 1. 文件格式统计（格式: 数量, 描述, 颜色）
file_format_data = {
    '.wem': (178063, '音频', '#1E88E5'),
    '.xbm': (119098, '纹理', '#FFC107'),
    '.mesh': (108305, '3D网格', '#4CAF50'),
    '.mlmask': (26168, '地形遮罩', '#9C27B0'),
    '.ent': (16068, '实体', '#FF5722'),
    '.anims': (16023, '动画', '#00BCD4'),
    '.mlsetup': (13712, '多层地形设置', '#795548'),
    '.mi': (6268, '材质实例', '#E91E63'),
    '.app': (2090, '外观', '#607D8B'),
    '.rig': (1223, '骨骼', '#2196F3'),
    '.mt': (268, '材质模板', '#8BC34A'),
    '.w2mesh': (332, 'W2网格', '#CDDC39'),
    '.bnk': (127, '音频银行', '#FF9800'),
    '.opuspak': (1442, '音频压缩包', '#F44336'),
}

# 2. 资产类别统计（按大类汇总）
asset_category_data = {
    '音频资源': 178063 + 127 + 1442,  # .wem + .bnk + .opuspak
    '纹理资源': 119098,  # .xbm
    '3D模型资源': 108305 + 332,  # .mesh + .w2mesh
    '地形资源': 26168 + 13712,  # .mlmask + .mlsetup
    '实体与动画': 16068 + 16023 + 1223,  # .ent + .anims + .rig
    '材质资源': 6268 + 268,  # .mi + .mt
    '外观资源': 2090,  # .app
}

# 3. 核心资源细分（重点资产类型的详细分布）
core_asset_data = {
    '视觉资产': {
        'textures(纹理)': 119098,
        'materials(材质)': 6268 + 268,
        'mesh(网格)': 108305 + 332,
    },
    '角色与动画': {
        'characters(角色)': 2090,  # .app 外观文件
        'animations(动画)': 16023,
        'rig(骨骼)': 1223,
    },
    '环境与场景': {
        'terrain(地形)': 26168 + 13712,
        'environment(环境)': 0,  # 无具体数量，按比例分配
        'lighting(光照)': 0,
    },
    '音频资源': {
        'sound(音频)': 178063 + 127 + 1442,
    },
    '实体与道具': {
        'entities(实体)': 16068,
        'items(道具)': 0,
        'vehicles(载具)': 0,
    }
}

# 4. 重点文件格式Top10
top10_formats = dict(sorted(file_format_data.items(), key=lambda x: x[1][0], reverse=True)[:10])


# -------------------------- 图表生成函数 --------------------------
def generate_asset_charts(output_dir):
    """生成综合统计图表（4行2列，共8个子图）"""
    fig, axes = plt.subplots(4, 2, figsize=(20, 16))
    axes = axes.flatten()  # 转为一维数组便于索引

    # -------------------------- 图1：Top10文件格式数量柱状图 --------------------------
    ax1 = axes[0]
    formats = list(top10_formats.keys())
    counts = [top10_formats[f][0] for f in formats]
    colors = [top10_formats[f][2] for f in formats]

    bars = ax1.bar(range(len(formats)), counts, color=colors, alpha=0.8, edgecolor='white', linewidth=1.5)
    ax1.set_title('Top10文件格式数量分布', fontproperties=font, fontsize=14, fontweight='bold', pad=20)
    ax1.set_xlabel('文件格式', fontproperties=font, fontsize=12)
    ax1.set_ylabel('文件数量', fontproperties=font, fontsize=12)
    ax1.set_xticks(range(len(formats)))
    ax1.set_xticklabels(formats, fontproperties=font)
    ax1.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)

    # 添加数值标签（简化显示，超过10万显示x万）
    for bar, count in zip(bars, counts):
        height = bar.get_height()
        label = f'{count // 10000}万' if count >= 10000 else f'{count:,}'
        ax1.text(bar.get_x() + bar.get_width() / 2, height + max(counts) * 0.01,
                 label, ha='center', va='bottom', fontproperties=font, fontweight='bold')

    # -------------------------- 图2：资产大类占比饼图 --------------------------
    ax2 = axes[1]
    categories = list(asset_category_data.keys())
    category_counts = list(asset_category_data.values())
    # 过滤数量为0的类别
    categories = [c for c, cnt in zip(categories, category_counts) if cnt > 0]
    category_counts = [cnt for cnt in category_counts if cnt > 0]

    # 颜色配置
    category_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF']
    while len(category_colors) < len(categories):
        category_colors.append(
            '#' + ''.join([hex(int(c * 255))[2:].zfill(2) for c in plt.cm.Set3(len(category_colors) / 10)]))

    wedges, texts, autotexts = ax2.pie(category_counts, labels=categories, colors=category_colors[:len(categories)],
                                       autopct='%1.1f%%', startangle=90,
                                       textprops={'fontproperties': font, 'fontsize': 10})
    ax2.set_title('资产大类占比分布', fontproperties=font, fontsize=14, fontweight='bold', pad=20)

    # 美化饼图文字
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')

    # -------------------------- 图3：核心资源细分堆叠柱状图 --------------------------
    ax3 = axes[2]
    main_categories = list(core_asset_data.keys())
    sub_assets = []
    sub_counts = defaultdict(list)
    sub_colors = defaultdict(list)

    # 颜色映射
    sub_color_map = {
        'textures(纹理)': '#FFC107', 'materials(材质)': '#E91E63', 'mesh(网格)': '#4CAF50',
        'characters(角色)': '#607D8B', 'animations(动画)': '#00BCD4', 'rig(骨骼)': '#2196F3',
        'terrain(地形)': '#9C27B0', 'environment(环境)': '#795548', 'lighting(光照)': '#CDDC39',
        'sound(音频)': '#1E88E5', 'entities(实体)': '#FF5722', 'items(道具)': '#8BC34A', 'vehicles(载具)': '#FF9800'
    }

    # 整理数据
    bottom = [0] * len(main_categories)
    for i, main_cat in enumerate(main_categories):
        for sub_cat, count in core_asset_data[main_cat].items():
            if count > 0:
                sub_counts[sub_cat].append(count)
                sub_colors[sub_cat].append(sub_color_map[sub_cat])
                ax3.bar(i, count, bottom=bottom[i],
                        label=sub_cat if sub_cat not in ax3.get_legend_handles_labels()[1] else "",
                        color=sub_color_map[sub_cat], alpha=0.8, edgecolor='white', linewidth=1)
                bottom[i] += count

    ax3.set_title('核心资源细分分布', fontproperties=font, fontsize=14, fontweight='bold', pad=20)
    ax3.set_xlabel('资源大类', fontproperties=font, fontsize=12)
    ax3.set_ylabel('文件数量', fontproperties=font, fontsize=12)
    ax3.set_xticks(range(len(main_categories)))
    ax3.set_xticklabels(main_categories, fontproperties=font, rotation=15)
    ax3.legend(prop=font, fontsize=9, loc='upper right', bbox_to_anchor=(1.3, 1))
    ax3.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)

    # -------------------------- 图4：文件格式数量对数坐标图（适配极端值） --------------------------
    ax4 = axes[3]
    all_formats = list(file_format_data.keys())
    all_counts = [file_format_data[f][0] for f in all_formats]
    all_colors = [file_format_data[f][2] for f in all_formats]

    bars = ax4.bar(range(len(all_formats)), all_counts, color=all_colors, alpha=0.7, edgecolor='white', linewidth=1)
    ax4.set_title('所有文件格式数量分布（对数坐标）', fontproperties=font, fontsize=14, fontweight='bold', pad=20)
    ax4.set_xlabel('文件格式', fontproperties=font, fontsize=12)
    ax4.set_ylabel('文件数量（对数尺度）', fontproperties=font, fontsize=12)
    ax4.set_xticks(range(len(all_formats)))
    ax4.set_xticklabels(all_formats, fontproperties=font, rotation=45)
    ax4.set_yscale('log')  # 对数坐标，解决数值差异过大问题
    ax4.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)

    # -------------------------- 图5：资产类型数量对比雷达图 --------------------------
    ax5 = axes[4]
    # 选择6个主要资产类型做雷达图
    radar_categories = ['音频', '纹理', '3D网格', '地形', '实体', '动画']
    radar_counts = [
        asset_category_data['音频资源'],
        asset_category_data['纹理资源'],
        asset_category_data['3D模型资源'],
        asset_category_data['地形资源'],
        asset_category_data['实体与动画'] // 3,  # 拆分实体动画
        asset_category_data['实体与动画'] // 3
    ]

    # 归一化数据（雷达图适合展示相对比例）
    max_count = max(radar_counts)
    normalized_counts = [cnt / max_count for cnt in radar_counts]

    # 绘制雷达图
    angles = [n / float(len(radar_categories)) * 2 * 3.14159 for n in range(len(radar_categories))]
    angles += angles[:1]  # 闭合图形
    normalized_counts += normalized_counts[:1]
    radar_categories += radar_categories[:1]

    ax5.plot(angles, normalized_counts, 'o-', linewidth=2, color='#FF6B6B', alpha=0.8)
    ax5.fill(angles, normalized_counts, alpha=0.3, color='#FF6B6B')
    ax5.set_xticks(angles[:-1])
    ax5.set_xticklabels(radar_categories[:-1], fontproperties=font)
    ax5.set_ylim(0, 1)
    ax5.set_title('主要资产类型相对比例（雷达图）', fontproperties=font, fontsize=14, fontweight='bold', pad=20)
    ax5.grid(True, alpha=0.3)

    # -------------------------- 图6：文件格式类型分类统计（横向柱状图） --------------------------
    ax6 = axes[5]
    # 按类型分组
    type_groups = defaultdict(int)
    type_colors = {
        '音频相关': '#1E88E5',
        '纹理相关': '#FFC107',
        '3D模型相关': '#4CAF50',
        '地形相关': '#9C27B0',
        '实体动画相关': '#FF5722',
        '材质相关': '#E91E63',
        '外观相关': '#607D8B'
    }

    for fmt, (cnt, desc, _) in file_format_data.items():
        if '音频' in desc:
            type_groups['音频相关'] += cnt
        elif '纹理' in desc:
            type_groups['纹理相关'] += cnt
        elif '网格' in desc:
            type_groups['3D模型相关'] += cnt
        elif '地形' in desc:
            type_groups['地形相关'] += cnt
        elif '实体' in desc or '动画' in desc or '骨骼' in desc:
            type_groups['实体动画相关'] += cnt
        elif '材质' in desc:
            type_groups['材质相关'] += cnt
        elif '外观' in desc:
            type_groups['外观相关'] += cnt

    # 横向柱状图
    groups = list(type_groups.keys())
    group_counts = list(type_groups.values())
    colors = [type_colors[g] for g in groups]

    bars = ax6.barh(range(len(groups)), group_counts, color=colors, alpha=0.8, edgecolor='white', linewidth=1)
    ax6.set_title('文件格式类型分组统计', fontproperties=font, fontsize=14, fontweight='bold', pad=20)
    ax6.set_xlabel('文件数量', fontproperties=font, fontsize=12)
    ax6.set_ylabel('文件类型组', fontproperties=font, fontsize=12)
    ax6.set_yticks(range(len(groups)))
    ax6.set_yticklabels(groups, fontproperties=font)
    ax6.grid(axis='x', alpha=0.3, linestyle='--', linewidth=0.5)

    # 添加数值标签
    for bar, count in zip(bars, group_counts):
        width = bar.get_width()
        label = f'{count // 10000}万' if count >= 10000 else f'{count:,}'
        ax6.text(width + max(group_counts) * 0.01, bar.get_y() + bar.get_height() / 2,
                 label, ha='left', va='center', fontproperties=font, fontweight='bold')

    # -------------------------- 图7：重点文件格式占比（环形图） --------------------------
    ax7 = axes[6]
    # 选择前5个重点格式 + 其他
    top5_formats = dict(sorted(file_format_data.items(), key=lambda x: x[1][0], reverse=True)[:5])
    other_count = sum(file_format_data[f][0] for f in file_format_data if f not in top5_formats)

    ring_labels = [f'{fmt}\n({file_format_data[fmt][1]})' for fmt in top5_formats.keys()] + ['其他']
    ring_counts = [top5_formats[f][0] for f in top5_formats.keys()] + [other_count]
    ring_colors = [top5_formats[f][2] for f in top5_formats.keys()] + ['#BDBDBD']

    # 绘制环形图（中间空心）
    wedges, texts, autotexts = ax7.pie(ring_counts, labels=ring_labels, colors=ring_colors,
                                       autopct='%1.1f%%', startangle=90,
                                       textprops={'fontproperties': font, 'fontsize': 9},
                                       wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2))
    ax7.set_title('重点文件格式占比（环形图）', fontproperties=font, fontsize=14, fontweight='bold', pad=20)

    # 美化文字
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')

    # -------------------------- 图8：资产规模汇总统计表 --------------------------
    ax8 = axes[7]
    ax8.axis('tight')
    ax8.axis('off')  # 隐藏坐标轴

    # 表格数据
    table_data = [
        ['资产大类', '文件数量', '占比', '主要格式'],
        ['音频资源', f'{asset_category_data["音频资源"]:,}',
         f'{asset_category_data["音频资源"] / sum(asset_category_data.values()):.1%}', '.wem, .bnk, .opuspak'],
        ['纹理资源', f'{asset_category_data["纹理资源"]:,}',
         f'{asset_category_data["纹理资源"] / sum(asset_category_data.values()):.1%}', '.xbm'],
        ['3D模型资源', f'{asset_category_data["3D模型资源"]:,}',
         f'{asset_category_data["3D模型资源"] / sum(asset_category_data.values()):.1%}', '.mesh, .w2mesh'],
        ['地形资源', f'{asset_category_data["地形资源"]:,}',
         f'{asset_category_data["地形资源"] / sum(asset_category_data.values()):.1%}', '.mlmask, .mlsetup'],
        ['实体与动画', f'{asset_category_data["实体与动画"]:,}',
         f'{asset_category_data["实体与动画"] / sum(asset_category_data.values()):.1%}', '.ent, .anims, .rig'],
        ['材质资源', f'{asset_category_data["材质资源"]:,}',
         f'{asset_category_data["材质资源"] / sum(asset_category_data.values()):.1%}', '.mi, .mt'],
        ['外观资源', f'{asset_category_data["外观资源"]:,}',
         f'{asset_category_data["外观资源"] / sum(asset_category_data.values()):.1%}', '.app'],
        ['总计', f'{sum(asset_category_data.values()):,}', '100.0%', '13种格式']
    ]

    # 创建表格
    table = ax8.table(cellText=table_data[1:], colLabels=table_data[0],
                      cellLoc='center', loc='center',
                      colWidths=[0.2, 0.2, 0.15, 0.45])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)

    # 设置表格样式
    for i in range(len(table_data[0])):
        table[(0, i)].set_facecolor('#FF6B6B')
        table[(0, i)].set_text_props(weight='bold', color='white', fontproperties=font)
        table[(0, i)].set_height(0.1)

    for i in range(1, len(table_data)):
        for j in range(len(table_data[0])):
            table[(i, j)].set_facecolor('#F5F5F5' if i % 2 == 0 else 'white')
            table[(i, j)].set_text_props(fontproperties=font)
            table[(i, j)].set_height(0.08)

    ax8.set_title('资产规模汇总统计', fontproperties=font, fontsize=14, fontweight='bold', pad=20)

    # -------------------------- 保存图表 --------------------------
    output_path = output_dir / 'cyberpunk2077_asset_analysis.png'
    plt.suptitle('赛博朋克2077核心美术资产统计分析报告', fontproperties=font, fontsize=18, fontweight='bold', y=0.98)
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    print(f"图表已保存到: {output_path}")
    print(f"图表包含8个子图：")
    print("1. Top10文件格式数量分布  2. 资产大类占比分布")
    print("3. 核心资源细分分布        4. 所有文件格式数量分布（对数坐标）")
    print("5. 主要资产类型相对比例    6. 文件格式类型分组统计")
    print("7. 重点文件格式占比（环形图）  8. 资产规模汇总统计表")


# -------------------------- 主函数 --------------------------
def main():
    # 输出目录（可自行修改）
    output_dir = Path(r'D:\Data\PYh\AmountSy\scnScene')
    output_dir.mkdir(exist_ok=True)  # 确保目录存在

    # 生成图表
    generate_asset_charts(output_dir)

    # 输出文本统计摘要
    print("\n" + "=" * 80)
    print("赛博朋克2077核心美术资产统计摘要")
    print("=" * 80)
    total_files = sum(asset_category_data.values())
    print(f"总文件数量：{total_files:,} 个")
    print(f"文件格式种类：{len(file_format_data)} 种")
    print(f"资产大类：{len(asset_category_data)} 类")
    print("\n文件数量Top3：")
    for i, (fmt, (cnt, desc, _)) in enumerate(sorted(file_format_data.items(), key=lambda x: x[1][0], reverse=True)[:3],
                                              1):
        print(f"  {i}. {fmt} ({desc})：{cnt:,} 个 ({cnt / total_files:.1%})")
    print("\n资产占比Top3：")
    for i, (cat, cnt) in enumerate(sorted(asset_category_data.items(), key=lambda x: x[1], reverse=True)[:3], 1):
        print(f"  {i}. {cat}：{cnt:,} 个 ({cnt / total_files:.1%})")


if __name__ == '__main__':
    # 安装依赖检查
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