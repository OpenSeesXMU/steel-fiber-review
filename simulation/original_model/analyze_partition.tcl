# 文件：analyze_partition_robust.tcl
# 功能：鲁棒性更强的分区分析脚本，处理多种node命令格式
# 用法：在OpenSees命令行中执行 source analyze_partition_robust.tcl

puts "开始分析模型分区信息 (增强版)..."
puts "========================================"

# 第一步：自动检测分区数量
set numParts 0
while {[file exists "node$numParts.tcl"]} {
    incr numParts
}
if {$numParts == 0} {
    puts "错误：未找到任何 nodeX.tcl 文件！请确认脚本在当前模型目录下运行。"
    exit
}
puts "自动检测到分区数量：$numParts"
puts "----------------------------------------"

# 第二步：循环分析每个分区文件
for {set pid 0} {$pid < $numParts} {incr pid} {
    set filename "node$pid.tcl"
    
    # 初始化
    set minX 1e20; set maxX -1e20
    set minY 1e20; set maxY -1e20
    set minZ 1e20; set maxZ -1e20
    set nodeCount 0
    set problematicLines 0

    # 打开并读取文件
    set fp [open $filename r]
    while {[gets $fp line] >= 0} {
        # 1. 去除首尾空白字符
        set line [string trim $line]
        
        # 2. 跳过空行和注释行（以#开头）
        if {$line eq "" || [string index $line 0] == "#"} {
            continue
        }
        
        # 3. 检查是否为node命令（允许行首有空格，且不区分大小写）
        if {[string match -nocase "node*" $line]} {
            # 4. 移除行内注释（如果存在）
            set line [lindex [split $line "#"] 0]
            set line [string trim $line]
            
            # 5. 分割行：使用正则表达式分割连续空白字符（包括空格和制表符）
            set fields [regexp -inline -all {\S+} $line]
            
            # 调试：打印前几行的解析情况
            if {$nodeCount < 3} {
                puts "  调试: 解析行 -> $fields"
            }
            
            # 6. 验证字段数量至少为5 (node, id, x, y, z)
            if {[llength $fields] >= 5} {
                # 尝试提取坐标，忽略第一个字段（“node”），取第2、3、4个字段作为x, y, z
                # 注意：节点ID在fields[1]，坐标在fields[2,3,4]
                set x_str [lindex $fields 2]
                set y_str [lindex $fields 3]
                set z_str [lindex $fields 4]
                
                # 安全地转换为数字
                if {[string is double -strict $x_str] && 
                    [string is double -strict $y_str] && 
                    [string is double -strict $z_str]} {
                    
                    set x [expr {double($x_str)}]
                    set y [expr {double($y_str)}]
                    set z [expr {double($z_str)}]
                    
                    # 更新范围
                    if {$x < $minX} {set minX $x}
                    if {$x > $maxX} {set maxX $x}
                    if {$y < $minY} {set minY $y}
                    if {$y > $maxY} {set maxY $y}
                    if {$z < $minZ} {set minZ $z}
                    if {$z > $maxZ} {set maxZ $z}
                    
                    incr nodeCount
                } else {
                    # 转换失败，记录问题行
                    incr problematicLines
                    if {$problematicLines <= 3} {
                        puts "  警告: 无法解析坐标，行内容: $line"
                    }
                }
            } else {
                # 字段数不足，记录问题行
                incr problematicLines
                if {$problematicLines <= 3} {
                    puts "  警告: 字段数不足，行内容: $line"
                }
            }
        }
    }
    close $fp
    
    # 输出该分区的分析结果
    puts "分区 $pid  ($filename):"
    puts "  成功读取节点数: $nodeCount"
    if {$problematicLines > 0} {
        puts "  有问题行数: $problematicLines"
    }
    if {$nodeCount > 0} {
        puts "  空间范围:"
        puts "    X: [format "%.3f" $minX]  ~  [format "%.3f" $maxX]  (宽度: [format "%.3f" [expr {$maxX - $minX}]])"
        puts "    Y: [format "%.3f" $minY]  ~  [format "%.3f" $maxY]  (宽度: [format "%.3f" [expr {$maxY - $minY}]])"
        puts "    Z: [format "%.3f" $minZ]  ~  [format "%.3f" $maxZ]  (宽度: [format "%.3f" [expr {$maxZ - $minZ}]])"
        puts "  中心点: ([format "%.3f" [expr {($minX+$maxX)/2}]], [format "%.3f" [expr {($minY+$maxY)/2}]], [format "%.3f" [expr {($minZ+$maxZ)/2}]])"
    } else {
        puts "  错误: 此分区未成功读取任何节点！"
    }
    puts ""
}

puts "分析完成！"
puts "========================================"
puts "\n接下来请根据输出判断分区模式："
puts "1. 如果各分区的X/Y/Z范围基本不重叠，则是'规则几何划分'"
puts "2. 如果各分区的X/Y/Z范围严重重叠，则是'图划分'"
puts "\n请将输出结果的关键信息告诉我，特别是："
puts "- 分区0和分区1的X范围分别是多少？"
puts "- 模型整体大概尺寸（所有分区X,Y,Z的最小/最大值）"
