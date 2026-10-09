set filename "./output/tips.out" 
set file [open $filename a+ ]
puts $file   " [getTime]  [nodeDisp 13184 3]  [nodeUnbalance 13184 3]  [lindex [eleResponse	5519	force] 2]"
close $file
