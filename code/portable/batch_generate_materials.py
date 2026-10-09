# Portable review copy. Numerical algorithms are unchanged. See docs/PORTABILITY_CHANGES.md.
from pathlib import Path
REVIEW_ROOT = Path(__file__).resolve().parents[2]
import numpy as np

# =========================================================
# 模块 1：鲁棒的物理特征提取算法 (从连续曲线中抓取 4 个特征点)
# =========================================================
def extract_four_features_robust(slip_array, force_array):
    n_points = len(force_array)
    idx_p2 = np.argmax(force_array)
    
    asc_slip = slip_array[:idx_p2]
    asc_force = force_array[:idx_p2]
    
    if len(asc_force) > 5:
        stiffness = np.gradient(asc_force, asc_slip)
        initial_stiffness = np.mean(stiffness[1:4])
        drop_indices = np.where(stiffness < initial_stiffness * 0.8)[0]
        idx_p1 = drop_indices[0] if len(drop_indices) > 0 else max(1, idx_p2 // 4)
    else:
        idx_p1 = max(0, idx_p2 - 1)

    idx_p4 = n_points - 1

    if idx_p4 - idx_p2 > 10:
        desc_slip = slip_array[idx_p2:idx_p4]
        desc_force = force_array[idx_p2:idx_p4]
        d1_desc = np.gradient(desc_force, desc_slip)
        d2_desc = np.gradient(d1_desc, desc_slip)
        idx_p3_relative = np.argmax(d2_desc)
        idx_p3 = idx_p2 + idx_p3_relative
        if idx_p3 <= idx_p2 + 5 or idx_p3 >= idx_p4 - 5:
            idx_p3 = idx_p2 + (idx_p4 - idx_p2) // 3
    else:
        idx_p3 = idx_p2 + (idx_p4 - idx_p2) // 2

    return [idx_p1, idx_p2, idx_p3, idx_p4]

# =========================================================
# 模块 2：AI 预测替身函数 (生成二维数组测试)
# =========================================================
def predict_curve_with_ai(d_f, L_e, f_u, f_c, theta):
    slip = np.linspace(0, 20, 200)
    force = np.zeros_like(slip)

    fc_factor = f_c / 50.0
    theta_factor = 1 + 0.1 * np.sin(np.radians(theta))

    f1 = 230.0 * fc_factor
    f2 = 480.0 * fc_factor * theta_factor
    f3 = 160.0 * fc_factor
    f4 = 60.0 * fc_factor

    s1, s2, s3, s4 = 0.5, 3.5, 7.0, 20.0

    for i, s in enumerate(slip):
        if s <= s1:
            force[i] = (f1 / s1) * s
        elif s <= s2:
            normalized_s = (s - s1) / (s2 - s1)
            force[i] = f1 + (f2 - f1) * np.sin(normalized_s * np.pi / 2)
        elif s <= s3:
            normalized_s = (s - s2) / (s3 - s2)
            force[i] = f3 + (f2 - f3) * (0.5 + 0.5 * np.cos(normalized_s * np.pi))
        else:
            force[i] = f4 + (f3 - f4) * np.exp(-0.3 * (s - s3))

    return slip.reshape(-1, 1), force.reshape(-1, 1)

# =========================================================
# 模块 3：核心批量生成与跨尺度写码引擎 (带 Pinching4 终极修复)
# =========================================================
def batch_create_opensees_materials():
    L_c = 32.0  # 混凝土网格特征长度
    
    fc_list = [40.0, 60.0, 80.0, 100.0]     
    theta_list = [0.0, 15.0, 30.0, 45.0]    
    d_f = 1.0                               
    L_e = 25.0                              
    f_u = 800.0                             
    
    A_f = 0.25 * np.pi * (d_f**2)           

    # 强制指定绝对路径，确保文件生成在正确位置
    save_path = str(Path.cwd() / "fiber_materials.tcl")

    with open(save_path, "w", encoding="utf-8") as f:
        f.write("# ==========================================\n")
        f.write("# 钢纤维 Pinching4 跨尺度本构库 (由 AI 批量生成)\n")
        f.write(f"# 网格特征长度 Lc = {L_c} mm, 纤维面积 Af = {A_f:.4f} mm^2\n")
        f.write("# ==========================================\n\n")
        
        matTag = 1 
        
        for f_c in fc_list:
            for theta in theta_list:
                # 1. 调用模型预测曲线
                slip, force = predict_curve_with_ai(d_f, L_e, f_u, f_c, theta)
                
                # 2. 拍扁二维数组，防止格式化报错
                slip = np.array(slip).flatten()
                force = np.array(force).flatten()
                
                # 3. 提取特征点
                indices = extract_four_features_robust(slip, force)
                feature_slips = slip[indices]
                feature_forces = force[indices]
                
                # 4. 转换：位移->应变，力->应力
                strain = feature_slips / L_c
                stress = feature_forces / A_f
                
                # 5. 强制转换为原生 Python 浮点数
                strain = [float(val) for val in strain]
                stress = [float(val) for val in stress]
                
                # 6. 写入 TCL 代码 (🌟 终极修复版：解决损伤类型字符串报错)
                f.write(f"# Material {matTag} | fc={f_c}MPa | theta={theta}deg\n")
                tcl_code = (
                    f"uniaxialMaterial Pinching4 {matTag} \\\n"
                    f"    {stress[0]:.2f} {strain[0]:.5f}  {stress[1]:.2f} {strain[1]:.5f}  "
                    f"{stress[2]:.2f} {strain[2]:.5f}  {stress[3]:.2f} {strain[3]:.5f} \\\n"
                    f"    -1.0 -0.0001  -1.5 -0.001  -2.0 -0.01  -2.5 -0.02 \\\n"
                    f"    1.0 0.0 0.0  1.0 0.0 0.0 \\\n"
                    f"    0.0 0.0 0.0 0.0 0.0 \\\n"
                    f"    0.0 0.0 0.0 0.0 0.0 \\\n"
                    f"    0.0 0.0 0.0 0.0 0.0 \\\n"
                    f"    0.0 cycle\n\n"   # <--- 唯一的变化：把 0 换成了单词 cycle
                )
                f.write(tcl_code)
                print(f"✅ 成功生成材料 {matTag:02d} (fc={f_c:5.1f} MPa, theta={theta:4.1f} deg)")
                
                matTag += 100
    
    print(f"\n📁 文件已成功保存至: {save_path}")

# =========================================================
# 启动器 (带防闪退机制)
# =========================================================
if __name__ == "__main__":
    try:
        print("🚀 正在启动 AI 跨尺度本构库生成引擎...\n")
        batch_create_opensees_materials()
        print("\n🎉 任务全部完成！")
    except Exception as e:
        print(f"\n❌ 运行中出现错误：{e}")
    finally:
        input("\n请按回车键 (Enter) 退出程序...")