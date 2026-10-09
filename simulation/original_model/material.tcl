# 1箍筋
uniaxialMaterial  Steel02      1     498e3      3.26e8  	    0.001   14.0     0.925    0.15 
# 2柱纵筋
uniaxialMaterial  Steel02      2     421e3      1.97e8  	    0.01    14.0     0.925    0.15 
# 3梁纵筋
uniaxialMaterial  Steel02      3     430e3      1.97e8  	    0.001    14.0     0.925    0.15
# uniaxialMaterial  Steel01      3     430e3      1.97e8  	    0

# 混凝土
#uniaxialMaterial  Concrete02   4    -1.6e6    -1.6e-3    -1.0e6    -5.0e-2    0.3    2.0e5     8.0e5 
#uniaxialMaterial  Concrete02   5    -1.6e8    -1.6e-1    -1.0e8    -5.0e-2    0.3    2.5e5     8.0e5 

#uniaxialMaterial  Hysteretic 4 1.2e5 0.5e-4 0.1 0.02 1.0 3.0 -2.0e6 -1.5e-3 -1.5e6 -4.0e-2 -1.51e6  -5.0  1.0  1.0  0.0  0.0  0.5
#uniaxialMaterial  Hysteretic 5 1.2e5 0.5e-4 0.1 0.02 1.0 3.0 -4.0e6 -3.0e-3 -3.0e6 -4.0e-2 -1.51e6  -5.0  1.0  1.0  0.0  0.0  0.5
#uniaxialMaterial  Elastic   5     2.1333e+09

uniaxialMaterial  Hysteretic 4 1.2e5 0.6e-4 0.1 0.1 1.0 3.0 -2.0e6 -1.5e-3 -1.0e6 -5.0e-2 -1.01e6  -5.0  1.0  1.0  0.0  0.0  0.5
uniaxialMaterial  Hysteretic 5 1.2e5 0.6e-4 0.1 0.1 1.0 3.0 -2.5e6 -2.5e-3 -2.0e6 -5.0e-2 -2.01e6  -5.0  1.0  1.0  0.0  0.0  0.5
uniaxialMaterial  Hysteretic 6 1.2e5 0.6e-4 0.1 0.1 1.0 3.0 -2.5e6 -2.5e-3 -2.0e6 -5.0e-2 -2.01e6  -5.0  1.0  1.0  0.0  0.0  0.5
# 钢纤维材料 
uniaxialMaterial  Steel02      100     400e3      2.0e8       0.01    14.0     0.925    0.15

# 刚性连接
uniaxialMaterial  Elastic   10   1.0e15

# ----------------------------------------------------------------- #
set A1 126.6769
set A2 817.3698
set A3 506.7075
set I1 6.8106e+03
set I2 2.8355e+05
set I8 1.0897e-04
set I3 1.0897e+03

# 1箍筋
uniaxialMaterial  Steel02      11     [expr 498e3*$A1]      [expr 3.26e8*$A1]  	    0.01    14.0     0.925    0.15 
# 2柱纵筋
uniaxialMaterial  Steel02      12     [expr 421e3*$A2]      [expr 1.97e8*$A2]  	    0.01    14.0     0.925    0.15 
# 3梁纵筋
uniaxialMaterial  Steel02      13     [expr 430e3*$A3]      [expr 1.97e8*$A3]  	    0.01    14.0     0.925    0.15 

# 1箍筋
uniaxialMaterial  Steel02      14     [expr 498e3*$I1]      [expr 3.26e8*$I1]  	    0.01    14.0     0.925    0.15 
# 2柱纵筋
uniaxialMaterial  Steel02      15     [expr 421e3*$I2]      [expr 1.97e8*$I2]  	    0.01    14.0     0.925    0.15 
# 3梁纵筋
uniaxialMaterial  Steel02      16     [expr 430e3*$I8]      [expr 1.97e8*$I8]  	    0.01    14.0     0.925    0.15 
# 3梁纵筋弯起
uniaxialMaterial  Steel02      17     [expr 430e3*$I3]      [expr 1.97e8*$I3]  	    0.01    14.0     0.925    0.15

section Aggregator 1 11 P 14 My 14 Mz 10 T
section Aggregator 2 12 P 15 My 15 Mz 10 T
section Aggregator 8 13 P 16 My 16 Mz 10 T
section Aggregator 3 13 P 17 My 17 Mz 10 T
geomTransf  Linear  1  1.0  1.0  1.0
