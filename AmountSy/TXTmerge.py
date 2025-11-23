
import os

input_dir=r"D:\Data\PYh\AmountSy\Out"
output_file=r"D:\Data\PYh\AmountSy\OutTXT.txt"
def merge_txt_files(input_dir, output_file, include_subdirs=False):
    """
    合并文件夹中的所有TXT文件到一个输出文件

    参数:
        input_dir: 包含TXT文件的文件夹路径
        output_file: 合并后的输出文件路径
        include_subdirs: 是否包含子文件夹中的TXT文件（默认不包含）
    """
    # 检查输入目录是否存在
    if not os.path.isdir(input_dir):
        print(f"错误：输入目录 '{input_dir}' 不存在！")
        return

    # 收集所有TXT文件路径
    txt_files = []
    for root, dirs, files in os.walk(input_dir):
        # 如果不包含子文件夹，只处理当前目录
        if not include_subdirs and root != input_dir:
            continue

        # 筛选出TXT文件
        for file in files:
            if file.lower().endswith('.txt'):
                txt_path = os.path.join(root, file)
                txt_files.append(txt_path)

    if not txt_files:
        print(f"提示：在 '{input_dir}' 下未找到任何TXT文件！")
        return

    # 合并文件内容
    with open(output_file, 'w', encoding='utf-8') as out_f:
        # 写入文件头信息
        out_f.write(f"===== 合并文件开始 =====")
        out_f.write(f"\n合并时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        out_f.write(f"源文件夹: {input_dir}\n")
        out_f.write(f"包含文件数: {len(txt_files)}\n")
        out_f.write(f"包含子文件夹: {'是' if include_subdirs else '否'}\n")
        out_f.write(f"========================\n\n")

        # 逐个写入TXT文件内容
        for i, txt_path in enumerate(txt_files, 1):
            try:
                with open(txt_path, 'r', encoding='utf-8') as in_f:
                    # 写入文件名作为分隔
                    out_f.write(f"[{i}/{len(txt_files)}] 文件名: {os.path.basename(txt_path)}\n")
                    out_f.write(f"文件路径: {txt_path}\n")
                    out_f.write("-" * 50 + "\n")
                    # 写入文件内容
                    out_f.write(in_f.read())
                    out_f.write("\n\n" + "=" * 50 + "\n\n")
                print(f"已处理: {txt_path}")
            except Exception as e:
                print(f"处理失败 {txt_path}: {str(e)}")
                out_f.write(f"[{i}/{len(txt_files)}] 处理失败: {txt_path}\n")
                out_f.write(f"错误信息: {str(e)}\n\n")

    print(f"\n合并完成！共处理 {len(txt_files)} 个TXT文件")
    print(f"结果已保存到: {output_file}")


if __name__ == "__main__":
    import datetime

    # 配置参数（可根据需要修改）
    INPUT_DIR = r"D:\Data\PYh\AmountSy\Out"  # 存放TXT文件的文件夹
    OUTPUT_FILE = r"D:\Data\PYh\AmountSy\OutTXT.txt"  # 合并后的输出文件
    INCLUDE_SUBDIRS = False  # 是否包含子文件夹中的TXT文件

    # 执行合并
    merge_txt_files(INPUT_DIR, OUTPUT_FILE, INCLUDE_SUBDIRS)