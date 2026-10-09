# Portable review copy. Numerical algorithms are unchanged. See docs/PORTABILITY_CHANGES.md.
from pathlib import Path
REVIEW_ROOT = Path(__file__).resolve().parents[2]
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputRegressor
import xgboost as xgb

# ==========================================
# 1. 数据加载 (直接读取，无需归一化)
# ==========================================
print("📦 正在加载数据...")
df = pd.read_csv(str(REVIEW_ROOT / "data" / "database" / "Final_AI_Dataset.csv"))

X_raw = df[['fiber type', 'df', 'fu', 'Le', 'fc', 'theta']].values
Y_raw = df.loc[:, 'Force_0':'Force_99'].values

X_train, X_test, Y_train, Y_test = train_test_split(X_raw, Y_raw, test_size=0.2, random_state=42)

# ==========================================
# 🚀 2. 构建 XGBoost (极端梯度提升树)
# ==========================================
print("🔥 正在召唤 XGBoost 死磕特征点...")
# 核心调参：learning_rate 变小，让它学得更细腻；max_depth 变大，允许它刻画极其尖锐的特征
xgb_estimator = xgb.XGBRegressor(
    n_estimators=500,        # 500棵树接力
    learning_rate=0.05,      # 较小的学习率，精雕细琢
    max_depth=7,             # 更深的树，用来捕捉尖峰突变
    subsample=0.8,           # 防止过拟合
    colsample_bytree=0.8,
    random_state=42
)

# 使用 MultiOutputRegressor 包装，让它能同时预测 100 个点
xgb_model = MultiOutputRegressor(xgb_estimator)

# 暴力拟合 (大概需要 2~3 秒)
xgb_model.fit(X_train, Y_train)
print("✅ XGBoost 训练完成！")

# ==========================================
# 🎯 3. 预测与可视化
# ==========================================
test_idx = 0
sample_x = X_test[test_idx].reshape(1, -1)
real_y = Y_test[test_idx]
real_x = sample_x[0]

pred_y = xgb_model.predict(sample_x)[0]

# ==========================================
# 📊 4. 画图对比
# ==========================================
target_slip = np.linspace(0, 25.0, 100)

plt.figure(figsize=(10, 6))
plt.plot(target_slip, real_y, 'b-', linewidth=2.5, label='Real Experiment Curve')
# 换成绿色的线代表 XGBoost
plt.plot(target_slip, pred_y, 'g--', linewidth=2.5, label='XGBoost Predicted Curve')

type_str = 'Hooked' if int(real_x[0]) == 1 else 'Straight'
plt.title(f"XGBoost Prediction vs Real Experiment\n"
          f"(Type:{type_str}, df:{real_x[1]:.1f}mm, fu:{real_x[2]:.0f}MPa, "
          f"Le:{real_x[3]:.1f}mm, fc:{real_x[4]:.1f}MPa, Angle:{real_x[5]:.0f}°)", 
          fontsize=12, fontweight='bold')
plt.xlabel('Slip (mm)', fontsize=12)
plt.ylabel('Pull-out Force (N)', fontsize=12)
plt.legend(fontsize=11)
plt.grid(True, linestyle='--', alpha=0.6)

# 标出 XGBoost 预测的最高点（峰值）
max_idx = np.argmax(pred_y)
plt.plot(target_slip[max_idx], pred_y[max_idx], 'ro', markersize=8)
plt.text(target_slip[max_idx]+0.5, pred_y[max_idx], f'Peak: {pred_y[max_idx]:.1f}N', color='red', fontweight='bold')

plt.savefig('XGBoost_Prediction.png', dpi=300)
print("📊 预测结果已保存为 'XGBoost_Prediction.png'！")
plt.show()