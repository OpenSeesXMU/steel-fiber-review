# Portable review copy. Numerical algorithms are unchanged. See docs/PORTABILITY_CHANGES.md.
from pathlib import Path
REVIEW_ROOT = Path(__file__).resolve().parents[2]
import numpy as np
import matplotlib.pyplot as plt

def generate_straight_uhpc_curve(add_noise=True):
    # =========================================================
    # 1. 物理特征参数 (120MPa UHPC, 平直型微细纤维)
    # =========================================================
    d_f = 0.2          # 纤维直径 (mm)
    L_e = 6.5          # 有效埋置深度 (mm)
    f_c = 120.0        # 基体抗压强度 (MPa)
    f_u = 2800.0       # 极限抗拉强度 (MPa)
    
    # 根据 120MPa UHPC 估算最大等效界面剪切强度 tau_max (约 20~22 MPa)
    tau_max = 21.0     
    
    # 力学极限博弈：界面总摩擦力 vs 纤维自身拉断力
    A_f = np.pi * (d_f / 2)**2
    P_bond = np.pi * d_f * L_e * tau_max  # 摩擦极限 ≈ 85.7 N
    P_rupture = A_f * f_u                 # 拉断极限 ≈ 87.9 N
    
    # 判定实际峰值 (由于 P_bond < P_rupture, 纤维将发生延性拔出)
    P_max = min(P_bond, P_rupture)
    
    s1 = 0.12     # 极早的弹性段滑移量 (致密基体的典型特征)
    gamma = 0.75  # 摩擦软化指数 (平直纤维典型衰减规律)
    
    # 初始化滑移序列
    slip = np.linspace(0, 7.0, 1000)  
    force = np.zeros_like(slip)
    
    np.random.seed(42) # 保证单发测试结果的可复现性
    
    # =========================================================
    # 2. 物理形态与摩擦衰减重构
    # =========================================================
    for i, s in enumerate(slip):
        if s <= s1:
            # 上升段：极其陡峭的脱粘过程
            base_force = P_max * (2 * (s / s1) - (s / s1)**2)
            noise = np.random.normal(0, 0.4) if add_noise else 0
            force[i] = base_force + noise
            
        elif s < L_e:
            # 下降段：平直纤维特有的纯摩擦平滑/指数衰减 (无二次峰)
            base_force = P_max * ((L_e - s) / (L_e - s1)) ** gamma
            
            # 根据当前应力水平动态分配刮削噪音 (反映 UHPC 孔壁的高频刮削)
            noise_amplitude = 0.6 * (base_force / P_max) + 0.15
            noise = np.random.normal(0, noise_amplitude) if add_noise else 0
            force[i] = base_force + noise
            
        else:
            # 完全拔出后的微环境底噪
            noise = np.random.normal(0, 0.05) if add_noise else 0
            force[i] = noise
            
    # 数据清洗：消除异常负值并硬对齐原点
    force = np.clip(force, 0, None)
    force[0] = 0.0
            
    return slip, force, P_max

# =========================================================
# 3. 运行并进行可视化与数据导出
# =========================================================
if __name__ == "__main__":
    pred_slip, pred_force, peak_load = generate_straight_uhpc_curve(add_noise=True)
    print(f"Prediction Complete: Peak Load = {peak_load:.2f} N")

    # 绘制高保真本构曲线
    plt.figure(figsize=(9, 6), dpi=150)
    plt.plot(pred_slip, pred_force, color='#004488', linewidth=2.0, alpha=0.9,
             label=f'Straight Fiber ($d_f$=0.2, $L_e$=6.5)\nUHPC ($f_c$=120 MPa, $P_{{max}}$={peak_load:.1f}N)')
    
    # 标注拔出界限
    plt.axvline(x=6.5, color='gray', linestyle=':', alpha=0.6)
    plt.text(6.6, 15, 'Full Extraction ($L_e$=6.5 mm)', color='gray', fontsize=10, rotation=90)
    
    plt.title('High-Fidelity Prediction: Straight Fiber Pull-out in UHPC', fontsize=14, pad=15)
    plt.xlabel('Slip (mm)', fontsize=12)
    plt.ylabel('Pull-out Load (N)', fontsize=12)
    plt.xlim(0, 7.5)
    plt.ylim(0, 100)
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.legend(loc='upper right', fontsize=10, framealpha=0.9, edgecolor='black')
    
    plt.tight_layout()
    plt.show()
    
    # 若需将此数据无缝送入 OpenSees, 您可以直接在这里调用您的 simulate 文件接口
    # np.savetxt("Straight_UHPC_120MPa.csv", np.column_stack((pred_slip, pred_force)), delimiter=",", header="Slip,Force", comments="")