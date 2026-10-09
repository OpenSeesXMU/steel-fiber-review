import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

# ==========================================
# 1. 数据加载与预处理
# ==========================================
print("📦 正在加载数据...")
df = pd.read_csv('Final_AI_Dataset.csv')

# 提取特征 X (前6个物理参数) 和 标签 Y (100个拉拔力点)
X_raw = df[['fiber type', 'df', 'fu', 'Le', 'fc', 'theta']].values
Y_raw = df.loc[:, 'Force_0':'Force_99'].values

# 归一化 (MinMaxScaler将数据缩放到 0~1 之间)
scaler_X = MinMaxScaler()
scaler_Y = MinMaxScaler()
X_scaled = scaler_X.fit_transform(X_raw)
Y_scaled = scaler_Y.fit_transform(Y_raw)

# 划分训练集和测试集
X_train, X_test, Y_train, Y_test = train_test_split(X_scaled, Y_scaled, test_size=0.2, random_state=42)

# 转换为 PyTorch 张量
X_train_tensor = torch.FloatTensor(X_train)
Y_train_tensor = torch.FloatTensor(Y_train)
X_test_tensor = torch.FloatTensor(X_test)
Y_test_tensor = torch.FloatTensor(Y_test)

dataset = TensorDataset(X_train_tensor, Y_train_tensor)
dataloader = DataLoader(dataset, batch_size=16, shuffle=True)

# ==========================================
# 🌟 终极定海神针：基于真实峰值位置的动态掩膜损失函数
# ==========================================
def feature_point_loss(predictions, targets):
    # 1. 计算每一个点的基础平方误差 (不求平均，保留每个点各自的独立误差)
    mse_none = nn.MSELoss(reduction='none')
    point_errors = mse_none(predictions, targets)
    
    # 2. 创建一个权重矩阵 (默认所有 100 个点权重为 1.0)
    weights = torch.ones_like(targets)
    
    # 3. 动态寻找【真实曲线】的峰值位置！
    # target_peak_indices 就是真实曲线最高点所在的 x 轴坐标点 (比如第 10 个点)
    target_peak_vals, target_peak_indices = torch.max(targets, dim=1)
    
    for i in range(targets.size(0)):
        peak_idx = target_peak_indices[i].item()
        
        # A. 真实峰值点所在位置，误差惩罚直接拉到 30 倍！(绝不允许峰值位置左右偏移)
        weights[i, peak_idx] = 30.0
        
        # B. 峰值前后的局部区域 (前后 5 个点)，放大 10 倍 (逼迫它跟着蓝线一起陡峭下降)
        start_idx = max(0, peak_idx - 5)
        end_idx = min(100, peak_idx + 6)
        weights[i, start_idx:end_idx] += 10.0
        
        # C. 上升段 (从 0 到峰值)，放大 5 倍 (逼迫它的初始刚度必须和真实实验一致)
        weights[i, 0:peak_idx] += 5.0
        
    # 将我们精心设计的“惩罚权重”乘到误差上，然后求平均
    weighted_base_loss = torch.mean(point_errors * weights)
    
    # 4. 曲线斜率误差 (保留，用于限制曲线不要长满“毛刺”)
    pred_diff = predictions[:, 1:] - predictions[:, :-1]
    target_diff = targets[:, 1:] - targets[:, :-1]
    shape_loss = nn.MSELoss()(pred_diff, target_diff)
    
    # 5. 残余摩擦段误差 (换用绝对值 L1Loss，死死咬住尾部的平缓段)
    pred_residual = torch.mean(predictions[:, -15:], dim=1)
    target_residual = torch.mean(targets[:, -15:], dim=1)
    residual_loss = nn.L1Loss()(pred_residual, target_residual)
    
    # 组合总 Loss：由于动态掩膜已经极其强大，其他权重回归正常
    total_loss = 1.0 * weighted_base_loss + 5.0 * shape_loss + 2.0 * residual_loss
    return total_loss

# ==========================================
# 🚀 3. 核心优化：扩容升级版神经网络架构
# ==========================================
class EnhancedFiberPredictor(nn.Module):
    def __init__(self):
        super(EnhancedFiberPredictor, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(6, 128),      # 变宽：64 -> 128
            nn.ReLU(),
            nn.Dropout(p=0.1),      # 引入 10% 随机失活防过拟合
            nn.Linear(128, 256),    # 变宽：128 -> 256
            nn.ReLU(),
            nn.Dropout(p=0.1),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 100)     # 输出 100 个点
        )

    def forward(self, x):
        return self.net(x)

model = EnhancedFiberPredictor()

# ==========================================
# 🎯 4. 核心优化：动态学习率训练策略
# ==========================================
# 初始学习率调小一点
optimizer = optim.Adam(model.parameters(), lr=0.002) 
# 每过 300 轮，学习率乘以 0.5 进行精细打磨
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=300, gamma=0.5)

epochs = 2000  # 因为学习率小了，我们把训练轮数拉长到 1200 轮
print(f"🧠 开始训练物理增强版 AI 模型，共 {epochs} 轮...")

for epoch in range(epochs):
    model.train()
    total_loss = 0
    for batch_x, batch_y in dataloader:
        optimizer.zero_grad()
        predictions = model(batch_x)
        
        # 使用我们的自定义损失函数！
        loss = feature_point_loss(predictions, batch_y) 
        
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
        
    scheduler.step() # 更新学习率调度器
    
    if (epoch + 1) % 150 == 0:
        current_lr = scheduler.get_last_lr()[0]
        print(f"Epoch [{epoch+1}/{epochs}], Loss: {total_loss/len(dataloader):.4f}, LR: {current_lr:.5f}")

print("✅ 训练完成！")

# ==========================================
# 5. 预测与可视化验证
# ==========================================
model.eval()
with torch.no_grad():
    # 拿测试集里的第 1 个样本考试
    test_idx = 0
    sample_x = X_test_tensor[test_idx].unsqueeze(0)
    real_y_scaled = Y_test_tensor[test_idx].unsqueeze(0)
    
    pred_y_scaled = model(sample_x)
    
    # 逆归一化
    pred_y = scaler_Y.inverse_transform(pred_y_scaled.numpy())
    real_y = scaler_Y.inverse_transform(real_y_scaled.numpy())
    real_x = scaler_X.inverse_transform(sample_x.numpy())[0]

# 画图对比
target_slip = np.linspace(0, 25.0, 100)

plt.figure(figsize=(10, 6))
plt.plot(target_slip, real_y[0], 'b-', linewidth=2.5, label='Real Experiment Curve')
plt.plot(target_slip, pred_y[0], 'r--', linewidth=2.5, label='AI Predicted Curve (Physics-Informed)')

type_str = 'Hooked' if int(real_x[0]) == 1 else 'Straight'
plt.title(f"Physics-Informed AI Prediction vs Real Experiment\n"
          f"(Type:{type_str}, df:{real_x[1]:.1f}mm, fu:{real_x[2]:.0f}MPa, "
          f"Le:{real_x[3]:.1f}mm, fc:{real_x[4]:.1f}MPa, Angle:{real_x[5]:.0f}°)", 
          fontsize=12, fontweight='bold')
plt.xlabel('Slip (mm)', fontsize=12)
plt.ylabel('Pull-out Force (N)', fontsize=12)
plt.legend(fontsize=11)
plt.grid(True, linestyle='--', alpha=0.6)

# 标出预测的最高点（峰值）方便直观检查
max_idx = np.argmax(pred_y[0])
plt.plot(target_slip[max_idx], pred_y[0][max_idx], 'ro', markersize=8)
plt.text(target_slip[max_idx]+0.5, pred_y[0][max_idx], f'Peak: {pred_y[0][max_idx]:.1f}N', color='red', fontweight='bold')

plt.savefig('Enhanced_AI_Prediction.png', dpi=300)
print("📊 增强版预测对比图已保存为 'Enhanced_AI_Prediction.png'！")
plt.show()