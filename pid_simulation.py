# =================================================================================
# COMPLETE PID FAMILY CONTROLLER FOR LASER POWER STABILIZATION
# =================================================================================
# This script implements P-only, PI, and PID controllers sequentially.
# It loads experimental data, simulates closed-loop response for each controller,
# quantifies performance metrics, and generates comparative visualizations.

# Import necessary libraries for numerical operations, data handling, control systems, and plotting.
import numpy as np
import csv
import control
import matplotlib.pyplot as plt
import os

# =================================================================================
# CREATE OUTPUT DIRECTORY
# =================================================================================

# Create the "data" folder if it doesn't exist
data_folder = "data"
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

# Create the "simulation data" subfolder inside "data"
simulation_folder = os.path.join(data_folder, "simulation data")
if not os.path.exists(simulation_folder):
    os.makedirs(simulation_folder)

print(f"Results will be saved to: {simulation_folder}")

# =================================================================================
# SECTION 1: DATA LOADING AND PREPARATION
# =================================================================================

# Initialize an empty list to store raw power readings from the CSV file.
powers = []
# Open the data file '0 dBm.csv' for reading.
with open('0dBm.csv', 'r') as f:
    # Create a CSV reader object to parse the file.
    reader = csv.reader(f)
    # Iterate through each row in the CSV file.
    for row in reader:
        # Filter for rows that have exactly 4 columns and where the first item is a digit.
        if len(row) == 4 and row[0].isdigit():
            try:
                # Attempt to convert the value in the 4th column (index 3) to a float and append to list.
                powers.append(float(row[3]))
            except ValueError:
                # If conversion fails (e.g., if it's text), skip this row silently.
                pass

# Convert the list of power readings into a NumPy array for efficient computation.
# Select only the first 601 samples, representing the first minute of data at 0.1s intervals.
powers = np.array(powers[:601])
# Calculate the mean of this data segment to serve as the target setpoint for the controller.
setpoint = np.mean(powers)
# Calculate the disturbance signal: the deviation of each sample from the target setpoint.
disturbance = powers - setpoint
# Define the discrete time step (sampling period) of the data, 0.1 seconds.
dt = 0.1
# Create a time vector from 0 to (number_of_samples * dt) in steps of dt.
time = np.arange(0, len(powers) * dt, dt)

# =================================================================================
# SECTION 2: CONTROLLER GAIN DEFINITION
# =================================================================================
# Define PID controller gains. These are "mild" values chosen to clearly visualize 
# the incremental effect of each term while maintaining stability.
kp = 1.0  # Proportional gain
ki = 8.0  # Integral gain
kd = 0.5  # Derivative gain

print("=" * 80)
print("PID FAMILY CONTROLLER SIMULATION FOR LASER POWER STABILIZATION")
print("=" * 80)
print(f"\nData Summary:")
print(f"  - Number of samples: {len(powers)}")
print(f"  - Time duration: {time[-1]:.1f} seconds")
print(f"  - Sampling interval: {dt} seconds")
print(f"  - Setpoint (mean power): {setpoint:.7f} W ({setpoint*1e3:.2f} mW)")
print(f"\nController Gains:")
print(f"  - Kp (Proportional): {kp}")
print(f"  - Ki (Integral): {ki}")
print(f"  - Kd (Derivative): {kd}")

# =================================================================================
# SECTION 3: P-ONLY CONTROLLER SIMULATION
# =================================================================================

print("\n" + "=" * 80)
print("STAGE 1: P-ONLY CONTROLLER SIMULATION")
print("=" * 80)

# Create continuous-time transfer function for P controller: C(s) = Kp.
C_p = control.TransferFunction([kp], [1])
# Model the closed-loop system's response to disturbance.
sys_p = 1 / (1 + C_p)
# Convert to discrete-time using Zero-Order Hold.
sys_p_disc = control.c2d(sys_p, dt, method='zoh')
# Simulate response to disturbance.
_, y_p = control.forced_response(sys_p_disc, T=time, U=disturbance)
# Calculate stabilized output.
stab_p = setpoint + y_p

# Calculate P-only performance metrics.
p_mean = np.mean(stab_p)
p_std = np.std(stab_p)
p_rsd = (p_std / p_mean) * 100
p_min = np.min(stab_p)
p_max = np.max(stab_p)
p_pp = p_max - p_min
p_pp_rel = (p_pp / p_mean) * 100
p_improvement = np.std(powers) / p_std

print(f"\n[P-Only Controller Results]")
print(f"  Stabilized Mean: {p_mean:.7f} W")
print(f"  Stabilized Std: {p_std:.3e} W")
print(f"  RSD: {p_rsd:.4f}%")
print(f"  Peak-to-Peak: {p_pp:.3e} W ({p_pp_rel:.4f}%)")
print(f"  Improvement Factor: {p_improvement:.2f}x")

# =================================================================================
# SECTION 4: PI CONTROLLER SIMULATION
# =================================================================================

print("\n" + "=" * 80)
print("STAGE 2: PI CONTROLLER SIMULATION")
print("=" * 80)

# Create continuous-time transfer function for PI controller: C(s) = (Kp*s + Ki)/s.
C_pi = control.TransferFunction([kp, ki], [1, 0])
# Model closed-loop response.
sys_pi = 1 / (1 + C_pi)
# Convert to discrete-time.
sys_pi_disc = control.c2d(sys_pi, dt, method='zoh')
# Simulate response.
_, y_pi = control.forced_response(sys_pi_disc, T=time, U=disturbance)
# Calculate stabilized output.
stab_pi = setpoint + y_pi

# Calculate PI performance metrics.
pi_mean = np.mean(stab_pi)
pi_std = np.std(stab_pi)
pi_rsd = (pi_std / pi_mean) * 100
pi_min = np.min(stab_pi)
pi_max = np.max(stab_pi)
pi_pp = pi_max - pi_min
pi_pp_rel = (pi_pp / pi_mean) * 100
pi_improvement = np.std(powers) / pi_std

print(f"\n[PI Controller Results]")
print(f"  Stabilized Mean: {pi_mean:.7f} W")
print(f"  Stabilized Std: {pi_std:.3e} W")
print(f"  RSD: {pi_rsd:.4f}%")
print(f"  Peak-to-Peak: {pi_pp:.3e} W ({pi_pp_rel:.4f}%)")
print(f"  Improvement Factor: {pi_improvement:.2f}x")

# =================================================================================
# SECTION 5: PID CONTROLLER SIMULATION
# =================================================================================

print("\n" + "=" * 80)
print("STAGE 3: FULL PID CONTROLLER SIMULATION")
print("=" * 80)

# Create continuous-time transfer function for PID controller: C(s) = (Kd*s^2 + Kp*s + Ki)/s.
C_pid = control.TransferFunction([kd, kp, ki], [1, 0])
# Model closed-loop response.
sys_pid = 1 / (1 + C_pid)
# Convert to discrete-time.
sys_pid_disc = control.c2d(sys_pid, dt, method='zoh')
# Simulate response.
_, y_pid = control.forced_response(sys_pid_disc, T=time, U=disturbance)
# Calculate stabilized output.
stab_pid = setpoint + y_pid

# Calculate PID performance metrics.
pid_mean = np.mean(stab_pid)
pid_std = np.std(stab_pid)
pid_rsd = (pid_std / pid_mean) * 100
pid_min = np.min(stab_pid)
pid_max = np.max(stab_pid)
pid_pp = pid_max - pid_min
pid_pp_rel = (pid_pp / pid_mean) * 100
pid_improvement = np.std(powers) / pid_std

print(f"\n[Full PID Controller Results]")
print(f"  Stabilized Mean: {pid_mean:.7f} W")
print(f"  Stabilized Std: {pid_std:.3e} W")
print(f"  RSD: {pid_rsd:.4f}%")
print(f"  Peak-to-Peak: {pid_pp:.3e} W ({pid_pp_rel:.4f}%)")
print(f"  Improvement Factor: {pid_improvement:.2f}x")

# =================================================================================
# SECTION 6: COMPREHENSIVE PERFORMANCE COMPARISON TABLE
# =================================================================================

print("\n" + "=" * 80)
print("PERFORMANCE COMPARISON SUMMARY")
print("=" * 80)

# Original signal metrics.
orig_mean = np.mean(powers)
orig_std = np.std(powers)
orig_rsd = (orig_std / orig_mean) * 100
orig_min = np.min(powers)
orig_max = np.max(powers)
orig_pp = orig_max - orig_min
orig_pp_rel = (orig_pp / orig_mean) * 100

print("\n[1] BASIC STATISTICS")
print(f"    {'Metric':<20} {'Original':<15} {'P-Only':<15} {'PI':<15} {'PID':<15}")
print("-" * 80)
print(f"    {'Mean Power (W)':<20} {orig_mean:.7f}  {p_mean:.7f}  {pi_mean:.7f}  {pid_mean:.7f}")
print(f"    {'Std Deviation (W)':<20} {orig_std:.3e}  {p_std:.3e}  {pi_std:.3e}  {pid_std:.3e}")
print(f"    {'Variance (W²)':<20} {np.var(powers):.3e}  {np.var(stab_p):.3e}  {np.var(stab_pi):.3e}  {np.var(stab_pid):.3e}")

print("\n[2] RELATIVE STABILITY METRICS")
print(f"    {'Metric':<20} {'Original':<15} {'P-Only':<15} {'PI':<15} {'PID':<15}")
print("-" * 80)
print(f"    {'RSD (%)':<20} {orig_rsd:.4f}       {p_rsd:.4f}       {pi_rsd:.4f}       {pid_rsd:.4f}")
print(f"    {'Peak-to-Peak (W)':<20} {orig_pp:.3e}  {p_pp:.3e}  {pi_pp:.3e}  {pid_pp:.3e}")
print(f"    {'P-P Relative (%)':<20} {orig_pp_rel:.4f}       {p_pp_rel:.4f}       {pi_pp_rel:.4f}       {pid_pp_rel:.4f}")

print("\n[3] PERFORMANCE IMPROVEMENT")
print(f"    {'Metric':<20} {'P-Only':<15} {'PI':<15} {'PID':<15}")
print("-" * 60)
print(f"    {'Improvement Factor (STD)':<20} {p_improvement:.2f}x        {pi_improvement:.2f}x        {pid_improvement:.2f}x")
print(f"    {'RSD Improvement (×)':<20} {(orig_rsd/p_rsd):.2f}x        {(orig_rsd/pi_rsd):.2f}x        {(orig_rsd/pid_rsd):.2f}x")
print(f"    {'Noise Reduction (%)':<20} {(1-p_std/orig_std)*100:.1f}%        {(1-pi_std/orig_std)*100:.1f}%        {(1-pid_std/orig_std)*100:.1f}%")

print("\n[4] CONTROL SPECIFICATIONS")
print(f"    {'Controller':<12} {'Kp':<10} {'Ki':<10} {'Kd':<10}")
print("-" * 45)
print(f"    {'P-Only':<12} {kp:<10} {'-':<10} {'-':<10}")
print(f"    {'PI':<12} {kp:<10} {ki:<10} {'-':<10}")
print(f"    {'PID':<12} {kp:<10} {ki:<10} {kd:<10}")
print("=" * 80)

# =================================================================================
# SECTION 7: DATA EXPORT TO FOLDER
# =================================================================================

# Save original data
original_path = os.path.join(simulation_folder, "original_data.csv")
np.savetxt(original_path, np.column_stack((time, powers)), 
           delimiter=",", header="time_s,power_W", comments="")

# Save P-only stabilized data
p_only_path = os.path.join(simulation_folder, "stabilized_P_only.csv")
np.savetxt(p_only_path, np.column_stack((time, stab_p)), 
           delimiter=",", header="time_s,power_W", comments="")

# Save PI stabilized data
pi_path = os.path.join(simulation_folder, "stabilized_PI.csv")
np.savetxt(pi_path, np.column_stack((time, stab_pi)), 
           delimiter=",", header="time_s,power_W", comments="")

# Save PID stabilized data
pid_path = os.path.join(simulation_folder, "stabilized_PID.csv")
np.savetxt(pid_path, np.column_stack((time, stab_pid)), 
           delimiter=",", header="time_s,power_W", comments="")

print("\nData exported to CSV files:")
print(f"  - {original_path}")
print(f"  - {p_only_path}")
print(f"  - {pi_path}")
print(f"  - {pid_path}")

# =================================================================================
# SECTION 8: VISUALIZATION
# =================================================================================

# Convert to milliwatts for plotting.
original_mw = powers * 1e3
stab_p_mw = stab_p * 1e3
stab_pi_mw = stab_pi * 1e3
stab_pid_mw = stab_pid * 1e3

# Calculate Y-axis limits from original data for consistent scaling.
ymin = np.min(original_mw)
ymax = np.max(original_mw)
padding = (ymax - ymin) * 0.05
ymin -= padding
ymax += padding

# Create figure with four subplots (original + 3 controllers).
plt.figure(figsize=(12, 10))

# Subplot 1: Original (free-running) data.
plt.subplot(4, 1, 1)
plt.plot(time, original_mw, 'b-', alpha=0.7, label='Original (free-running)', linewidth=1)
plt.axhline(y=setpoint*1e3, color='g', linestyle='--', alpha=0.5, label=f'Setpoint: {setpoint*1e3:.2f} mW')
plt.ylabel('Power (mW)')
plt.title('PID Family Controller Comparison (same y-scale, mild gains for illustration)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.ylim(ymin, ymax)

# Subplot 2: P-Only stabilized data.
plt.subplot(4, 1, 2)
plt.plot(time, stab_p_mw, 'r-', alpha=0.8, label=f'P-Only (Kp={kp}) | σ = {p_std*1e6:.1f} µW | RSD = {p_rsd:.3f}%', linewidth=1.5)
plt.axhline(y=setpoint*1e3, color='g', linestyle='--', alpha=0.5)
plt.ylabel('Power (mW)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.ylim(ymin, ymax)

# Subplot 3: PI stabilized data.
plt.subplot(4, 1, 3)
plt.plot(time, stab_pi_mw, 'orange', alpha=0.8, label=f'PI (Kp={kp}, Ki={ki}) | σ = {pi_std*1e6:.1f} µW | RSD = {pi_rsd:.3f}%', linewidth=1.5)
plt.axhline(y=setpoint*1e3, color='g', linestyle='--', alpha=0.5)
plt.ylabel('Power (mW)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.ylim(ymin, ymax)

# Subplot 4: Full PID stabilized data.
plt.subplot(4, 1, 4)
plt.plot(time, stab_pid_mw, 'green', alpha=0.8, label=f'PID (Kp={kp}, Ki={ki}, Kd={kd}) | σ = {pid_std*1e6:.1f} µW | RSD = {pid_rsd:.3f}%', linewidth=1.5)
plt.axhline(y=setpoint*1e3, color='g', linestyle='--', alpha=0.5)
plt.ylabel('Power (mW)')
plt.xlabel('Time (seconds)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.ylim(ymin, ymax)

plt.tight_layout()

# Save the figure to the simulation folder
figure_path = os.path.join(simulation_folder, 'pid_family_comparison.png')
plt.savefig(figure_path, dpi=150, bbox_inches='tight')
plt.show()

print("\n" + "=" * 80)
print("SIMULATION COMPLETED SUCCESSFULLY")
print("=" * 80)
print(f"\nOutput files saved to: {simulation_folder}")
print("  - original_data.csv")
print("  - stabilized_P_only.csv")
print("  - stabilized_PI.csv")
print("  - stabilized_PID.csv")
print("  - pid_family_comparison.png")
print("=" * 80)