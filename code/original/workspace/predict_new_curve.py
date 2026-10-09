import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

# ==========================================
# 1. 重新加载数据并拟合 Scaler (必须和训练时的尺子完全一致)
# ==========================================
df = pd.read_csv('Final_AI_Dataset.csv')
X_raw = df[['fiber type', 'df', 'fu', 'Le', 'fc', 'theta']].values
Y_raw = df.loc[:, 'Force_0':'Force_99'].values

scaler_X = MinMaxScaler()
scaler_Y = MinMaxScaler()
scaler_X.fit(X_raw)
scaler_Y.fit(Y_raw)

# ==========================================
# 2. 定义相同的神经网络架构
# ==========================================
class FiberPredictor(nn.Module):
    def __init__(self):
        super(FiberPredictor, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(6, 64),
            nn.ReLU(),
            nn.Linear(64, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, 100)
        )
    def forward(self, x):
        return self.net(x)

# ==========================================
# 3. 快速后台训练 (全部数据梭哈，因为只有61条，瞬间跑完)
# ==========================================
print("⏳ 正在后台准备 AI 模型，请稍候 (约需2秒)...")
model = FiberPredictor()
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.005)

X_train_tensor = torch.FloatTensor(scaler_X.transform(X_raw))
Y_train_tensor = torch.FloatTensor(scaler_Y.transform(Y_raw))

model.train()
for epoch in range(800):  # 训练800轮
    optimizer.zero_grad()
    loss = criterion(model(X_train_tensor), Y_train_tensor)
    loss.backward()
    optimizer.step()

print("✅ AI 虚拟试验机准备完毕！\n")

# ==========================================
# 🌟 4. 核心功能：为你写一个预测任意参数的函数
# ==========================================
def predict_and_plot(fiber_type, df_val, fu_val, Le_val, fc_val, theta_val):
    model.eval()
    with torch.no_grad():
        # 将你的自定义输入组装成矩阵
        new_input = np.array([[fiber_type, df_val, fu_val, Le_val, fc_val, theta_val]])
        
        # 对输入进行归一化
        new_input_scaled = scaler_X.transform(new_input)
        new_input_tensor = torch.FloatTensor(new_input_scaled)
        
        # AI 进行预测
        predicted_y_scaled = model(new_input_tensor)
        
        # 对预测结果进行逆归一化，还原为真实的 牛顿(N) 力
        predicted_y = scaler_Y.inverse_transform(predicted_y_scaled.numpy())[0]
        
    # 画出预测曲线
    target_slip = np.linspace(0, 25.0, 100)
    plt.figure(figsize=(10, 6))
    plt.plot(target_slip, predicted_y, 'r-', linewidth=2.5, label='AI Predicted Curve')
    
    # 图表排版
    type_str = 'Hooked' if fiber_type == 1 else 'Straight'
    title_str = (f"AI Virtual Pull-out Test\n"
                 f"Type: {type_str}, df: {df_val}mm, fu: {fu_val}MPa\n"
                 f"Le: {Le_val}mm, fc: {fc_val}MPa, Angle: {theta_val}°")
    plt.title(title_str)
    plt.xlabel('Slip (mm)')
    plt.ylabel('Pull-out Force (N)')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    
    # 保存并显示
    save_name = f'Virtual_Test_fc{fc_val}_type{fiber_type}.png'
    plt.savefig(save_name)
    print(f"📊 预测曲线图已生成，保存为: {save_name}")
    plt.show()
    
    # 将预测的 100 个点以 DataFrame 形式返回，方便你导出
    df_result = pd.DataFrame({'Slip(mm)': target_slip, 'Force(N)': predicted_y})
    return df_result

# ==========================================
# 🎯 5. 开始你的虚拟试验！
# ==========================================
# ！！！你可以在这里随意修改这 6 个基本参数 ！！！
my_predicted_data = predict_and_plot(
    fiber_type = 1,       # 1为端钩，0为平直
    df_val     = 0.8,     # 假设纤维直径为 0.8 mm
    fu_val     = 1000,    # 假设抗拉强度为 1000 MPa
    Le_val     = 20.0,    # 假设埋深 20 mm
    fc_val     = 55.0,    # 假设基体强度为 55 MPa (你的数据库里可能没有刚好55的数据)
    theta_val  = 0        # 0度垂直拉拔
)

# 【终极目标接轨】把生成的曲线存为 CSV，准备导入 ABAQUS 或 OpenSees 节点模型！
my_predicted_data.to_csv('Predicted_Curve_For_Abaqus.csv', index=False)
print("💾 预测的坐标数据点已保存为 'Predicted_Curve_For_Abaqus.csv'")