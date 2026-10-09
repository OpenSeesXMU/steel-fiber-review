# =====================================================================
# OpenSeesMP Main Script (Macro-Model + AI Discrete Fibers)
# =====================================================================
wipe ;
logFile screen.out
model basic -ndm 3 -ndf 6

set pid [getPID]
set np [getNP]

puts "==================================================="
puts " Processor PID: $pid has started, initializing..."
puts "==================================================="

source material.tcl
source fiber_materials.tcl
source fibers.tcl

set dt 0.02
set tol 5.0e-2

if {$pid == 0} {
    catch {file mkdir "./output"}
    catch {file mkdir "./output/recorder_data"}
}
after 500 

catch {file mkdir "./output/recordEachFrameNodeDispl$pid"}
catch {file mkdir "./output/recordEachFrameStrainStress$pid"}
catch {file mkdir "./output/recordEachFrameSteelForce$pid"}

puts "PID $pid: Reading concrete mesh nodes and elements..."
source "node$pid.tcl"
source "fix$pid.tcl"
source "element$pid.tcl"
source "recordInitNodeCoord$pid.tcl"

# 1. 唤醒 Python 并清理旧文件 (只有 PID 0 执行)
if {$pid == 0} {
    puts "---------------------------------------------------"
    puts "PID 0: Waking up Python engine..."
    
    # 强制清理上一局的残留，确保安全
    catch {file delete -force "global_fiber_data.txt"}
    catch {file delete -force "python_done.flag"}
    
    if {[catch {exec python generateFibers.py} py_result]} {
        puts "PID 0: Python execution ERROR -> $py_result"
    } else {
        puts "PID 0: Python execution SUCCESS! Output: \n$py_result"
    }
}

# 2. 🚨 所有人屏息等待发令枪！
puts "PID $pid: Waiting for python_done.flag..."
set waitCounter 0
set maxWait 600  
while {![file exists "python_done.flag"] && $waitCounter < $maxWait} {
    after 500
    incr waitCounter
}

if {![file exists "python_done.flag"]} {
    puts "FATAL ERROR (PID $pid): Timeout waiting for python_done.flag!"
    exit -1
}
after 500 

# 3. 枪声响起，一起读取！
puts "PID $pid: Signal received! Assembling fibers into partition..."
source addFibersToPartition.tcl
puts "PID $pid: Fiber assembly complete!"

# 4. 配置防死锁求解器
puts "PID $pid: Configuring parallel solver (MUMPS)..."
# 改用 Penalty 彻底防止多核 equalDOF 通讯死锁
constraints Penalty 1.0e12 1.0e12
numberer ParallelPlain
system Mumps -ICNTL14 300
test NormDispIncr $tol 5 1
algorithm Newton
integrator LoadControl 0.1
analysis Static

puts "PID $pid: Starting initial static analysis..."
analyze 10
loadConst -time 0.0

puts "PID $pid: Entering dynamic/loading phase..."
source divideStepAnalysis.tcl 

puts "==================================================="
puts " Processor PID: $pid completed all tasks!"
puts "==================================================="
wipe ;