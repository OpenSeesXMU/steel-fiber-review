set  minDt  5.e-4

proc divideStepAnalysis {DT  divideNum  tol} {
	puts "function is called..."

	global minDt pid
    set  dt  [ expr   $DT/$divideNum ]
	if {abs($dt) > abs($minDt)} {
		# test NormDispIncr  $tol  4  1
        #---------------------------------------------#
		test NormDispIncr $tol  4  5
		algorithm ModifiedNewton -initial
        #---------------------------------------------#
		integrator LoadControl $dt
		for {set i 0} {$i < $divideNum} {incr i} {
            print integrator
            print algorithm
			analysis Static	
			set ok [analyze 1]
			if {$ok != 0} {
				set ok [divideStepAnalysis $dt $divideNum  $tol]
			}  else {
                if {$pid == 9} {
                    source "recorder.tcl"
                }
            }
		}
		algorithm Newton
	} else {
		integrator LoadControl $DT
		test NormDispIncr $tol  4  5
		algorithm ModifiedNewton -initial
        print integrator
        print algorithm
		analysis Static	
 		set ok [analyze 1]
        if {$pid == 9} {
            source "recorder.tcl"
        }
	}
	return $ok
}