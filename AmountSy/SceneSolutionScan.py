import json
import pandas as pd
from pathlib import Path


def read_qempth_to_table(json_file="QEmpthresult.json", output_excel="QEmpthresultClipDPD.xlsx"):
    """
    读取 QEmpthresult.json 文件并转换为 Excel 表格

    Args:
        json_file: JSON 文件路径
        output_excel: 输出的 Excel 文件路径
    """
    # 读取 JSON 文件
    print(f"正在读取 {json_file}...")
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 准备数据列表
    rows = []
    section_clip_summary = []  # 用于第二个Sheet的数据
    section_clip_matrix = []  # 用于第三个Sheet的透视数据
    all_clip_types = set()  # 收集所有Clip类型

    # 遍历所有场景解决方案
    scene_solutions = data.get('scene_solutions', {})

    for scene_path, scene_data in scene_solutions.items():
        sections = scene_data.get('sections', [])

        for section in sections:
            section_name = section.get('section_name', '')
            tracks = section.get('tracks', [])

            # 收集当前Section中的所有Clip类型
            section_clips = []

            for track in tracks:
                track_name = track.get('track_name', '')
                track_type = track.get('track_type', '')
                clips = track.get('clips', [])

                # 收集所有clip类型
                section_clips.extend(clips)

                # 如果有 clips，为每个 clip 创建一行
                if clips:
                    for clip in clips:
                        rows.append({
                            '场景路径': scene_path,
                            '章节名称': section_name,
                            '轨道名称': track_name,
                            '轨道类型': track_type,
                            'Clip': clip,
                            'Clip数量': len(clips)
                        })
                else:
                    # 如果没有 clips，创建一行空的
                    rows.append({
                        '场景路径': scene_path,
                        '章节名称': section_name,
                        '轨道名称': track_name,
                        '轨道类型': track_type,
                        'Clip': '',
                        'Clip数量': 0
                    })

            # 统计当前Section的Clip类型
            unique_clips = list(set(section_clips))  # 去重
            clip_counts = {clip: section_clips.count(clip) for clip in unique_clips}

            # 收集所有Clip类型到全局集合
            all_clip_types.update(unique_clips)

            section_clip_summary.append({
                '场景路径': scene_path,
                '章节名称': section_name,
                '所有Clip类型': ', '.join(sorted(unique_clips)) if unique_clips else '',
                '不同Clip类型数量': len(unique_clips),
                '总Clip数量': len(section_clips),
                'Clip类型详情': str(clip_counts) if clip_counts else ''
            })

            # 为透视表准备数据
            matrix_row = {
                '场景路径': scene_path,
                '章节名称': section_name
            }
            matrix_row.update(clip_counts)
            section_clip_matrix.append(matrix_row)

    # 创建 DataFrame
    df_detail = pd.DataFrame(rows)
    df_summary = pd.DataFrame(section_clip_summary)

    # 创建透视表 DataFrame
    df_pivot = pd.DataFrame(section_clip_matrix)

    # 确保所有Clip类型列都存在，缺失的填充为0
    all_clip_columns = sorted(list(all_clip_types))
    for clip_type in all_clip_columns:
        if clip_type not in df_pivot.columns:
            df_pivot[clip_type] = 0

    # 重新排列列顺序：场景路径、章节名称、然后是所有Clip类型（按字母排序）
    column_order = ['场景路径', '章节名称'] + all_clip_columns
    df_pivot = df_pivot[column_order]

    # 将NaN填充为0
    df_pivot = df_pivot.fillna(0)

    # 将Clip计数转换为整数类型
    for clip_col in all_clip_columns:
        df_pivot[clip_col] = df_pivot[clip_col].astype(int)

    # 保存为 Excel（多个Sheet）
    print(f"正在保存到 {output_excel}...")
    with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
        df_detail.to_excel(writer, sheet_name='详细Clip信息', index=False)
        df_summary.to_excel(writer, sheet_name='Section Clip汇总', index=False)
        df_pivot.to_excel(writer, sheet_name='Clip类型矩阵', index=False)

    print(f"完成！共处理 {len(rows)} 行详细数据，{len(section_clip_summary)} 个Section汇总")
    print(f"发现 {len(all_clip_types)} 种不同的Clip类型")
    print(f"输出文件: {output_excel}")

    # 显示预览
    print("\n详细数据预览:")
    print(df_detail.head(10))
    print("\nSection汇总数据预览:")
    print(df_summary.head(10))
    print("\nClip类型矩阵预览:")
    print(df_pivot.head(10))

    return df_detail, df_summary, df_pivot


if __name__ == "__main__":
    # 执行转换
    df_detail, df_summary, df_pivot = read_qempth_to_table()

    # 可选：同时保存为 CSV 格式
    df_detail.to_csv("QEmpthresult_detail.csv", index=False, encoding='utf-8-sig')
    df_summary.to_csv("QEmpthresult_summary.csv", index=False, encoding='utf-8-sig')
    df_pivot.to_csv("QEmpthresult_pivot.csv", index=False, encoding='utf-8-sig')
    print("同时保存了 CSV 格式: QEmpthresult_detail.csv, QEmpthresult_summary.csv 和 QEmpthresult_pivot.csv")
