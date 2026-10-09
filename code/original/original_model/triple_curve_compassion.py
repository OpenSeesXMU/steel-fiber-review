import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

# =========================================================
# 1. 鲁棒性数据读取
# =========================================================
def load_csv_data(filename):
    if not os.path.exists(filename):
        return [], []
    try:
        try:
            df = pd.read_csv(filename, header=0)
            if not np.issubdtype(df.iloc[:, 0].dtype, np.number):
                raise ValueError
        except:
            df = pd.read_csv(filename, header=None)
        df = df.sort_values(by=df.columns[0])
        slip = df.iloc[:, 0].values
        force = np.clip(df.iloc[:, 1].values, 0, None)
        return slip, force
    except Exception:
        return [], []

wille_slip, wille_force = load_csv_data("wille2012_A_S.csv")
yoo_slip, yoo_force = load_csv_data("yoo2017_S13_A_2.csv")

# =========================================================
# 2. 纯下凹物理模型生成
# =========================================================
d_f, L_e, tau_max = 0.2, 6.5, 7.8     
P_max = np.pi * d_f * L_e * tau_max  # 峰值约 31.8 N
s1 = 0.25      

# 【绝对核心：满足您“微圆+下凹”的极致参数】
alpha = 1.15  # 仅保留极微弱的顶点圆润，瞬间转身向下，彻底根除“外凸大肚子”！
beta = 2.5    # 强力下凹指数，打造纯正的碗状（向下凹）衰减滑梯！

pred_slip = np.linspace(0, 7.5, 1000)  
pred_force = np.zeros_like(pred_slip)

for i, s in enumerate(pred_slip):
    if s <= s1:
        # 上升段：纯净抛物线
        pred_force[i] = P_max * (2 * (s / s1) - (s / s1)**2)
    elif s < L_e:
        # 下降段：微圆润起手，紧接着纯向下凹！
        x = (s - s1) / (L_e - s1)
        pred_force[i] = P_max * (1 - x**alpha)**beta
    else:
        # 拔出归零
        pred_force[i] = 0.0

# =========================================================
# 3. 高清学术出图
# =========================================================
plt.figure(figsize=(9, 6), dpi=300)

if len(yoo_slip) > 0:
    plt.plot(yoo_slip, yoo_force, linestyle='-', marker='s', markersize=3, 
             color='#ff7f0e', alpha=0.5, linewidth=1.5, label='Exp: Yoo 2017 (S13-A-2)')

if len(wille_slip) > 0:
    plt.plot(wille_slip, wille_force, linestyle='-', marker='o', markersize=3, 
             color='#2ca02c', alpha=0.5, linewidth=1.5, label='Exp: Wille 2012 (A-S)')

# 绘制终极版预测曲线
plt.plot(pred_slip, pred_force, color='#004488', linewidth=3.5, zorder=10, 
         label=r'Predicted Model (Slightly Rounded & Concave Up)')

plt.axvline(x=6.5, color='gray', linestyle=':', alpha=0.8)
plt.text(6.6, 5, 'Full Extraction ($L_e$=6.5 mm)', color='gray', fontsize=11, rotation=90)

plt.title('Final Calibrated Baseline: Concave Descending Model', fontsize=15, pad=15, fontweight='bold')
plt.xlabel('Slip (mm)', fontsize=13)
plt.ylabel('Pull-out Load (N)', fontsize=13)
plt.xlim(0, 7.5)
plt.ylim(0, 50) 
plt.grid(True, linestyle='--', alpha=0.4)
plt.legend(loc='upper right', fontsize=11, framealpha=0.95, edgecolor='black', borderpad=0.8)

plt.tight_layout()
plt.savefig("Pullout_Comparison_Concave.png", bbox_inches='tight')
plt.show()