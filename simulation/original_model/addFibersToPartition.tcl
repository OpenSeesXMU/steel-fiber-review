# =====================================================================
# Script: addFibersToPartition.tcl
# Function: Read global fiber data and assemble fibers for current PID
# =====================================================================

set fp [open "global_fiber_data.txt" r]
set fiber_data [read $fp]
close $fp

set lines [split $fiber_data "\n"]
set matTag 100 
set Af 62.8  
set local_fiber_count 0

foreach line $lines {
    if {[string length $line] < 5} { continue }
    
    set parts [split $line " "]
    set owner_pid [lindex $parts 0]
    set cNode1 [lindex $parts 1]
    set cNode2 [lindex $parts 2]
    set x1 [lindex $parts 3]
    set y1 [lindex $parts 4]
    set z1 [lindex $parts 5]
    set x2 [lindex $parts 6]
    set y2 [lindex $parts 7]
    set z2 [lindex $parts 8]
    set fNode1 [lindex $parts 9]
    set fNode2 [lindex $parts 10]
    set fEle [lindex $parts 11]

    # 防线1：是不是分给我的任务？
    if {$pid == $owner_pid} {
        
        # 防线2：这两个节点到底在不在我的内存里？
        set has_n1 [expr {[catch {nodeCoord $cNode1} check1] == 0 && [llength $check1] > 0}]
        set has_n2 [expr {[catch {nodeCoord $cNode2} check2] == 0 && [llength $check2] > 0}]

        if {$has_n1 == 1 && $has_n2 == 1} {
            node $fNode1 $x1 $y1 $z1
            node $fNode2 $x2 $y2 $z2
            
            # 锁死旋转自由度防止奇异矩阵
            fix $fNode1 0 0 0 1 1 1
            fix $fNode2 0 0 0 1 1 1
            
            element corotTruss $fEle $fNode1 $fNode2 $Af $matTag
            
            equalDOF $cNode1 $fNode1 1 2 3
            equalDOF $cNode2 $fNode2 1 2 3
            
            incr local_fiber_count
        }
    }
}
puts "PID $pid: Successfully verified and created $local_fiber_count fibers!"