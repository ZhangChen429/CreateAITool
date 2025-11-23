import json
import pandas as pd
from pathlib import Path
from collections import Counter,defaultdict

def json_to_compact_excel(json_files, output_excel):
    compact_data = []
    all_node_names = []  # 存储所有节点名称，用于统计
    target_phase_data=[]
    target_node_names = []  # 新增：仅存储指定路径下的节点名称（用于统计）
    node_phase_map = {}  # 新增：存储节点对应的指定路径阶段（用于高频节点路径填充）
    phase_node_counter = defaultdict(Counter)  # 新增：路径-节点次数映射（核心）
    # 新增：指定需要单独做表格的路径前缀
    TARGET_PATH_PREFIXES = [
        r"base\quest\main_quests",
        r"base\quest\side_quests",
        r"base\quest\minor_quests"
    ]

    for json_file in json_files:
        file_path = Path(json_file)
        if not file_path.exists():
            print(f"⚠️  {json_file} 不存在，跳过")
            continue
        # 读取JSON（兼容中文和特殊字符）
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)

            # 第一次循环：收集所有节点名称
            for phase, nodes in data.get("questphases", {}).items():
                if any(phase.startswith(prefix) for prefix in TARGET_PATH_PREFIXES):
                    phase_counter = Counter()  # 单个路径的节点计数器
                phase_counter = Counter()  # 单个路径的节点计数器
                for node in nodes:
                    node_name = str(node.get("name", "")).strip()
                    if node_name:
                        target_node_names.append(node_name)
                        # 节点-阶段映射（原有）
                        if node_name not in node_phase_map:
                            node_phase_map[node_name] = set()
                        node_phase_map[node_name].add(phase)
                        # 统计当前路径下该节点的出现次数（新增）
                        phase_counter[node_name] += 1
                # 保存当前路径的节点次数统计（新增）
                phase_node_counter[phase] = phase_counter
        # 阶段合并为一行，自动转字符串避免类型错误
        for phase, nodes in data.get("questphases", {}).items():
            compact_data.append({
                "阶段路径": phase,
                "节点ID集合": " | ".join(str(n.get("id", "")) for n in nodes),
                "节点名称集合": " | ".join(str(n.get("name", "")) for n in nodes),
                "节点类名集合": " | ".join(str(n.get("class", "")) for n in nodes),
                "节点路径集合": " | ".join(str(n.get("path", "")) for n in nodes),
                "节点数": len(nodes)
            })
            # 新增：判断是否是指定路径开头，是则添加到目标数据
            if any(phase.startswith(prefix) for prefix in TARGET_PATH_PREFIXES):
                target_phase_data.append({
                    "阶段路径": phase,
                    "节点名称集合": " | ".join(str(n.get("name", "")) for n in nodes),
                    "节点类名集合": " | ".join(str(n.get("class", "")) for n in nodes),
                    "节点数": len(nodes)
                })
        # 统计并按出现次数降序排序（所有节点都展示）
        name_counter = Counter(target_node_names)
        sorted_names = sorted(name_counter.items(), key=lambda x: x[1], reverse=True)

    # 打印统计结果
    print("=" * 60)
    print("🔍 所有节点名称出现次数（按次数降序）：")
    for idx, (name, cnt) in enumerate(sorted_names, 1):
        print(f"  {idx:2d}. {name:<15} → {cnt}次")
    print("=" * 60)
    print(f"📊 总计：{len(name_counter)} 个不同节点，共 {len(target_node_names)} 个节点实例")
    print("=" * 60)
    print("=" * 50)

    # 新增：处理高频节点（≥10次）路径分布表格
    high_freq_nodes = [name for name, cnt in name_counter.items() if cnt >= 10]  # 过滤≥5次的节点
    high_freq_data = []
    for node_name in high_freq_nodes:
        # 填充该节点对应的所有指定路径阶段（用换行分隔，Excel中双击可查看完整内容）
        phases = "\n".join(sorted(node_phase_map.get(node_name, set())))
        high_freq_data.append({
            "高频节点名称（出现≥5次）": node_name,
            "出现次数": name_counter[node_name],
            "包含该节点的指定路径阶段": phases,
            "涉及阶段数": len(node_phase_map.get(node_name, set()))
        })
    df_high_freq = pd.DataFrame(high_freq_data)

    # 新增：路径-高频节点次数矩阵表格（核心需求）
    matrix_data = []
    # 遍历所有指定路径，填充每个高频节点的出现次数
    for phase in sorted(phase_node_counter.keys()):  # 按路径排序，更整齐
        row = {"指定路径": phase}
        # 为每个高频节点填充当前路径下的出现次数（无则填0）
        for node_name in high_freq_nodes:
            row[node_name] = phase_node_counter[phase].get(node_name, 0)
        matrix_data.append(row)
    df_matrix = pd.DataFrame(matrix_data)

    # 核心：保存3个工作表（原有2个 + 新增1个）
    df_all_phase = pd.DataFrame(compact_data)  # 工作表1：所有阶段汇总（原有）
    df_count = pd.DataFrame([  # 工作表2：节点名称统计（原有）
        {"排名": idx + 1, "节点名称": name, "出现次数": cnt}
        for idx, (name, cnt) in enumerate(sorted_names)
    ])
    df_target_phase = pd.DataFrame(target_phase_data)  # 工作表3：指定路径阶段汇总（新增）

    with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
        df_all_phase.to_excel(writer, sheet_name="所有阶段汇总", index=False)
        df_count.to_excel(writer, sheet_name="节点名称统计", index=False)
        df_target_phase.to_excel(writer, sheet_name="指定路径阶段汇总", index=False)
        df_high_freq.to_excel(writer, sheet_name="高频节点路径分布", index=False)  # 新增工作表
        df_matrix.to_excel(writer, sheet_name="路径-高频节点次数矩阵", index=False)  # 新增工作表
    # 打印结果提示（保持原有格式）
    print(f"✅ 两个表格生成完成！→ {output_excel}")
    print(f"   📑 工作表1：阶段节点汇总（{len(compact_data)} 行，一行一个阶段）")
    print(f"   📑 工作表2：节点名称统计（{len(df_count)} 行，按出现次数降序）")
    print(f"   📑 工作表3：指定路径阶段汇总（{len(target_phase_data)} 行，含main/side/minor quests）")
    print(f"   📑 工作表4：高频节点路径分布（{len(df_high_freq)} 行，出现≥10次的节点）")
    if high_freq_nodes:
        print(f"🔍 高频节点列表：{', '.join(high_freq_nodes)}")
    else:
        print("🔍 暂无出现次数≥10次的高频节点")
    print("=" * 50)

if __name__ == "__main__":
    INPUT_JSON = ["无递归quest_all_nodes.txt"]  # 你的JSON文件路径（可添加多个）
    OUTPUT_EXCEL = "quest_nodes_compact.xlsx"  # 输出Excel路径
    json_to_compact_excel(INPUT_JSON, OUTPUT_EXCEL)