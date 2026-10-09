import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor

def run_true_ablation_study():
    # =========================================================
    # 1. Generate the "Complete" Synthetic Database (60+ curves)
    # =========================================================
    np.random.seed(42)
    X_full = []
    y_full = []
    slip_points = np.linspace(0, 15.0, 100)

    # Simulate 65 random pull-out tests (mixed straight and hooked, mixed fc)
    for _ in range(65):
        is_hooked = np.random.choice([0, 1])
        d_f = np.random.uniform(0.15, 0.75)
        L_e = np.random.uniform(6.5, 25.0)
        fu = np.random.uniform(1000, 2800)
        fc = np.random.uniform(30, 150)
        
        if is_hooked:
            tau = 8.0 + (fc - 30) * 0.1
            P_max = np.pi * d_f * L_e * tau * 2.5 # Hook enhancement
            for s in slip_points:
                if s <= 0.2:
                    f = P_max * 0.3 * (s/0.2)
                elif s <= 1.5:
                    f = P_max * 0.3 + (P_max * 0.7) * ((s-0.2)/1.3)
                else:
                    f = P_max * ((L_e - s)/(L_e - 1.5))**0.8 if s < L_e else 0
                X_full.append([is_hooked, d_f, L_e, fu, fc, s])
                y_full.append(max(0, f + np.random.normal(0, 0.5)))
        else:
            tau = 3.0 + (fc - 30) * 0.08
            P_max = np.pi * d_f * L_e * tau
            for s in slip_points:
                if s <= 0.25:
                    f = P_max * (2*(s/0.25) - (s/0.25)**2)
                else:
                    f = P_max * ((L_e - s)/(L_e - 0.25))**1.05 if s < L_e else 0
                X_full.append([is_hooked, d_f, L_e, fu, fc, s])
                y_full.append(max(0, f + np.random.normal(0, 0.5)))

    X_full = np.array(X_full)
    y_full = np.array(y_full)

    # =========================================================
    # 2. PERFORM ABLATION: Delete Wille & Yoo Data Distributions
    # (Remove all Straight fibers where fc > 100 MPa)
    # =========================================================
    mask = ~((X_full[:, 0] == 0) & (X_full[:, 4] > 100))
    X_ablated = X_full[mask]
    y_ablated = y_full[mask]
    print(f"Original data points: {len(X_full)}, After ablation: {len(X_ablated)}")

    # =========================================================
    # 3. Train AI Model on Ablated Data
    # =========================================================
    # We use a Random Forest regressor to map X -> Y directly
    rf_model = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
    rf_model.fit(X_ablated, y_ablated)

    # =========================================================
    # 4. Predict the Target Parameter Set (Straight, df=0.2, Le=6.5, fc=120)
    # =========================================================
    test_slips = np.linspace(0, 7.0, 150)
    X_target = np.column_stack((
        np.zeros_like(test_slips),              # Type = 0 (Straight)
        np.full_like(test_slips, 0.2),          # df = 0.2
        np.full_like(test_slips, 6.5),          # Le = 6.5
        np.full_like(test_slips, 2800),         # fu = 2800
        np.full_like(test_slips, 120),          # fc = 120
        test_slips                              # Slip
    ))

    y_pred_ml = rf_model.predict(X_target)
    y_pred_ml = np.clip(y_pred_ml, 0, None)
    y_pred_ml[0] = 0.0

    # =========================================================
    # 5. Generate True Calibrated Baseline (For Comparison)
    # =========================================================
    tau_true = 7.8
    P_max_true = np.pi * 0.2 * 6.5 * tau_true
    y_true = np.zeros_like(test_slips)
    for i, s in enumerate(test_slips):
        if s <= 0.25:
            y_true[i] = P_max_true * (2*(s/0.25) - (s/0.25)**2)
        elif s < 6.5:
            y_true[i] = P_max_true * ((6.5 - s)/(6.5 - 0.25))**1.05
        else:
            y_true[i] = 0

    # =========================================================
    # 6. Plot the True ML Ablation Results
    # =========================================================
    plt.figure(figsize=(10, 6.5), dpi=300)

    plt.plot(test_slips, y_true, color='#2ca02c', linewidth=2.5, linestyle='--', zorder=10,
             label=f'Calibrated Physical Baseline ($P_{{max}}$ = {P_max_true:.1f} N)')

    plt.plot(test_slips, y_pred_ml, color='#d62728', linewidth=3.0, zorder=5, alpha=0.9,
             label='True ML Prediction (Trained on Ablated DB)')

    plt.axvline(x=6.5, color='gray', linestyle=':', alpha=0.8)
    plt.text(6.6, 5, 'Full Extraction ($L_e$=6.5 mm)', color='gray', fontsize=11, rotation=90)

    plt.title('True AI Ablation Study: Prediction Without UHPC Straight Fiber Data', fontsize=14, pad=15, fontweight='bold')
    plt.xlabel('Slip (mm)', fontsize=13)
    plt.ylabel('Pull-out Load (N)', fontsize=13)
    plt.xlim(0, 7.5)
    plt.ylim(0, max(P_max_true * 1.5, 50)) 
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.legend(loc='upper right', fontsize=11, framealpha=0.9, edgecolor='black')

    plt.tight_layout()
    plt.savefig("True_ML_Ablation_Result.png")
    plt.show()
    print("Ablation study complete. Check 'True_ML_Ablation_Result.png'")

if __name__ == "__main__":
    run_true_ablation_study()