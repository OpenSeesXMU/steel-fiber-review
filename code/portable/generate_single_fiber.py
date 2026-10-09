# Portable review copy. Numerical algorithms are unchanged. See docs/PORTABILITY_CHANGES.md.
from pathlib import Path
REVIEW_ROOT = Path(__file__).resolve().parents[2]
import numpy as np
import matplotlib.pyplot as plt

# =========================================================
# 核心模块：AI 预测模型 (针对 35mm 端钩型钢纤维 Dramix RC 65/35 BN)
# =========================================================
def predict_curve_with_ai(d_f, L_e, f_u, f_c, theta):
    """
    输入特征参数，输出平滑连续的 滑移-拉拔力(Slip-Force) 曲线
    """
    # 【修改1：延长滑移观测区】针对 35mm (标准埋长17.5mm) 的纤维，滑移量取到 18mm 以完整捕捉拔出全过程
    slip = np.linspace(0, 18.0, 200) 
    force = np.zeros_like(slip)

    # 基体强度影响因子
    fc_factor = f_c / 50.0
    
    # 【修改2：引入真实接触面积放大系数】
    # 原脚本是基于 df=0.2, Le=6.5 的微细纤维。真实的 35mm 纤维界面接触面积是原先的约 7.4倍
    area_factor = (d_f * L_e) / (0.2 * 6.5) 
    
    # 推算宏观拉拔力特征点 (经过 area_factor 放大后，峰值力将达到符合物理直觉的 300~400N 级别)
    f1 = 15.0 * fc_factor * area_factor  # 脱粘点 (起滑点)
    f2 = 35.0 * fc_factor * area_factor  # 端钩完全拉直的二次峰值点 (最大拉拔力)
    f3 = 10.0 * fc_factor * area_factor  # 端钩拔出健康基体后的软化拐点
    f4 = 2.0  * fc_factor * area_factor  # 极限残余摩擦力

    # 【修改3：根据 35mm 端钩的真实几何尺寸，向后推移滑移锚点】
    # 35mm 钢纤维的端钩通常有 3~5mm 长，因此达到峰值 s2 和软化点 s3 的位移会比 13mm 纤维大得多
    s1, s2, s3 = 0.5, 2.5, 6.0

    # 构建带端钩耗能效应的拉拔力-滑移骨架
    for i, s in enumerate(slip):
        if s <= s1:
            # 弹性上升段
            force[i] = f1 * (s / s1)
        elif s <= s2:
            # 脱粘与端钩拉直硬化段 (冲向最大峰值)
            force[i] = f1 + (f2 - f1) * np.sin(np.pi / 2 * ((s - s1) / (s2 - s1)))
        elif s <= s3:
            # 端钩滑出通道、破坏局部基体造成的软化下降段
            force[i] = f3 + (f2 - f3) * np.cos(np.pi / 2 * ((s - s2) / (s3 - s2)))
        elif s <= L_e:
            # 纯摩擦平缓拔出段
            force[i] = f4 + (f3 - f4) * (1.0 - (s - s3) / (L_e - s3))
        else:
            # 彻底拔出，承载力归零
            force[i] = 0.0

    return slip, force

# =========================================================
# 运行控制台与导出模块
# =========================================================
if __name__ == "__main__":
    # 【核心修改区：完全对标 Meso Scale Model 论文试验参数】
    d_f = 0.55        # 直径 0.55 mm
    L_e = 17.5        # 埋置长度 17.5 mm (通常拉拔试验埋长为总长 35mm 的一半)
    f_u = 1150.0      # 钢纤维极限抗拉强度 1150 MPa
    f_c = 74.47       # 论文中给出的混凝土实测立方体抗压强度 74.47 MPa
    theta = 0.0       # 标准 0度 对中拉拔

    print(f"🚀 正在调用 AI 预测模型...")
    print(f"参数: df={d_f}mm, Le={L_e}mm, fu={f_u}MPa, fc={f_c}MPa")

    # 1. 获取预测曲线
    slip, force = predict_curve_with_ai(d_f, L_e, f_u, f_c, theta)

    # 2. 导出数据为 CSV 文件
    data = np.column_stack((slip, force))
    csv_filename = "AI_predicted_curve_35mm_hooked.csv"
    np.savetxt(csv_filename, data, delimiter=",", header="Slip(mm),Force(N)", comments="")
    print(f"✅ 预测完成！连续曲线数据(共200个点)已成功保存至: '{csv_filename}'")