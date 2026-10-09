import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb

# ==========================================
# 1. 加载数据
# ==========================================
print("📦 正在加载数据...")
df = pd.read_csv('Final_AI_Dataset.csv')

X_raw = df[['fiber type', 'df', 'fu', 'Le', 'fc', 'theta']].values
Y_raw = df.loc[:, 'Force_0':'Force_99'].values

# ==========================================
# 🧠 2. 物理先验特征工程
# ==========================================
type_f, df_val, fu_val, Le_val, fc_val, theta_val = X_raw.T

aspect_ratio = Le_val / df_val                     
bond_area = np.pi * df_val * Le_val                
sqrt_fc = np.sqrt(fc_val)                          
theoretical_pullout = bond_area * sqrt_fc          
cos_theta = np.cos(theta_val * np.pi / 180.0)      

X_enhanced = np.column_stack((X_raw, aspect_ratio, bond_area, sqrt_fc, theoretical_pullout, cos_theta))

# ==========================================
# 🎯 3. 提取 2 大绝对物理锚点 (取消位置预测)
# ==========================================
Y_peak_forces = np.max(Y_raw, axis=1)              # 锚点1：峰值力 (Y轴)
Y_residuals = Y_raw[:, -1]                         # 锚点2：残余力 (Y轴)

X_tr, X_te, Y_tr, Y_te, Pf_tr, Pf_te, Rf_tr, Rf_te = train_test_split(
    X_enhanced, Y_raw, Y_peak_forces, Y_residuals, test_size=0.2, random_state=42
)

# ==========================================
# 🔥 4. 训练专属模型网络
# ==========================================
print("🔥 正在训练带物理特征的锚点模型...")
# 专家 A：随机森林画出包含微小波动的总体流线形状 (它决定了 X 轴的峰值在哪！)
model_shape = RandomForestRegressor(n_estimators=300, random_state=42).fit(X_tr, Y_tr)

# 专家 B、C：XGBoost 专心死磕 Y 轴的大小
model_pf = xgb.XGBRegressor(n_estimators=300, learning_rate=0.05, max_depth=4).fit(X_tr, Pf_tr)
model_rf = xgb.XGBRegressor(n_estimators=300, learning_rate=0.05, max_depth=4).fit(X_tr, Rf_tr)

# ==========================================
# 🛠️ 5. 预测与振幅比例校准 (不扭曲 X 轴)
# ==========================================
test_idx = 0
sample_x = X_te[test_idx].reshape(1, -1)
real_y = Y_te[test_idx]
raw_params = X_te[test_idx][:6] 

# AI 预测出基础形状和两个精确的 Y 轴锚点
base_curve = model_shape.predict(sample_x)[0]
pred_pf = model_pf.predict(sample_x)[0]
pred_rf = model_rf.predict(sample_x)[0]

# 【核心修正】：直接信任灰线的峰值位置！
pred_pi = np.argmax(base_curve) 

calibrated_curve = np.zeros(100)

# 计算峰值的放大倍数
scale_peak = pred_pf / base_curve[pred_pi] if base_curve[pred_pi] > 0 else 1.0

# 计算尾部的放大倍数
scale_res = pred_rf / base_curve[-1] if base_curve[-1] > 0 else 1.0

# 优雅地把整条灰线等比例拔高！
for i in range(100):
    if i <= pred_pi:
        # 上升段：纯等比例放大，完美保留原始刚度特征
        calibrated_curve[i] = base_curve[i] * scale_peak
    else:
        # 下降段：放大倍数从 scale_peak 缓缓过渡到 scale_res
        ratio = (i - pred_pi) / (99 - pred_pi)
        current_scale = scale_peak * (1 - ratio) + scale_res * ratio
        calibrated_curve[i] = base_curve[i] * current_scale

# ==========================================
# 📊 6. 可视化
# ==========================================
target_slip = np.linspace(0, 25.0, 100)

plt.figure(figsize=(10, 6))
plt.plot(target_slip, real_y, 'b-', linewidth=3, label='Real Experiment', alpha=0.8)
plt.plot(target_slip, base_curve, color='gray', linestyle=':', linewidth=2, label='AI Base Shape (Trust its X-axis)')
plt.plot(target_slip, calibrated_curve, 'r-', linewidth=2.5, label='Amplitude Scaled Curve')

type_str = 'Hooked' if int(raw_params[0]) == 1 else 'Straight'
plt.title(f"Amplitude Scaled Prediction (Physics + Shape Preserved)\n"
          f"(Type:{type_str}, df:{raw_params[1]:.1f}mm, fu:{raw_params[2]:.0f}MPa, "
          f"Le:{raw_params[3]:.1f}mm, fc:{raw_params[4]:.1f}MPa, Angle:{raw_params[5]:.0f}°)", 
          fontsize=12, fontweight='bold')
plt.xlabel('Slip (mm)', fontsize=12)
plt.ylabel('Pull-out Force (N)', fontsize=12)
plt.legend(fontsize=11)
plt.grid(True, linestyle='--', alpha=0.6)

plt.plot(target_slip[pred_pi], pred_pf, 'r*', markersize=12, label='Scaled Peak')
plt.plot(target_slip[-1], pred_rf, 'rs', markersize=8, label='Scaled Residual')
plt.text(target_slip[pred_pi]+0.5, pred_pf, f'Peak: {pred_pf:.1f}N', color='red', fontweight='bold')

plt.savefig('Amplitude_Scaled_Prediction.png', dpi=300)
print("📊 比例缩放版结果已生成！请查看 'Amplitude_Scaled_Prediction.png'")
plt.show()