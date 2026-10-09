import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

def generate_physical_hooked_curve():
    """
    基于端钩钢纤维真实力学机制，生成分段平滑测试曲线
    """
    slip = np.linspace(0, 20, 200)
    force = np.zeros_like(slip)

    # 设定的物理真实特征锚点
    s1, f1 = 0.5, 230.0  # 点1：弹性脱粘点
    s2, f2 = 3.5, 480.0  # 点2：极限峰值点
    s3, f3 = 7.0, 160.0  # 点3：软化拐点
    s4, f4 = 20.0, 60.0  # 点4：残余摩擦点

    for i, s in enumerate(slip):
        if s <= s1:
            # 第一阶段：纯弹性脱粘（绝对直线）
            force[i] = (f1 / s1) * s
        elif s <= s2:
            # 第二阶段：端钩拉直硬化（平滑的向上凸曲线，使用正弦四分之一波模拟）
            normalized_s = (s - s1) / (s2 - s1)
            force[i] = f1 + (f2 - f1) * np.sin(normalized_s * np.pi / 2)
        elif s <= s3:
            # 第三阶段：陡峭下降段（使用余弦平滑过渡）
            normalized_s = (s - s2) / (s3 - s2)
            force[i] = f3 + (f2 - f3) * (0.5 + 0.5 * np.cos(normalized_s * np.pi))
        else:
            # 第四阶段：残余摩擦段（指数衰减）
            force[i] = f4 + (f3 - f4) * np.exp(-0.3 * (s - s3))
            
    return slip, force

def extract_four_features_robust(slip_array, force_array):
    """
    针对真实力学曲线的鲁棒特征提取算法
    """
    n_points = len(force_array)
    
    # --- 点2：峰值点 ---
    idx_p2 = np.argmax(force_array)
    
    # --- 点1：起拔点 (寻找直线段结束，非线性刚度开始下降的拐点) ---
    asc_slip = slip_array[:idx_p2]
    asc_force = force_array[:idx_p2]
    
    if len(asc_force) > 5:
        # 计算刚度（一阶导数）
        stiffness = np.gradient(asc_force, asc_slip)
        # 当刚度跌落至初始线性刚度的 80% 时，认为是脱粘点
        initial_stiffness = np.mean(stiffness[1:4])
        drop_indices = np.where(stiffness < initial_stiffness * 0.8)[0]
        idx_p1 = drop_indices[0] if len(drop_indices) > 0 else max(1, idx_p2 // 4)
    else:
        idx_p1 = max(0, idx_p2 - 1)

    # --- 点4：残余点 ---
    idx_p4 = n_points - 1

    # --- 点3：软化拐点 ---
    if idx_p4 - idx_p2 > 10:
        desc_slip = slip_array[idx_p2:idx_p4]
        desc_force = force_array[idx_p2:idx_p4]
        
        # 寻找下降段二阶导数极值点
        d1_desc = np.gradient(desc_force, desc_slip)
        d2_desc = np.gradient(d1_desc, desc_slip)
        idx_p3_relative = np.argmax(d2_desc)
        idx_p3 = idx_p2 + idx_p3_relative
        
        # 安全校验
        if idx_p3 <= idx_p2 + 5 or idx_p3 >= idx_p4 - 5:
            idx_p3 = idx_p2 + (idx_p4 - idx_p2) // 3
    else:
        idx_p3 = idx_p2 + (idx_p4 - idx_p2) // 2

    return [idx_p1, idx_p2, idx_p3, idx_p4]

# ==========================================
# 运行主程序
# ==========================================
slip_sim, force_sim = generate_physical_hooked_curve()
indices = extract_four_features_robust(slip_sim, force_sim)

feature_slips = slip_sim[indices]
feature_forces = force_sim[indices]

# 生成图表
plt.figure(figsize=(10, 6))
# 绘制背景的真实平滑曲线
plt.plot(slip_sim, force_sim, 'b-', linewidth=2.5, alpha=0.6, label="Continuous Physical Curve")
# 绘制 OpenSees 的 Pinching4 四折线骨架
plt.plot(feature_slips, feature_forces, 'r--', linewidth=2, label="OpenSees Pinching4 Backbone (4-Points)")
# 绘制特征点
plt.plot(feature_slips, feature_forces, 'ro', markersize=9)

labels = ['1: Debonding', '2: Peak', '3: Softening Turn', '4: Residual']
for i, txt in enumerate(labels):
    plt.annotate(txt, (feature_slips[i], feature_forces[i]), textcoords="offset points", xytext=(0,12), ha='center', fontweight='bold', color='red')

plt.title("Physics-Based Hooked-End Fiber Feature Extraction", fontsize=14)
plt.xlabel("Slip (mm)", fontsize=12)
plt.ylabel("Pull-out Force (N)", fontsize=12)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()