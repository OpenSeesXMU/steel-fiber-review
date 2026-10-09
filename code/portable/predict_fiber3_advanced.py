# Portable review copy. Numerical algorithms are unchanged. See docs/PORTABILITY_CHANGES.md.
from pathlib import Path
REVIEW_ROOT = Path(__file__).resolve().parents[2]
import numpy as np
import matplotlib.pyplot as plt

def get_concave_fiber3_4_5mm(add_noise=True):
    # 1. 物理参数设置 (修改埋深为 4.5 mm)
    d_f = 0.15          # 纤维直径 (mm)
    L_e = 4.5           # 埋置深度 (mm) <- 修改为 4.5 mm
    tau_max = 11.0      # 界面粘结强度 (MPa)
    f_u = 2500.0        # 抗拉极限强度 (MPa)
    
    # 2. 力学极限计算
    A_f = np.pi * (d_f / 2)**2
    P_bond = np.pi * d_f * L_e * tau_max  # 理论名义粘结力 (约 23.3 N)
    P_rupture = A_f * f_u                 # 截面抗拉断极限 (约 44.2 N)
    
    # 实际峰值力 (取较小值)
    P_max = min(P_bond, P_rupture)
    
    # 3. 本构形状参数
    s1 = 0.25     # 弹性段滑移量
    beta = 0.65   # 泊松衰减系数，主导内凹特征
    
    # X轴生成至 5.5 mm，完整展示 4.5 mm 归零点
    slip = np.linspace(0, 5.5, 1000)  
    force = np.zeros_like(slip)
    
    for i, s in enumerate(slip):
        if s <= s1:
            # 弹性爬坡段
            base_force = P_max * (2 * (s / s1) - (s / s1)**2)
            noise = np.random.normal(0, 0.15) if add_noise else 0
            force[i] = base_force + noise
            
        elif s < L_e:
            # 真实下降段：线性面积递减 × 泊松指数衰减 = 完美内凹
            area_ratio = (L_e - s) / (L_e - s1)
            poisson_decay = np.exp(-beta * (s - s1))
            
            base_force = P_max * area_ratio * poisson_decay
            
            # 分配微小滑动摩擦噪音
            noise = np.random.normal(0, 0.3 * (base_force / P_max)) if add_noise else 0
            force[i] = base_force + noise
        else:
            # 彻底拔出，物理截断
            force[i] = 0.0
            
    force = np.clip(force, 0, None)
    force[0] = 0.0
            
    return slip, force, P_max

# ================= 运行与绘图 =================
pred_slip, pred_force, peak_load = get_concave_fiber3_4_5mm(add_noise=True)

plt.figure(figsize=(9.5, 6), dpi=150)

# 绘制带有指数内凹形态的 Fiber 3 (4.5mm)
plt.plot(pred_slip, pred_force, color='#004488', linewidth=3.0, zorder=10, 
         label=r'Predicted: Fiber 3 (Concave Decay, $L_e$=4.5 mm)')

# 标注理论峰值点
peak_idx = np.argmax(pred_force)
plt.scatter(pred_slip[peak_idx], pred_force[peak_idx], color='red', s=50, zorder=15)
plt.text(pred_slip[peak_idx] + 0.15, pred_force[peak_idx] * 0.95, 
         f'Peak Load: {peak_load:.1f} N', fontsize=11, color='red')

# 标注 4.5 mm 物理截断边界
plt.axvline(x=4.5, color='gray', linestyle=':', alpha=0.7)
plt.text(4.55, 5, 'Complete Extraction (4.5 mm)', color='gray', fontsize=10, rotation=90)

# 图表排版设计
plt.title('Validation with Physically Accurate Concave Decay ($L_e = 4.5$ mm)', fontsize=14, pad=15)
plt.xlabel('Slip (mm)', fontsize=12)
plt.ylabel('Pull-out Load (N)', fontsize=12)

# 自适应视野：X轴到 5.5mm，Y轴到 30N
plt.xlim(0, 5.5)
plt.ylim(0, 30)

plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(loc='upper right', fontsize=11, framealpha=0.9, edgecolor='black')

plt.tight_layout()
plt.show()