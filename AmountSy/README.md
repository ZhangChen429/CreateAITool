# Scene Solution JSON to Excel Converter

将 scene solution 扫描生成的 JSON 文件转换为 Excel 表格的工具。

## 安装依赖

在命令行中运行：

```cmd
cd D:\Data\PYh\AmountSy
pip install -r requirements.txt
```

## 使用方法

### 方法 1：直接运行（会提示输入文件路径）

```cmd
python scene_json_to_excel.py
```

然后输入 JSON 文件的完整路径。

### 方法 2：命令行参数

```cmd
python scene_json_to_excel.py D:\scene_detailed.json
```

### 方法 3：拖拽文件

将 JSON 文件直接拖放到 `scene_json_to_excel.py` 上。

## 输出说明

脚本会生成一个与 JSON 文件同名的 `.xlsx` 文件，包含以下工作表：

1. **Summary（摘要）**
   - Scene Path：场景文件路径
   - Has Interruption Scenarios：是否有中断场景
   - Has Event Execution Tags：是否有事件执行标签
   - Total Nodes：总节点数

2. **Interruption Scenarios（中断场景）**
   - Scene Path：场景文件路径
   - Type：中断场景类型

3. **Event Execution Tags（事件执行标签）**
   - Scene Path：场景文件路径
   - Type：标签类型

4. **Node Type Count (Detail)（节点类型统计-详细）**
   - Scene Path：场景文件路径
   - Node Type：节点类型名称
   - Count：该类型节点在该场景中的数量

5. **Node Type Count (Summary)（节点类型统计-汇总）**
   - Node Type：节点类型名称
   - Count：该类型节点在所有场景中的总数量（降序排列）

## 示例

```cmd
cd D:\Data\PYh\AmountSy
python scene_json_to_excel.py D:\scene_detailed.json
```

执行后会生成 `D:\scene_detailed.xlsx`

## 注意事项

- 确保已安装 Python 3.7 或更高版本
- JSON 文件必须是使用 `-mode=detailedNodes` 扫描生成的格式
- 输出文件会自动添加表头样式和自动调整列宽
