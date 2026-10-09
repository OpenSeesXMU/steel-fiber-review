# File: generateGlobalFibers.tcl
# 由PID 0生成全局纤维数据

puts "PID 0: 开始生成全局钢纤维数据..."

# ==================== 参数定义 ====================
set fiberNum       10000      ;# 纤维总数
set fiberE        2.0e11     ;# 弹性模量 (Pa)
set fiberYield    500e6      ;# 屈服应力 (Pa)
set fiberArea     0.0000785  ;# 截面积 (m^2)，直径10mm
set fiberLength   0.05       ;# 长度 (m)，50mm

# 纤维分布范围 - 根据你的模型尺寸调整！
# 整体模型范围: X:0-2240, Y:0-448, Z:0-2688 (单位可能是mm)
# 转换为米，假设原单位是mm: 除以1000
set scale 0.001  ;# 如果原坐标是mm，则转换为米

set xMin [expr 0.0 * $scale]
set xMax [expr 2240.0 * $scale]
set yMin [expr 0.0 * $scale]
set yMax [expr 448.0 * $scale]
set zMin [expr 0.0 * $scale]
set zMax [expr 2688.0 * $scale]

# 固定随机种子
expr srand(12345)

# 打开文件准备写入
set fiberDataFile [open "global_fiber_data.txt" w]
puts $fiberDataFile "# 全局纤维数据 - 请勿手动修改"
puts $fiberDataFile "# 总数: $fiberNum"
puts $fiberDataFile "# 格式: fiberID x1 y1 z1 x2 y2 z2"

# ==================== 生成循环 ====================
for {set i 1} {$i <= $fiberNum} {incr i} {
    # 随机起点
    set x1 [expr $xMin + rand() * ($xMax - $xMin)]
    set y1 [expr $yMin + rand() * ($yMax - $yMin)]
    set z1 [expr $zMin + rand() * ($zMax - $zMin)]
    
    # 随机方向
    set theta [expr rand() * 2.0 * 3.14159265359]
    set phi   [expr acos(2.0 * rand() - 1.0)]
    set ux [expr sin($phi) * cos($theta)]
    set uy [expr sin($phi) * sin($theta)]
    set uz [expr cos($phi)]
    
    # 计算终点
    set x2 [expr $x1 + $ux * $fiberLength]
    set y2 [expr $y1 + $uy * $fiberLength]
    set z2 [expr $z1 + $uz * $fiberLength]
    
    # 写入文件
    puts $fiberDataFile "$i $x1 $y1 $z1 $x2 $y2 $z2"
    
    if {$i % 2000 == 0} {
        puts "PID 0: 已生成 $i / $fiberNum 根纤维数据..."
    }
}

close $fiberDataFile
puts "PID 0: 全局纤维数据已保存至 global_fiber_data.txt"