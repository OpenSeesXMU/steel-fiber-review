# Portable review copy. Numerical algorithms are unchanged. See docs/PORTABILITY_CHANGES.md.
from pathlib import Path
REVIEW_ROOT = Path(__file__).resolve().parents[2]
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

# ==========================================
# 1. 数据加载 (极简版：不需要 MinMaxScaler 归一化！)
# 树模型天生免疫量纲差异，可以直接吃原始数据
# ==========================================
print("📦 正在加载数据...")
df = pd.read_csv(str(REVIEW_ROOT / "data" / "database" / "Final_AI_Dataset.csv"))

# 提取特征 X 和 标签 Y
X_raw = df[['fiber type', 'df', 'fu', 'Le', 'fc', 'theta']].values
Y_raw = df.loc[:, 'Force_0':'Force_99'].values

# 划分训练集和测试集
X_train, X_test, Y_train, Y_test = train_test_split(X_raw, Y_raw, test_size=0.2, random_state=42)

# ==========================================
# 🌲 2. 构建并训练随机森林模型
# ==========================================
print("🌲 正在召唤 300 棵决策树进行联合训练...")
# n_estimators=300 表示建立 300 棵树进行投票，n_jobs=-1 表示调用电脑所有CPU核心加速
rf_model = RandomForestRegressor(n_estimators=300, random_state=42, n_jobs=-1)

# 直接暴力拟合 (1秒内跑完)
rf_model.fit(X_train, Y_train)
print("✅ 训练完成！毫无痛苦！")

# ==========================================
# 🎯 3. 预测与可视化
# ==========================================
# 抽取测试集第一个样本
test_idx = 0
sample_x = X_test[test_idx].reshape(1, -1)
real_y = Y_test[test_idx]
real_x = sample_x[0]

# AI 直接吐出 100 个真实的拉拔力数值
pred_y = rf_model.predict(sample_x)[0]

# ==========================================
# 📊 4. 画图对比
# ==========================================
target_slip = np.linspace(0, 25.0, 100)

plt.figure(figsize=(10, 6))
plt.plot(target_slip, real_y, 'b-', linewidth=2.5, label='Real Experiment Curve')
plt.plot(target_slip, pred_y, 'r--', linewidth=2.5, label='Random Forest Predicted Curve')

type_str = 'Hooked' if int(real_x[0]) == 1 else 'Straight'
plt.title(f"Random Forest Prediction vs Real Experiment\n"
          f"(Type:{type_str}, df:{real_x[1]:.1f}mm, fu:{real_x[2]:.0f}MPa, "
          f"Le:{real_x[3]:.1f}mm, fc:{real_x[4]:.1f}MPa, Angle:{real_x[5]:.0f}°)", 
          fontsize=12, fontweight='bold')
plt.xlabel('Slip (mm)', fontsize=12)
plt.ylabel('Pull-out Force (N)', fontsize=12)
plt.legend(fontsize=11)
plt.grid(True, linestyle='--', alpha=0.6)

# 标出预测的最高点（峰值）
max_idx = np.argmax(pred_y)
plt.plot(target_slip[max_idx], pred_y[max_idx], 'ro', markersize=8)
plt.text(target_slip[max_idx]+0.5, pred_y[max_idx], f'Peak: {pred_y[max_idx]:.1f}N', color='red', fontweight='bold')

plt.savefig('RF_Prediction.png', dpi=300)
print("📊 预测结果已保存为 'RF_Prediction.png'！请打开查看！")
plt.show()