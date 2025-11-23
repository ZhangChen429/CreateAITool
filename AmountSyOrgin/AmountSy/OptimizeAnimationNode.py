# 读取原始数据（假设原始文件路径为 animation_files_optimized.txt，可根据实际修改）
input_file = "D:/Data/PYh/AmountSy/Out/animation_files_optimized.txt"
output_dir = "classified_files/"

import os
# 创建输出目录
os.makedirs(output_dir, exist_ok=True)

# 定义分类关键词（统一小写匹配，避免大小写问题）
categories = {
    "Dirt": ["dirt"],
    "Generic": ["generic"],
    "Idle": ["idle"],
    "Stand": ["stand"],
    "Kneel": ["kneel"],
    "Sit": ["sit"],
    "Lie": ["lie"],
    "Lean Left": ["lean left"],
    "Lean Right": ["lean right"],
    "Lean Forward": ["lean forward"],
    "Lean Backward": ["lean backward"]
}

# 初始化每个分类的内容列表
category_contents = {cat: [] for cat in categories.keys()}

# 读取并解析原始文件
with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()
    current_file = ""
    for line in lines:
        # 提取文件名（匹配 "文件名: xxx.anims" 格式）
        if line.startswith("文件名:"):
            current_file = line.strip()
        # 提取相对路径（匹配 "相对路径: xxx" 格式）
        elif line.startswith("相对路径:"):
            current_path = line.strip()
            # 组合文件信息
            file_info = f"{current_file}\n{current_path}\n{'-'*50}\n"
            # 转换为小写进行关键词匹配
            lower_info = (current_file + current_path).lower()
            # 匹配对应分类并添加
            for cat, keywords in categories.items():
                for kw in keywords:
                    if kw in lower_info:
                        category_contents[cat].append(file_info)
                        break  # 避免同一关键词重复匹配

# 将每个分类的内容写入对应文件
for cat, contents in category_contents.items():
    output_file = os.path.join(output_dir, f"{cat}_classified.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"【{cat}分类文件】\n")
        f.write(f"匹配关键词：{categories[cat]}\n")
        f.write(f"文件总数：{len(contents)}\n")
        f.write("="*60 + "\n\n")
        f.writelines(contents)
    print(f"{cat}分类完成，共{len(contents)}个文件，保存至 {output_file}")

print("所有分类任务执行完毕！")