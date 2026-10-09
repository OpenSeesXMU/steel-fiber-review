import numpy as np
import random
import math
import glob
from scipy.spatial import KDTree
import os
import sys
import traceback

print(">>> [Python Engine] Reading concrete nodes and identifying PID ownership...")

try:
    concrete_nodes_dict = {}
    node_ownership_map = {}  

    # 1. Read files
    node_files = glob.glob('node*.tcl')
    if not node_files:
        print("ERROR: No node*.tcl files found in the current directory.")
        sys.exit(1)

    print(f">>> Found {len(node_files)} node*.tcl files, parsing data...")

    for file_name in node_files:
        try:
            file_pid = int(file_name.lower().replace('node', '').replace('.tcl', ''))
        except ValueError:
            continue

        with open(file_name, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line.startswith('node'):
                    parts = line.split()
                    if len(parts) >= 5:
                        try:
                            tag = int(parts[1])
                            x, y, z = float(parts[2]), float(parts[3]), float(parts[4])
                            concrete_nodes_dict[tag] = (x, y, z)
                            node_ownership_map[tag] = file_pid
                        except ValueError:
                            continue

    if not concrete_nodes_dict:
        print("ERROR: No valid nodes successfully read.")
        sys.exit(1)

    print(f">>> Successfully read {len(concrete_nodes_dict)} nodes. Building spatial KD-Tree...")

    node_tags = list(concrete_nodes_dict.keys())
    node_coords = list(concrete_nodes_dict.values())
    tree = KDTree(node_coords)

    # 2. Parameters
    coords_arr = np.array(node_coords)
    min_x, min_y, min_z = coords_arr.min(axis=0)
    max_x, max_y, max_z = coords_arr.max(axis=0)

    Lf = 13.0     
    Vf = 0.02     
    Af = math.pi * (0.2 / 2)**2 
    V_total = (max_x - min_x) * (max_y - min_y) * (max_z - min_z)

    equiv_factor = 2000.0 
    Af_equiv = Af * equiv_factor
    N_fibers = int((V_total * Vf) / (Af * Lf) / equiv_factor)

    fiber_data_output = []
    start_fiber_node = 10000000
    start_fiber_ele =  10000000

    print(f">>> Target fibers to generate: {N_fibers}...")

    # 3. Geometry generation
    for i in range(N_fibers):
        cx, cy, cz = random.uniform(min_x, max_x), random.uniform(min_y, max_y), random.uniform(min_z, max_z)
        cos_theta = 2 * random.random() - 1
        sin_theta = math.sqrt(1 - cos_theta**2)
        phi = 2 * math.pi * random.random()
        
        dx, dy, dz = sin_theta * math.cos(phi), sin_theta * math.sin(phi), cos_theta
        p1 = (cx + Lf/2 * dx, cy + Lf/2 * dy, cz + Lf/2 * dz)
        p2 = (cx - Lf/2 * dx, cy - Lf/2 * dy, cz - Lf/2 * dz)
        
        _, idx1 = tree.query(p1)
        _, idx2 = tree.query(p2)
        closest_node_1 = node_tags[idx1]
        closest_node_2 = node_tags[idx2]
        
        owner_pid_1 = node_ownership_map.get(closest_node_1, -1)
        owner_pid_2 = node_ownership_map.get(closest_node_2, -1)
        
        if owner_pid_1 == owner_pid_2 and owner_pid_1 != -1:
            fNode1 = start_fiber_node + 2*i
            fNode2 = start_fiber_node + 2*i + 1
            fEle = start_fiber_ele + i
            
            line = f"{owner_pid_1} {closest_node_1} {closest_node_2} {p1[0]:.3f} {p1[1]:.3f} {p1[2]:.3f} {p2[0]:.3f} {p2[1]:.3f} {p2[2]:.3f} {fNode1} {fNode2} {fEle}\n"
            fiber_data_output.append(line)

    # 4. Write data
    with open("global_fiber_data.txt", 'w') as f:
        f.writelines(fiber_data_output)
    print(">>> [Python Engine] Data file 'global_fiber_data.txt' closed and saved.")

    # 5. Fire the signal flag
    with open("python_done.flag", "w") as f:
        f.write("OK")
    print(">>> [Python Engine Done] Signal flag 'python_done.flag' generated.")

except Exception as e:
    print(f"FATAL ERROR IN PYTHON: {e}")
    traceback.print_exc()
    sys.exit(1)