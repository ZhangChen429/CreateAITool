import matplotlib.pyplot as plt
import numpy as np

# 数据整理（排除小计行，保留有效任务）
tasks = [
    ("q000", "三个出身序章", 75, "超大型"),
    ("q001", "救援+义体医生+兜风", 71, "超大型"),
    ("q003", "接货", 49, "大型"),
    ("q004", "情报", 30, "中型"),
    ("q005", "劫案", 40, "超大型"),
    ("q101", "争分夺秒", 41, "大型"),
    ("q103", "Maelstrom后续", 45, "中型"),
    ("q104", "强尼黑梦相关", 33, "中型"),
    ("q105", "主线任务", 92, "超大型"),
    ("q108", "Johnny剧情", 51, "大型"),
    ("q110", "主线任务", 90, "超大型"),
    ("q112", "搜索与摧毁", 53, "大型"),
    ("q113", "街头巡查/荒坂线", 30, "中型"),
    ("q114", "鬼镇/Panam线", 47, "超大型"),
    ("q115", "夜曲 Op55N1", 50, "超大型"),
    ("q116", "永生/神舆", 16, "中型"),
    ("q201", "结局1", 25, "中型"),
    ("q202", "结局2", 16, "中型"),
    ("q203", "结局3", 27, "中型"),
    ("q204", "结局4", 26, "中型"),
]

# 拆分数据列
task_codes = [t[0] for t in tasks]
task_names = [t[1] for t in tasks]
scene_nums = [t[2] for t in tasks]
complexity = [t[3] for t in tasks]

# 复杂度-颜色映射（超大型=红色，大型=橙色，中型=蓝色）
color_map = {
    "超大型": "#E74C3C",
    "大型": "#F39C12",
    "中型": "#3498DB"
}
bar_colors = [color_map[c] for c in complexity]

# 设置中文字体（避免中文乱码）
plt.rcParams['font.sans-serif'] = ['SimHei']  # Windows用黑体，Mac用'Arial Unicode MS'
plt.rcParams['axes.unicode_minus'] = False

# 创建画布和子图
fig, ax = plt.subplots(figsize=(14, 8))  # 宽14英寸，高8英寸

# 绘制柱状图（x轴为任务代码，y轴为Scene数量）
bars = ax.bar(
    x=task_codes,
    height=scene_nums,
    color=bar_colors,
    alpha=0.8,  # 透明度
    edgecolor="black",  # 柱子边框色
    linewidth=0.5
)

# 在柱子顶部标注具体数值
for bar, num in zip(bars, scene_nums):
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width()/2.,  # x坐标（柱子中心）
        height + 1,  # y坐标（柱子顶部+1，避免贴边）
        str(num),  # 标注文本（Scene数量）
        ha='center', va='bottom', fontsize=10, fontweight='bold'
    )

# 设置图表标题和坐标轴标签
ax.set_title("赛博朋克2077 各任务 Scene场景数量对比", fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel("任务代码", fontsize=12, fontweight='bold')
ax.set_ylabel("Scene场景数量", fontsize=12, fontweight='bold')

# 调整x轴标签（避免重叠）
ax.tick_params(axis='x', rotation=45)  # 旋转45度
ax.set_xticks(range(len(task_codes)))
ax.set_xticklabels(task_codes, fontsize=10)

# 设置y轴范围（底部留空，顶部多10%，更美观）
ax.set_ylim(0, max(scene_nums) * 1.1)

# 添加网格线（y轴，辅助读数）
ax.yaxis.grid(True, alpha=0.3, linestyle='--')
ax.set_axisbelow(True)

# 添加图例（按复杂度区分）
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor=color_map["超大型"], label='超大型'),
    Patch(facecolor=color_map["大型"], label='大型'),
    Patch(facecolor=color_map["中型"], label='中型')
]
ax.legend(handles=legend_elements, loc='upper right', fontsize=10)

# 调整布局（避免标签被截断）
plt.tight_layout()

# 导出图片（高清PNG格式）
plt.savefig("cyberpunk2077_task_scene_bar.png", dpi=300, bbox_inches='tight')
plt.show()