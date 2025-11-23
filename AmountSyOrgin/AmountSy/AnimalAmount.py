import os

# 基础目录设置
BASE_DIR = r"D:\AppSoft\Sy2077\2077\2077\CDPR2077\r6\depot\base\animations"
OUTPUT_FILE = r"D:\Data\PYh\AmountSy\Out\animation_files统计.txt"
CSV_FILE = r"D:\Data\PYh\AmountSy\Out\animation_files统计.csv"


def get_animation_files(base_dir):
    """获取base_dir下所有*.Animation文件的信息"""
    animation_files = []
    # 递归遍历所有子目录
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.lower().endswith('.anims'):
                # 绝对路径
                abs_path = os.path.join(root, file)
                # 相对路径（相对于BASE_DIR）
                rel_path = os.path.relpath(abs_path, base_dir)
                animation_files.append({
                    'filename': file,
                    'absolute_path': abs_path,
                    'relative_path': rel_path
                })
    return animation_files


def main():
    # 检查基础目录是否存在
    if not os.path.isdir(BASE_DIR):
        print(f"错误：基础目录 '{BASE_DIR}' 不存在！")
        return

    # 获取所有Animation文件信息
    animation_files = get_animation_files(BASE_DIR)
    total = len(animation_files)

    if total == 0:
        print(f"提示：在 '{BASE_DIR}' 下未找到任何*.Animation文件！")
        return

    # 确保输出目录存在
    output_dir = os.path.dirname(OUTPUT_FILE)
    os.makedirs(output_dir, exist_ok=True)

    # 写入文本报告
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("Animation文件统计报告\n")
        f.write(f"统计目录: {BASE_DIR}\n")
        f.write(f"文件总数: {total}\n")
        f.write("========================================\n\n")

        for i, file_info in enumerate(animation_files, 1):
            f.write(f"[{i}/{total}] 文件名: {file_info['filename']}\n")
            f.write(f"  绝对路径: {file_info['absolute_path']}\n")
            f.write(f"  相对路径: {file_info['relative_path']}\n")
            f.write("----------------------------------------\n")

    # 写入CSV文件（便于后续处理）
    with open(CSV_FILE, 'w', encoding='utf-8') as f:
        f.write("序号,文件名,绝对路径,相对路径\n")
        for i, file_info in enumerate(animation_files, 1):
            f.write(f"{i},{file_info['filename']},{file_info['absolute_path']},{file_info['relative_path']}\n")

    # 控制台输出结果
    print(f"统计完成！共找到 {total} 个*.Animation文件")
    print(f"详细报告已保存到: {OUTPUT_FILE}")
    print(f"CSV数据已保存到: {CSV_FILE}")


if __name__ == "__main__":
    main()