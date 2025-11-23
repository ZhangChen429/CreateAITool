import json
import os
from pathlib import Path
from collections import defaultdict

# Base directory (游戏文件所在目录，可根据实际情况修改)
base_dir = r"D:\AppSoft\Sy2077\2077\2077\CDPR2077\r6\depot\base\quest"

# Find all .scnlocjson files (递归查找所有目标文件)
scnlocjson_files = list(Path(base_dir).rglob("*.scnlocjson"))

print(f"Found {len(scnlocjson_files)} .scnlocjson files\n")
print("Processing files...\n")

# Data structures (数据存储结构)
scene_data = []
quest_type_stats = defaultdict(lambda: {"scenes": 0, "total_lines": 0})
total_dialogue_lines = 0
total_scenes = 0

# Process each file (批量处理文件)
for idx, file_path in enumerate(scnlocjson_files):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        scene_name = data.get("SceneName", "Unknown")
        scene_path = str(file_path.relative_to(Path(base_dir)))
        sections = data.get("SectionsInScene", [])
        num_sections = len(sections)

        # Count total dialogue lines and collect speakers (统计对话行和说话人)
        total_lines = 0
        speakers = set()

        for section in sections:
            lines = section.get("LinesInSection", [])
            total_lines += len(lines)

            for line in lines:
                speaker = line.get("Speaker")
                if speaker and speaker.strip():
                    speakers.add(speaker)

        # Determine quest type from path (从文件路径提取任务类型)
        parts = file_path.relative_to(Path(base_dir)).parts
        quest_type = parts[0] if parts else "unknown"

        # Store scene data (存储场景数据)
        scene_info = {
            "scene_name": scene_name,
            "scene_path": scene_path,
            "num_sections": num_sections,
            "total_lines": total_lines,
            "speakers": sorted(list(speakers)),
            "num_speakers": len(speakers),
            "quest_type": quest_type
        }
        scene_data.append(scene_info)

        # Update quest type stats (更新任务类型统计)
        quest_type_stats[quest_type]["scenes"] += 1
        quest_type_stats[quest_type]["total_lines"] += total_lines

        # Update totals (更新总体统计)
        total_dialogue_lines += total_lines
        total_scenes += 1

        # Progress indicator (进度提示)
        if (idx + 1) % 50 == 0:
            print(f"Processed {idx + 1}/{len(scnlocjson_files)} files...")

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        continue

print(f"\nProcessed {total_scenes} files successfully\n")

# Sort scenes by dialogue count (按对话行数降序排序)
scene_data.sort(key=lambda x: x["total_lines"], reverse=True)

# Generate report (生成报告)
print("=" * 100)
print("COMPREHENSIVE SCNLOCJSON ANALYSIS REPORT")
print("=" * 100)
print()

# Overall Statistics (总体统计)
print("=" * 100)
print("OVERALL STATISTICS")
print("=" * 100)
print(f"Total Scenes Analyzed: {total_scenes}")
print(f"Total Dialogue Lines: {total_dialogue_lines:,}")
print(f"Average Lines per Scene: {total_dialogue_lines / total_scenes if total_scenes > 0 else 0:.2f}")
print()

# Top 10 Scenes (Top10对话最多的场景)
print("=" * 100)
print("TOP 10 SCENES WITH MOST DIALOGUE")
print("=" * 100)
print(f"{'Rank':<6} {'Scene Name':<50} {'Lines':<10} {'Sections':<10} {'Speakers':<10}")
print("-" * 100)
for i, scene in enumerate(scene_data[:10], 1):
    print(f"{i:<6} {scene['scene_name']:<50} {scene['total_lines']:<10} {scene['num_sections']:<10} {scene['num_speakers']:<10}")
print()

# Quest Type Breakdown (按任务类型分类统计)
print("=" * 100)
print("BREAKDOWN BY QUEST TYPE")
print("=" * 100)
print(f"{'Quest Type':<30} {'Scenes':<15} {'Total Lines':<15} {'Avg Lines/Scene':<20}")
print("-" * 100)
for quest_type in sorted(quest_type_stats.keys()):
    stats = quest_type_stats[quest_type]
    avg_lines = stats["total_lines"] / stats["scenes"] if stats["scenes"] > 0 else 0
    print(f"{quest_type:<30} {stats['scenes']:<15} {stats['total_lines']:<15,} {avg_lines:<20.2f}")
print()

# Full Scene Table (完整场景列表)
print("=" * 100)
print("COMPLETE SCENE LIST (Sorted by Dialogue Count - Descending)")
print("=" * 100)
print(f"{'Scene Name':<60} {'Lines':<10} {'Sections':<10} {'Speakers':<10} {'Quest Type':<20}")
print("-" * 100)
for scene in scene_data:
    print(f"{scene['scene_name']:<60} {scene['total_lines']:<10} {scene['num_sections']:<10} {scene['num_speakers']:<10} {scene['quest_type']:<20}")
print()

# Export detailed data to JSON (导出详细数据到JSON文件)
output_file = r"D:\Data\PYh\AmountSy\Out\scnlocjson_analysis_detailed.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        "summary": {
            "total_scenes": total_scenes,
            "total_dialogue_lines": total_dialogue_lines,
            "average_lines_per_scene": total_dialogue_lines / total_scenes if total_scenes > 0 else 0
        },
        "quest_type_stats": dict(quest_type_stats),
        "scenes": scene_data
    }, f, indent=2, ensure_ascii=False)

print(f"Detailed analysis exported to: {output_file}")
print()

# Additional statistics (补充统计)
print("=" * 100)
print("ADDITIONAL STATISTICS")
print("=" * 100)
scenes_with_dialogue = sum(1 for s in scene_data if s["total_lines"] > 0)
scenes_without_dialogue = total_scenes - scenes_with_dialogue
print(f"Scenes with dialogue: {scenes_with_dialogue}")
print(f"Scenes without dialogue: {scenes_without_dialogue}")
if scene_data:
    largest_scene = max(scene_data, key=lambda x: x["total_lines"])
    most_speakers_scene = max(scene_data, key=lambda x: x["num_speakers"])
    print(f"Largest scene (by lines): {largest_scene['scene_name']} with {largest_scene['total_lines']:,} lines")
    print(f"Most speakers in a scene: {most_speakers_scene['scene_name']} with {most_speakers_scene['num_speakers']} speakers")
print()

print("Analysis complete!")