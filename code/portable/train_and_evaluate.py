# Portable review copy. Numerical algorithms are unchanged. See docs/PORTABILITY_CHANGES.md.
from pathlib import Path
REVIEW_ROOT = Path(__file__).resolve().parents[2]
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
import xgboost as xgb
import warnings
warnings.filterwarnings('ignore')

print("🚀 正在加载数据集并构建物理特征...")

# ==========================================
# 1. 加载数据与物理特征工程
# ==========================================
df = pd.read_csv(str(REVIEW_ROOT / "data" / "database" / "Final_AI_Dataset.csv"))
# 提取原始 6 个特征: Fiber_Type, d_f, f_u, L_e, f_c, theta
X_raw = df.iloc[:, 1:7].values
Y_raw = df.iloc[:, 7:].values

# 物理特征工程 (Physics-Informed)
d_f = X_raw[:, 1]
L_e = X_raw[:, 3]
f_c = X_raw[:, 5]

surface_area = np.pi * d_f * L_e
sqrt_fc = np.sqrt(f_c)
theo_bond = surface_area * sqrt_fc

# 拼接为最终的特征矩阵 X (9个特征)
X_features = np.column_stack((X_raw, surface_area, sqrt_fc, theo_bond))

# 提取物理锚点用于 XGBoost 训练
peak_forces = np.max(Y_raw, axis=1)
peak_indices = np.argmax(Y_raw, axis=1)
residual_forces = np.mean(Y_raw[:, -5:], axis=1)

# 数据归一化 (形状画师需要)
scaler_X = MinMaxScaler()
scaler_Y = MinMaxScaler()
X_scaled = scaler_X.fit_transform(X_features)
Y_scaled = scaler_Y.fit_transform(Y_raw)

# ==========================================
# 2. 🚨 核心修改：90% 训练集 vs 10% 测试集划分
# ==========================================
# random_state=42 保证每次划分的随机结果一致，方便复现
X_train, X_test, Y_train, Y_test, raw_Y_train, raw_Y_test, \
peak_f_train, peak_f_test, peak_idx_train, peak_idx_test, \
res_f_train, res_f_test = train_test_split(
    X_scaled, Y_scaled, Y_raw, 
    peak_forces, peak_indices, residual_forces, 
    test_size=0.10, random_state=42
)

print(f"📊 数据集划分完毕：训练集 {len(X_train)} 条，测试集 {len(X_test)} 条 (占比 10%)")

# ==========================================
# 3. 模型训练 (仅使用 90% 的训练集数据)
# ==========================================
print("🧠 正在训练形状画师 (Random Forest)...")
model_shape = RandomForestRegressor(n_estimators=300, random_state=42)
model_shape.fit(X_train, Y_train)

print("🎯 正在训练峰值狙击手 (XGBoost)...")
model_peak_force = xgb.XGBRegressor(n_estimators=300, learning_rate=0.05, random_state=42)
model_peak_force.fit(X_train, peak_f_train)

print("⚓ 正在训练残余锚定手 (XGBoost)...")
model_res_force = xgb.XGBRegressor(n_estimators=300, learning_rate=0.05, random_state=42)
model_res_force.fit(X_train, res_f_train)

# ==========================================
# 4. 模型测试与盲测评估 (对 10% 的测试集进行预测)
# ==========================================
print("\n🔍 正在对 10% 盲测集进行评估...")

# A. 预测基础形状
Y_test_pred_scaled = model_shape.predict(X_test)
Y_test_pred_base = scaler_Y.inverse_transform(Y_test_pred_scaled)

# B. 预测物理锚点
pred_peak_forces = model_peak_force.predict(X_test)
pred_res_forces = model_res_force.predict(X_test)

# C. 执行物理锚点缩放补偿 (针对测试集)
Y_test_final = np.zeros_like(Y_test_pred_base)
for i in range(len(X_test)):
    base_curve = Y_test_pred_base[i]
    target_peak = pred_peak_forces[i]
    target_res = pred_res_forces[i]
    
    base_peak_idx = np.argmax(base_curve)
    base_peak_val = base_curve[base_peak_idx]
    
    if base_peak_val <= 0:
        base_peak_val = 1e-5 
        
    scale_factor = target_peak / base_peak_val
    adjusted_curve = base_curve * scale_factor
    
    # 尾部残余平滑过渡补偿
    res_idx = int(len(adjusted_curve) * 0.8)
    current_res = np.mean(adjusted_curve[res_idx:])
    res_shift = target_res - current_res
    
    transition = np.linspace(0, 1, len(adjusted_curve) - res_idx)
    adjusted_curve[res_idx:] += res_shift * transition
    
    Y_test_final[i] = np.clip(adjusted_curve, a_min=0, a_max=None)

# ==========================================
# 5. 误差量化与出图展示
# ==========================================
# 计算测试集整体峰值误差
mae_peak = np.mean(np.abs(pred_peak_forces - peak_f_test))
mape_peak = np.mean(np.abs((pred_peak_forces - peak_f_test) / peak_f_test)) * 100

print("========================================")
print(f"📈 测试集峰值平均绝对误差 (MAE): {mae_peak:.2f} N")
print(f"📈 测试集峰值平均相对误差 (MAPE): {mape_peak:.2f} %")
print("========================================\n")

# 随机抽取一条测试集数据作图
sample_idx = np.random.randint(0, len(X_test))

true_curve = raw_Y_test[sample_idx]
pred_curve = Y_test_final[sample_idx]
slip_axis = np.linspace(0, 25.0, 100)

plt.figure(figsize=(10, 6))
plt.plot(slip_axis, true_curve, 'b-', linewidth=2.5, label='True Exp. Curve (Blind Test)')
plt.plot(slip_axis, pred_curve, 'r--', linewidth=2.5, label='AI Predicted Curve')

plt.scatter(slip_axis[np.argmax(true_curve)], np.max(true_curve), color='blue', s=100, zorder=5)
plt.scatter(slip_axis[np.argmax(pred_curve)], np.max(pred_curve), color='red', marker='*', s=200, zorder=5)

plt.title('AI Blind Test Performance (10% Unseen Data)', fontsize=16, fontweight='bold')
plt.xlabel('Slip (mm)', fontsize=14)
plt.ylabel('Pull-out Force (N)', fontsize=14)
plt.legend(fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('Test_Set_Evaluation.png', dpi=300)
print(">>> 盲测评估图像已保存为 'Test_Set_Evaluation.png'，请查看盲测拟合精度！")