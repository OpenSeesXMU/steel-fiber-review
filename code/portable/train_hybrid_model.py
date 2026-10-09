# Portable review copy. Numerical algorithms are unchanged. See docs/PORTABILITY_CHANGES.md.
from pathlib import Path
REVIEW_ROOT = Path(__file__).resolve().parents[2]
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from catboost import CatBoostRegressor
import xgboost as xgb

# ==========================================
# 1. 加载数据与提取“物理锚点”
# ==========================================
print("📦 正在加载数据...")
df = pd.read_csv(str(REVIEW_ROOT / "data" / "database" / "Final_AI_Dataset.csv"))

X_raw = df[['fiber type', 'df', 'fu', 'Le', 'fc', 'theta']].values
Y_raw = df.loc[:, 'Force_0':'Force_99'].values

# 【核心】：从真实曲线中单独提取两个最关键的物理特征点
Y_peaks = np.max(Y_raw, axis=1) # 真实的峰值力
Y_residuals = Y_raw[:, -1]      # 真实的尾部残余力 (第100个点)

X_train, X_test, Y_train, Y_test, Y_peak_train, Y_peak_test, Y_res_train, Y_res_test = train_test_split(
    X_raw, Y_raw, Y_peaks, Y_residuals, test_size=0.2, random_state=42
)

# ==========================================
# 🚀 2. 训练三大专属模型 (解耦策略)
# ==========================================
print("🔥 正在训练特征点专属模型...")

# 专家 A: 形状画师 (Random Forest 负责画出顺滑的大致轮廓)
model_shape = RandomForestRegressor(n_estimators=300, random_state=42)
model_shape.fit(X_train, Y_train)

# 专家 B: 峰值狙击手 (换成顶刊推荐的 CatBoost！)
# verbose=0 是为了让它在后台安静训练，不疯狂刷屏
model_peak = CatBoostRegressor(iterations=500, learning_rate=0.03, depth=6, random_seed=42, verbose=0)
model_peak.fit(X_train, Y_peak_train)

# 专家 C: 尾部锚点手 (XGBoost 只负责死磕 1 个数字：残余力)
model_res = xgb.XGBRegressor(n_estimators=300, learning_rate=0.05, max_depth=5, random_state=42)
model_res.fit(X_train, Y_res_train)

# ==========================================
# 🎯 3. 预测与物理补偿校准
# ==========================================
test_idx = 0
sample_x = X_test[test_idx].reshape(1, -1)
real_y = Y_test[test_idx]
real_x = sample_x[0]

# 1. 拿到三种预测结果
base_curve = model_shape.predict(sample_x)[0]
pred_peak_force = model_peak.predict(sample_x)[0]
pred_res_force = model_res.predict(sample_x)[0]

# 2. 物理误差补偿算法 (见证奇迹的时刻！)
calibrated_curve = np.zeros(100)
peak_idx = np.argmax(base_curve) # 找到基础曲线的峰值所在位置

# 计算目标需要拔高/压低的误差
error_peak = pred_peak_force - base_curve[peak_idx]
error_res = pred_res_force - base_curve[-1]

# 将误差像“拉弓”一样，按比例线性补偿到整条曲线上，强行让曲线穿过真实的锚点
for i in range(100):
    if i <= peak_idx:
        # 上升段：从 0 开始拉升，直到达到峰值目标
        ratio = i / peak_idx if peak_idx > 0 else 1.0
        calibrated_curve[i] = base_curve[i] + error_peak * ratio
    else:
        # 下降段：从峰值目标平滑过渡到尾部残余力目标
        ratio = (i - peak_idx) / (99 - peak_idx)
        calibrated_curve[i] = base_curve[i] + error_peak + (error_res - error_peak) * ratio

# ==========================================
# 📊 4. 画图对比
# ==========================================
target_slip = np.linspace(0, 25.0, 100)

plt.figure(figsize=(10, 6))
plt.plot(target_slip, real_y, 'b-', linewidth=3, label='Real Experiment Curve', alpha=0.8)
# 画出未经校准的灰线，让你对比看看
plt.plot(target_slip, base_curve, color='gray', linestyle=':', linewidth=2, label='AI Base Shape (Uncalibrated)')
# 画出最终的红线
plt.plot(target_slip, calibrated_curve, 'r-', linewidth=2.5, label='Hybrid Physics-Calibrated Curve')

type_str = 'Hooked' if int(real_x[0]) == 1 else 'Straight'
plt.title(f"Hybrid Physics-AI Prediction vs Real Experiment\n"
          f"(Type:{type_str}, df:{real_x[1]:.1f}mm, fu:{real_x[2]:.0f}MPa, "
          f"Le:{real_x[3]:.1f}mm, fc:{real_x[4]:.1f}MPa, Angle:{real_x[5]:.0f}°)", 
          fontsize=12, fontweight='bold')
plt.xlabel('Slip (mm)', fontsize=12)
plt.ylabel('Pull-out Force (N)', fontsize=12)
plt.legend(fontsize=11)
plt.grid(True, linestyle='--', alpha=0.6)

# 标出最终校准后的峰值
plt.plot(target_slip[peak_idx], calibrated_curve[peak_idx], 'ro', markersize=8)
plt.text(target_slip[peak_idx]+0.5, calibrated_curve[peak_idx]+10, f'Precise Peak: {calibrated_curve[peak_idx]:.1f}N', color='red', fontweight='bold')

plt.savefig('Hybrid_Prediction.png', dpi=300)
print("📊 混合模型预测结果已保存为 'Hybrid_Prediction.png'！")
plt.show()