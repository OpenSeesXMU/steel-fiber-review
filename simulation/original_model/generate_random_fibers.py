import numpy as np
import math
import random
import os

# ====================================================================
# 核心配置参数 (请根据你的实际情况微调)
# ====================================================================
NODE_FILE = "node0.tcl"          # 你原有的混凝土节点文件
OUTPUT_FILE = "fibers.tcl"       # 即将生成的钢纤维单元文件

TOTAL_FIBERS = 5000              # 你想在模型里撒多少根纤维？(例如 5000 根)
FIBER_LENGTH = 35.0              # 钢纤维的实际物理长度 (mm)
FIBER_AREA = 0.785               # 钢纤维的横截面积 (mm^2)，假设直径 1.0mm
MAT_TAG = 1                      # 你在 fiber_materials.tcl 里生成的材料编号 (默认全用 1 号本构)
START_ELE_ID = 1000000           # 钢纤维单元的起始编号 (设大一点，防止和混凝土单元编号冲突)

# ====================================================================
# 步骤 1：读取并解析原有的混凝土节点坐标
# ====================================================================
def read_concrete_nodes(filepath):
    print(f"📂 正在读取混凝土节点文件: {filepath} ...")
    nodes = {}
    with open(filepath, 'r') as f:
        for line in f:
            parts = line.strip().split()
            # 解析 OpenSees 节点格式: node tag X Y Z
            if len(parts) >= 5 and parts[0].lower() == 'node':
                tag = int(parts[1])
                x, y, z = float(parts[2]), float(parts[3]), float(parts[4])
                nodes[tag] = np.array([x, y, z])
    print(f"✅ 成功读取 {len(nodes)} 个混凝土节点。")
    return nodes

# ====================================================================
# 步骤 2：生成三维随机纤维，并就近锚固到混凝土节点
# ====================================================================
def generate_fibers(nodes):
    print(f"🎲 正在生成 {TOTAL_FIBERS} 根随机纤维并进行空间锚固...")
    
    # 获取模型的空间边界 (Bounding Box)
    node_coords = np.array(list(nodes.values()))
    min_bounds = np.min(node_coords, axis=0)
    max_bounds = np.max(node_coords, axis=0)
    
    node_tags = list(nodes.keys())
    
    # 建立 KDTree 以实现光速的“最近节点搜索” (如果数据量极大推荐使用 scipy.spatial.KDTree)
    # 这里为了不让你安装额外库，写一个基于向量化的高效简易查找
    def find_nearest_node(target_coord):
        distances = np.linalg.norm(node_coords - target_coord, axis=1)
        nearest_idx = np.argmin(distances)
        return node_tags[nearest_idx]

    fiber_elements = []
    
    for i in range(TOTAL_FIBERS):
        # 1. 随机生成纤维的中点位置 (确保在模型范围内)
        cx = random.uniform(min_bounds[0], max_bounds[0])
        cy = random.uniform(min_bounds[1], max_bounds[1])
        cz = random.uniform(min_bounds[2], max_bounds[2])
        center = np.array([cx, cy, cz])
        
        # 2. 随机生成三维空间方向 (球面坐标系)
        theta = random.uniform(0, math.pi)       # 极角
        phi = random.uniform(0, 2 * math.pi)     # 方位角
        
        dx = (FIBER_LENGTH / 2.0) * math.sin(theta) * math.cos(phi)
        dy = (FIBER_LENGTH / 2.0) * math.sin(theta) * math.sin(phi)
        dz = (FIBER_LENGTH / 2.0) * math.cos(theta)
        
        # 计算理论起点和终点
        pt1 = center - np.array([dx, dy, dz])
        pt2 = center + np.array([dx, dy, dz])
        
        # 3. 就近锚固：寻找离 pt1 和 pt2 最近的真实混凝土节点！
        node1_tag = find_nearest_node(pt1)
        node2_tag = find_nearest_node(pt2)
        
        # 防止起点和终点锚固到同一个混凝土节点上 (退化成长度为0的杆)
        if node1_tag != node2_tag:
            ele_id = START_ELE_ID + len(fiber_elements)
            fiber_elements.append((ele_id, node1_tag, node2_tag))
            
    print(f"✅ 成功生成并锚固了 {len(fiber_elements)} 根有效纤维单元。")
    return fiber_elements

# ====================================================================
# 步骤 3：输出 OpenSees 可读的 TCL 文件
# ====================================================================
def write_tcl_file(fiber_elements):
    print(f"💾 正在写入 OpenSees 单元文件: {OUTPUT_FILE} ...")
    with open(OUTPUT_FILE, 'w') as f:
        f.write("# ==========================================\n")
        f.write("# 钢纤维离散模型 Truss 单元定义 (跨尺度锚固)\n")
        f.write(f"# 纤维总数: {len(fiber_elements)}, 横截面积: {FIBER_AREA}, 本构标签: {MAT_TAG}\n")
        f.write("# ==========================================\n\n")
        
        for ele_id, n1, n2 in fiber_elements:
            # OpenSees Truss 单元语法: element truss $eleTag $iNode $jNode $A $matTag
            f.write(f"element truss {ele_id} {n1} {n2} {FIBER_AREA} {MAT_TAG}\n")
            
    print("🎉 跨尺度离散纤维网络生成完毕！")

# ====================================================================
# 主程序
# ====================================================================
if __name__ == "__main__":
    if not os.path.exists(NODE_FILE):
        print(f"❌ 错误：找不到文件 '{NODE_FILE}'，请确保它和本脚本在同一目录下。")
    else:
        concrete_nodes = read_concrete_nodes(NODE_FILE)
        fibers = generate_fibers(concrete_nodes)
        write_tcl_file(fibers)
        input("\n按回车键退出...")