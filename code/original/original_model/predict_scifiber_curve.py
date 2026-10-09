import numpy as np
import matplotlib.pyplot as plt

def predict_custom_uhpc_fiber():
    # 1. 输入您的物理参数
    d_f = 0.2           # 纤维直径 (mm)
    L_f = 13.0          # 纤维总长 (mm)
    L_e = L_f / 2       # 理论有效埋置深度 (6.5 mm)
    f_u = 2800.0        # 抗拉极限强度 (MPa)
    tau_max = 6.8       # 150MPa基体等效粘结强度 (MPa)
    
    # 2. 力学验算
    A_f = np.pi * (d_f / 2)**2
    P_bond = np.pi * d_f * L_e * tau_max  # 约 27.8 N
    P_rupture = A_f * f_u                 # 约 88.0 N
    
    # 实际峰值力
    P_max = min(P_bond, P_rupture)
    
    # 3. 物理本构演化 (内凹衰减)
    s1 = 0.25     # 弹性段滑移，确保起步清晰
    beta = 0.65   # 泊松收缩衰减系数，主导内凹特征
    
    # X轴延伸至 7.5 mm，完整展示归零点
    slip = np.linspace(0, 7.5, 1000)  
    force = np.zeros_like(slip)
    
    for i, s in enumerate(slip):
        if s <= s1:
            # 弹性爬坡
            force[i] = P_max * (2 * (s / s1) - (s / s1)**2)
        elif s < L_e:
            # 真实下降段：线性面积递减 × 泊松指数衰减 (内凹)
            area_ratio = (L_e - s) / (L_e - s1)
            poisson_decay = np.exp(-beta * (s - s1))
            force[i] = P_max * area_ratio * poisson_decay
        else:
            # 彻底拔出归零
            force[i] = 0.0
            
    return slip, force, P_max

# ================= 绘图生成 =================
slip_vals, force_vals, peak_load = predict_custom_uhpc_fiber()

plt.figure(figsize=(9, 6), dpi=150)
plt.plot(slip_vals, force_vals, color='#ff7f0e', linewidth=3.5, 
         label=r'Predicted: Custom Fiber ($L_e$=6.5mm, $f_c$=150MPa)')

# 标注峰值
peak_idx = np.argmax(force_vals)
plt.scatter(slip_vals[peak_idx], force_vals[peak_idx], color='red', s=50, zorder=5)
plt.text(slip_vals[peak_idx] + 0.2, force_vals[peak_idx] * 0.95, 
         f'Peak: {peak_load:.1f} N', fontsize=11, color='red')

# 标注物理截断
plt.axvline(x=6.5, color='gray', linestyle=':', alpha=0.7)
plt.text(6.6, 5, 'Complete Extraction (6.5 mm)', color='gray', fontsize=10, rotation=90)

# 图表排版
plt.title('UHPC Straight Steel Fiber Pull-out Prediction', fontsize=15, pad=15)
plt.xlabel('Slip (mm)', fontsize=13)
plt.ylabel('Pull-out Load (N)', fontsize=13)
plt.xlim(0, 8.0)
plt.ylim(0, 40)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(loc='upper right', fontsize=11)
plt.tight_layout()
plt.show()