import matplotlib.pyplot as plt
import numpy as np
import json

# 设置中文字体（避免中文乱码）
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 读取JSON数据（请替换为你的文件路径）
with open(r"D:\Data\PYh\AmountSy\Out\scnlocjson_analysis_detailed.json", 'r', encoding='utf-8') as f:
    data = json.load(f)

# 提取数据
quest_types = list(data['quest_type_stats'].keys())
scene_counts = [data['quest_type_stats'][qt]['scenes'] for qt in quest_types]
line_counts = [data['quest_type_stats'][qt]['total_lines'] for qt in quest_types]
avg_lines = [line_counts[i]/scene_counts[i] if scene_counts[i]>0 else 0 for i in range(len(quest_types))]

# 1. 任务类型场景数&对话量双轴图
fig, ax1 = plt.subplots(figsize=(12, 6))
x = np.arange(len(quest_types))
width = 0.35

# 场景数柱状图（左轴）
bars1 = ax1.bar(x - width/2, scene_counts, width, label='场景数', color='#2E86AB', alpha=0.8)
ax1.set_xlabel('任务类型', fontsize=12)
ax1.set_ylabel('场景数', fontsize=12, color='#2E86AB')
ax1.tick_params(axis='y', labelcolor='#2E86AB')
ax1.set_xticks(x)
ax1.set_xticklabels(quest_types, rotation=45, ha='right')

# 对话量折线图（右轴）
ax2 = ax1.twinx()
line1 = ax2.plot(x + width/2, line_counts, label='总对话行数', color='#A23B72', marker='o', linewidth=2)
ax2.set_ylabel('总对话行数', fontsize=12, color='#A23B72')
ax2.tick_params(axis='y', labelcolor='#A23B72')

# 添加数值标签
for bar in bars1:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 2, f'{int(height)}', ha='center', va='bottom', fontsize=10)
for i, v in enumerate(line_counts):
    ax2.text(i + width/2, v + 200, f'{int(v)}', ha='center', va='bottom', fontsize=10, color='#A23B72')

# 标题和图例
plt.title('各任务类型场景数与对话量分布', fontsize=14, fontweight='bold')
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
plt.tight_layout()
plt.savefig('任务类型场景数对话量分布.png', dpi=300, bbox_inches='tight')
plt.show()

# 2. Top10场景对话量柱状图
top10_scenes = data['scenes'][:10]
scene_names = [s['scene_name'][:20] + '...' if len(s['scene_name'])>20 else s['scene_name'] for s in top10_scenes]
top10_lines = [s['total_lines'] for s in top10_scenes]

plt.figure(figsize=(12, 6))
bars = plt.barh(scene_names[::-1], top10_lines[::-1], color='#F18F01', alpha=0.8)
plt.xlabel('对话行数', fontsize=12)
plt.ylabel('场景名称', fontsize=12)
plt.title('Top10 对话量最高场景', fontsize=14, fontweight='bold')
plt.grid(axis='x', alpha=0.3)

# 添加数值标签
for i, bar in enumerate(bars):
    width = bar.get_width()
    plt.text(width + 10, bar.get_y() + bar.get_height()/2, f'{int(width)}', ha='left', va='center', fontsize=10)

plt.tight_layout()
plt.savefig('Top10场景对话量.png', dpi=300, bbox_inches='tight')
plt.show()

# 3. 任务类型对话占比饼图
# 筛选占比>0.5%的类型，其余归为"其他"
threshold = sum(line_counts) * 0.005
major_lines = []
major_types = []
other_lines = 0

for qt, lines in zip(quest_types, line_counts):
    if lines >= threshold:
        major_types.append(qt)
        major_lines.append(lines)
    else:
        other_lines += lines

if other_lines > 0:
    major_types.append('其他')
    major_lines.append(other_lines)

plt.figure(figsize=(10, 8))
colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E', '#F9C74F', '#90A959', '#577590']
wedges, texts, autotexts = plt.pie(major_lines, labels=major_types, autopct='%1.1f%%', colors=colors[:len(major_types)],
                                  startangle=90, textprops={'fontsize': 11})
plt.title('各任务类型对话占比', fontsize=14, fontweight='bold')
plt.axis('equal')  # 保证饼图为正圆形
plt.tight_layout()
plt.savefig('任务类型对话占比饼图.png', dpi=300, bbox_inches='tight')
plt.show()