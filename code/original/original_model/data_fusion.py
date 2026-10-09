import pandas as pd
import numpy as np
import os
from scipy.interpolate import interp1d

# ==========================================
# 1. 配置文件路径和重采样标准
# ==========================================
# 将这里换成你真实的 xlsx 文件名，比如 'experiment.xlsx'
metadata_file = 'experiment.xlsx'

# 设定统一标准：滑移拉到 25 mm，等距切分为 100 个点
target_max_slip = 25.0
num_points = 100
target_slip = np.linspace(0, target_max_slip, num_points)

# ==========================================
# 2. 读取参数总表 (特征 X)
# ==========================================
print(f"🚀 正在读取 Excel 特征总表: {metadata_file} ...")
# 【核心修改点】：这里换成了 read_excel
df_meta = pd.read_excel(metadata_file, header=1) 
df_meta = df_meta.dropna(subset=['file name']) 

all_samples = []
success_count = 0

print("🚀 开始进行数据缝合，请稍候...")

# ==========================================
# 3. 遍历总表，逐一处理对应的曲线文件 (标签 Y)
# ==========================================
for index, row in df_meta.iterrows():
    file_name = str(row['file name']).strip()
    
    # 检查你文件夹里有没有对应的 CSV 文件
    if not os.path.exists(file_name):
        print(f"⚠️ 找不到文件: {file_name}，已跳过")
        continue
        
    try:
        # 读取原始曲线数据 (没有表头，第一列滑移，第二列力)
        df_curve = pd.read_csv(file_name, header=None, names=['Slip', 'Force'])
        
        # 清洗数据：剔除负滑移，强制按滑移量递增排序并去重
        df_curve.loc[df_curve['Slip'] < 0, 'Slip'] = 0
        df_curve = df_curve.sort_values(by='Slip').drop_duplicates(subset='Slip').reset_index(drop=True)
        
        raw_slip = df_curve['Slip'].values
        raw_force = df_curve['Force'].values
        
        # 进行一维线性插值重采样
        interpolator = interp1d(raw_slip, raw_force, kind='linear', bounds_error=False, fill_value=(0, 0))
        target_force = interpolator(target_slip)
        
        # 组装这行数据的字典：先放入总表里的特征参数 X
        sample_data = row.to_dict()
        
        # 再放入刚才生成的 100 个拉拔力数据点 Y
        for i, force in enumerate(target_force):
            sample_data[f'Force_{i}'] = round(force, 2)
            
        all_samples.append(sample_data)
        success_count += 1
        
    except Exception as e:
        print(f"❌ 处理 {file_name} 时发生内部报错: {e}")

# ==========================================
# 4. 导出终极 AI 训练集
# ==========================================
if all_samples:
    df_final = pd.DataFrame(all_samples)
    final_output_name = 'Final_AI_Dataset.csv'
    df_final.to_csv(final_output_name, index=False)
    print(f"\n✅ 缝合完成！成功处理并拼接了 {success_count} 条数据。")
    print(f"🎉 你的机器学习终极训练集已生成，保存在同级目录: {final_output_name}")
else:
    print("\n⚠️ 没有成功生成任何数据，请检查你的 CSV 曲线文件是不是都放在了这个文件夹里。")