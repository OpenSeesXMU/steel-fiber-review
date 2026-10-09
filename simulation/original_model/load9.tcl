timeSeries Path 2 -fileTime time.txt -filePath Path.txt -factor [expr 2125/100*1.0e15]
# timeSeries Linear 2 -factor [expr 2125/100*1.0e15]
pattern Plain 2 2 {
	load 13184 0.0 0.0 1.0 0.0 0.0 0.0
}

timeSeries Constant 3
pattern Plain 3 3 {
	sp 1672 1 [nodeDisp 1672 1]
	sp 1672 2 [nodeDisp 1672 2]
	sp 1672 3 [nodeDisp 1672 3]
}
