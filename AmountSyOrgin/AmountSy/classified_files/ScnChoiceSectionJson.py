import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体和图表样式

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 若为Windows系统，取消注释此行
plt.rcParams['axes.unicode_minus'] = False
plt.style.use('default')

# 1. 数据预处理（修正后：确保所有列表长度一致，共59条数据）
data = {
    'quest_category': [
        'main_quests/part1', 'main_quests/prologue', 'main_quests/epilogue',
        'side_quests/sq027', 'side_quests/sq011', 'side_quests/sq026', 'side_quests/sq023',
        'side_quests/sq012', 'side_quests/sq017', 'side_quests/sq021', 'side_quests/sq031',
        'side_quests/sq030', 'side_quests/sq029', 'side_quests/sq004', 'side_quests/sq024',
        'side_quests/sq006', 'side_quests/sq032', 'side_quests/sq018', 'side_quests/sq025',
        'minor_quests/mq025', 'minor_quests/mq026', 'side_quests/sq028', 'minor_quests/mq037',
        'minor_quests/mq019', 'minor_quests/mq028', 'minor_quests/mq009', 'minor_quests/mq000',
        'minor_quests/mq014', 'minor_quests/mq006', 'minor_quests/mq040', 'minor_quests/mq010',
        'minor_quests/mq032', 'minor_quests/mq001', 'minor_quests/mq018', 'minor_quests/mq008',
        'minor_quests/mq023', 'minor_quests/mq007', 'holocalls', 'minor_quests/mq015',
        'minor_quests/mq002', 'minor_quests/mq033', 'minor_quests/mq024', 'minor_quests/mq016',
        'minor_quests/mq030', 'minor_quests/mq017', 'minor_quests/mq013', 'minor_quests/mq021',
        'minor_quests/mq012', 'minor_quests/mq003', 'minor_quests/mq035', 'minor_quests/mq036',
        'minor_quests/mq042', 'minor_quests/mq011', 'minor_quests/mq005', 'minor_quests/mq041',
        'minor_quests/mq038', 'minor_quests/mq022', 'minor_quests/mq029', 'minor_quests/mq027',
        'minor_quests/mq034'
    ],
    'scene_count': [
        217, 108, 36, 20, 11, 17, 9, 13, 16, 13, 15, 10, 7, 9, 13, 10, 7, 11, 11,
        7, 5, 11, 2, 6, 5, 4, 4, 9, 3, 4, 6, 4, 5, 7, 3, 4, 5, 66, 6, 6, 4, 3, 3,
        3, 5, 1, 4, 1, 4, 3, 3, 3, 1, 6, 1, 3, 4, 2, 4, 1, 2
    ],
    'choice_ratio': [
        16.11, 15.29, 19.41, 11.46, 14.35, 21.09, 17.31, 19.96, 14.00, 21.38, 17.20, 22.00,
        14.81, 12.04, 19.44, 21.07, 24.50, 20.74, 17.86, 17.30, 20.67, 19.29, 23.81, 24.00,
        15.82, 25.30, 61.84, 17.60, 17.95, 16.13, 26.92, 18.60, 16.51, 31.82, 13.46, 24.62,
        13.48, 0.00, 25.37, 22.22, 63.16, 36.17, 28.81, 13.51, 26.42, 12.96, 34.00, 10.20,
        23.21, 13.33, 29.27, 19.05, 9.84, 21.21, 21.88, 24.24, 23.68, 36.00, 100.00, 100.00
    ]
}

# 验证数据长度（确保均为59条）
assert len(data['quest_category']) == len(data['scene_count']) == len(data['choice_ratio']), "数据长度不一致"
df = pd.DataFrame(data)

# 提取任务类型（main/side/minor/holocalls）
def get_quest_type(category):
    if 'main_quests' in category:
        return '主线任务'
    elif 'side_quests' in category:
        return '支线任务'
    elif 'minor_quests' in category:
        return '次要任务'
    else:
        return '全息通话'

df['quest_type'] = df['quest_category'].apply(get_quest_type)

# 按场景数量排序（便于可视化）
df = df.sort_values('scene_count', ascending=False).reset_index(drop=True)

# 2. 创建图表（柱状图+折线图组合）
fig, ax1 = plt.subplots(figsize=(16, 10))

# 定义颜色和标记映射
colors = {'主线任务': '#2E86AB', '支线任务': '#A23B72', '次要任务': '#F18F01', '全息通话': '#C73E1D'}
markers = {'主线任务': 'o', '支线任务': 's', '次要任务': '^', '全息通话': 'D'}

# 绘制柱状图（场景数量）
x_pos = np.arange(len(df))
for quest_type in df['quest_type'].unique():
    mask = df['quest_type'] == quest_type
    ax1.bar(x_pos[mask], df.loc[mask, 'scene_count'],
            label=quest_type, color=colors[quest_type], alpha=0.7, edgecolor='white', linewidth=0.5)

# 设置左Y轴（场景数量）
ax1.set_xlabel('任务名称', fontsize=12, fontweight='bold')
ax1.set_ylabel('场景数量', fontsize=12, fontweight='bold', color='#333333')
ax1.tick_params(axis='y', labelcolor='#333333')
ax1.set_yscale('log')  # 对数刻度（适配1-217的巨大差异）
ax1.grid(axis='y', alpha=0.3, linestyle='--')

# 创建右Y轴（选择比例）
ax2 = ax1.twinx()

# 绘制折线图（选择比例）
for quest_type in df['quest_type'].unique():
    mask = df['quest_type'] == quest_type
    ax2.plot(x_pos[mask], df.loc[mask, 'choice_ratio'],
             marker=markers[quest_type], markersize=6, linewidth=2,
             label=quest_type, color=colors[quest_type], alpha=0.9)

# 设置右Y轴（选择比例）
ax2.set_ylabel('选择比例 (%)', fontsize=12, fontweight='bold', color='#666666')
ax2.tick_params(axis='y', labelcolor='#666666')
ax2.set_ylim(0, 110)  # 预留10%余量，避免100%数据超出范围
ax2.axhline(y=20, color='gray', linestyle='--', alpha=0.5, label='20%基准线')

# 优化X轴标签（避免拥挤）
ax1.set_xticks(x_pos[::3])  # 每隔3个标签显示1个
ax1.set_xticklabels(df['quest_category'].iloc[::3], rotation=45, ha='right', fontsize=8)
ax1.set_xlim(-0.5, len(df)-0.5)

# 合并图例（双轴图例统一显示）
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
# 去重（保留唯一图例）
unique_labels = list(dict.fromkeys(labels1 + labels2))
unique_lines = []
for label in unique_labels:
    if label in labels1:
        unique_lines.append(lines1[labels1.index(label)])
    else:
        unique_lines.append(lines2[labels2.index(label)])
ax1.legend(unique_lines, unique_labels, loc='upper right', framealpha=0.9, shadow=True, fontsize=10)

# 添加标题和注释
plt.title('游戏任务场景数量与选择比例对比分析', fontsize=16, fontweight='bold', pad=20)
fig.text(0.02, 0.02, '注：左轴为场景数量（对数刻度），右轴为选择比例；颜色/标记区分任务类型',
         fontsize=9, style='italic', color='#666666')

# 调整布局（避免标签被截断）
plt.tight_layout()

# 保存图片（可选，支持高分辨率）
# plt.savefig('quest_analysis.png', dpi=300, bbox_inches='tight')

# 显示图表
plt.show()