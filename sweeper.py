import sys
import time
import os
import csv
import numpy as np
from datetime import datetime
from collections import deque
import threading

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog
from PyQt5.QtCore import QTimer

# 5 dBm - Higher power (~6.2 mW)
# 2 dBm - Medium power (~1.55 mW)
# 0 dBm - Low power (~0.58 mW)
# -2 dBm - Very low power (~0.216 mW)
# -5 dBm - Lowest power (~0.05 mW)

PID_CONFIGS = {
    5: [  # 5 dBm - Higher power (~6.2 mW)
        (0.1, 0, 0, "P-only: Very Low"),
        (0.3, 0, 0, "P-only: Low"),
        (0.5, 0, 0, "P-only: Medium"),
        (0.8, 0, 0, "P-only: High"),
        (1.0, 0, 0, "P-only: Aggressive"),
        (0.2, 0.05, 0, "PI-only: Conservative"),
        (0.3, 0.08, 0, "PI-only: Low"),
        (0.4, 0.12, 0, "PI-only: Medium"),
        (0.5, 0.18, 0, "PI-only: High"),
        (0.6, 0.25, 0, "PI-only: Aggressive"),
        (0.2, 0.04, 0.02, "PID: Conservative"),
        (0.35, 0.08, 0.04, "PID: Low"),
        (0.5, 0.12, 0.06, "PID: Medium"),
        (0.65, 0.16, 0.08, "PID: High"),
        (0.8, 0.2, 0.1, "PID: Aggressive")
    ],
    
    2: [  # 2 dBm - Medium power (~1.55 mW)
        (0.08, 0, 0, "P-only: Very Low"),
        (0.25, 0, 0, "P-only: Low"),
        (0.4, 0, 0, "P-only: Medium"),
        (0.6, 0, 0, "P-only: High"),
        (0.8, 0, 0, "P-only: Aggressive"),
        (0.15, 0.03, 0, "PI-only: Conservative"),
        (0.25, 0.06, 0, "PI-only: Low"),
        (0.35, 0.1, 0, "PI-only: Medium"),
        (0.45, 0.14, 0, "PI-only: High"),
        (0.55, 0.2, 0, "PI-only: Aggressive"),
        (0.15, 0.03, 0.012, "PID: Conservative"),
        (0.28, 0.06, 0.025, "PID: Low"),
        (0.4, 0.1, 0.04, "PID: Medium"),
        (0.52, 0.14, 0.055, "PID: High"),
        (0.65, 0.18, 0.07, "PID: Aggressive")
    ],
    
    0: [  # 0 dBm - Low power (~0.58 mW)
        (0.05, 0, 0, "P-only: Very Low"),
        (0.18, 0, 0, "P-only: Low"),
        (0.3, 0, 0, "P-only: Medium"),
        (0.45, 0, 0, "P-only: High"),
        (0.6, 0, 0, "P-only: Aggressive"),
        (0.1, 0.02, 0, "PI-only: Conservative"),
        (0.18, 0.04, 0, "PI-only: Low"),
        (0.25, 0.07, 0, "PI-only: Medium"),
        (0.35, 0.1, 0, "PI-only: High"),
        (0.45, 0.15, 0, "PI-only: Aggressive"),
        (0.1, 0.02, 0.008, "PID: Conservative"),
        (0.2, 0.04, 0.015, "PID: Low"),
        (0.3, 0.07, 0.025, "PID: Medium"),
        (0.4, 0.1, 0.035, "PID: High"),
        (0.5, 0.13, 0.045, "PID: Aggressive")
    ],
    
    -2: [  # -2 dBm - Very low power (~0.216 mW)
        (0.03, 0, 0, "P-only: Very Low"),
        (0.12, 0, 0, "P-only: Low"),
        (0.22, 0, 0, "P-only: Medium"),
        (0.35, 0, 0, "P-only: High"),
        (0.5, 0, 0, "P-only: Aggressive"),
        (0.08, 0.01, 0, "PI-only: Conservative"),
        (0.14, 0.025, 0, "PI-only: Low"),
        (0.2, 0.04, 0, "PI-only: Medium"),
        (0.28, 0.06, 0, "PI-only: High"),
        (0.38, 0.08, 0, "PI-only: Aggressive"),
        (0.08, 0.01, 0.005, "PID: Conservative"),
        (0.15, 0.025, 0.01, "PID: Low"),
        (0.22, 0.04, 0.015, "PID: Medium"),
        (0.3, 0.055, 0.02, "PID: High"),
        (0.4, 0.07, 0.025, "PID: Aggressive")
    ],
    
    -5: [  # -5 dBm - Lowest power (~0.05 mW)
        (0.02, 0, 0, "P-only: Very Low"),
        (0.08, 0, 0, "P-only: Low"),
        (0.15, 0, 0, "P-only: Medium"),
        (0.25, 0, 0, "P-only: High"),
        (0.38, 0, 0, "P-only: Aggressive"),
        (0.05, 0.008, 0, "PI-only: Conservative"),
        (0.1, 0.015, 0, "PI-only: Low"),
        (0.16, 0.025, 0, "PI-only: Medium"),
        (0.22, 0.04, 0, "PI-only: High"),
        (0.3, 0.055, 0, "PI-only: Aggressive"),
        (0.05, 0.008, 0.003, "PID: Conservative"),
        (0.1, 0.015, 0.006, "PID: Low"),
        (0.16, 0.025, 0.01, "PID: Medium"),
        (0.22, 0.04, 0.015, "PID: High"),
        (0.3, 0.055, 0.02, "PID: Aggressive")
    ]
}

RECORDING_DURATION = 300  # (seconds)

SAMPLING_RATES = [1, 2, 5, 10, 20] # (Hz)


class MultiRateDataRecorder:
    """Recorder that saves data at multiple sampling rates simultaneously"""
    
    def __init__(self, sampling_rates):
        self.sampling_rates = sampling_rates
        self.buffers = {rate: [] for rate in sampling_rates}
        self.last_sample_time = {rate: 0 for rate in sampling_rates}
        self.filename = None
        self.start_time = None
        self.is_recording = False
        self.pid_configs = []
        
    def start_recording(self, filename, pid_configs):
        self.filename = filename
        self.pid_configs = pid_configs
        for rate in self.sampling_rates:
            self.buffers[rate] = []
            self.last_sample_time[rate] = 0
        self.start_time = time.time()
        self.is_recording = True
        print(f"  Recording to: {os.path.basename(filename)}")
        print(f"  Sampling rates: {self.sampling_rates} Hz")
        
    def add_data_point(self, timestamp, raw_power, controlled_powers_dict):
        if not self.is_recording:
            return
        
        for rate in self.sampling_rates:
            interval = 1.0 / rate
            if self.last_sample_time[rate] == 0:
                self.last_sample_time[rate] = timestamp
                self.buffers[rate].append({
                    'timestamp': timestamp,
                    'raw_power_mw': raw_power,
                    'controlled_powers': controlled_powers_dict.copy()
                })
            elif timestamp - self.last_sample_time[rate] >= interval:
                self.last_sample_time[rate] = timestamp
                self.buffers[rate].append({
                    'timestamp': timestamp,
                    'raw_power_mw': raw_power,
                    'controlled_powers': controlled_powers_dict.copy()
                })
    
    def stop_recording(self):
        self.is_recording = False
        
        saved_files = []
        for rate in self.sampling_rates:
            if len(self.buffers[rate]) == 0:
                print(f"  No data for {rate}Hz")
                continue
                
            rate_filename = self.filename.replace('.csv', f'_{rate}Hz.csv')
            
            try:
                with open(rate_filename, 'w', newline='') as csvfile:
                    header = ['Time (s)', 'Raw Power (mW)']
                    for set_id, name, Kp, Ki, Kd in self.pid_configs:
                        header.append(f'Controlled Power ({name})')
                    writer = csv.writer(csvfile)
                    writer.writerow(header)
                    
                    for point in self.buffers[rate]:
                        row = [f"{point['timestamp']:.3f}", f"{point['raw_power_mw']:.6f}"]
                        for set_id, name, Kp, Ki, Kd in self.pid_configs:
                            controlled = point['controlled_powers'].get(set_id, 0)
                            row.append(f"{controlled:.6f}")
                        writer.writerow(row)
                
                print(f"  ✓ Saved {rate}Hz: {os.path.basename(rate_filename)} ({len(self.buffers[rate])} points)")
                saved_files.append(rate_filename)
                
            except Exception as e:
                print(f"  Error saving {rate}Hz file: {e}")
        
        return saved_files
    
    def get_statistics(self):
        stats = {}
        for rate in self.sampling_rates:
            if len(self.buffers[rate]) == 0:
                continue
                
            raw_powers = [p['raw_power_mw'] for p in self.buffers[rate]]
            stats[rate] = {
                'raw': {
                    'mean': np.mean(raw_powers),
                    'std': np.std(raw_powers),
                    'rsd': (np.std(raw_powers) / np.mean(raw_powers) * 100) if np.mean(raw_powers) > 0 else 0,
                },
                'controlled': {}
            }
            
            controlled_by_set = {}
            for point in self.buffers[rate]:
                for set_id, power in point['controlled_powers'].items():
                    if set_id not in controlled_by_set:
                        controlled_by_set[set_id] = []
                    controlled_by_set[set_id].append(power)
            
            for set_id, powers in controlled_by_set.items():
                stats[rate]['controlled'][set_id] = {
                    'mean': np.mean(powers),
                    'std': np.std(powers),
                    'rsd': (np.std(powers) / np.mean(powers) * 100) if np.mean(powers) > 0 else 0,
                }
        
        return stats



class AutomatedPIDSweep:
    def __init__(self):
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)
        
        self.main_window = None
        self.widget = None
        self.t1_tab = None
        self.recorder = MultiRateDataRecorder(SAMPLING_RATES)
        self.is_recording = False
        self.recording_duration = RECORDING_DURATION
        self.data_collection_timer = None
        self.results_dir = None  
        
        self.dBm_values = [5, 2, 0, -2, -5]
        
        self.current_dBm_index = 0
        self.pid_set_ids = []
        self.pid_configs_for_recorder = []
        
        print(f"Total dBm values to test: {len(self.dBm_values)}")
        print(f"Recording duration per dBm: {self.recording_duration / 60:.1f} minutes")
        print(f"Sampling rates: {SAMPLING_RATES} Hz")
        
    def get_pid_configs_for_dBm(self, dBm):
        return PID_CONFIGS.get(dBm, PID_CONFIGS[5])
    
    def setup_multi_pid_sets(self, pid_configs):
        """Setup all PID sets in the GUI - Updated for new GUI structure"""
        multi_pid = self.widget.multi_pid
        
        current_sets = list(multi_pid.pids.keys())
        for set_id in current_sets:
            multi_pid.remove_pid(set_id)
        
        self.widget.controlled_power_sets.clear()
        
        self.widget.pid_set_combo.blockSignals(True)
        self.widget.pid_set_combo.clear()
        
        self.pid_set_ids = []
        self.pid_configs_for_recorder = []
        
        for i, (Kp, Ki, Kd, name) in enumerate(pid_configs):
            set_id = multi_pid.add_pid(Kp, Ki, Kd, name)
            self.pid_set_ids.append(set_id)
            self.widget.controlled_power_sets[set_id] = deque(maxlen=10000)
            self.pid_configs_for_recorder.append((set_id, name, Kp, Ki, Kd))
            self.widget.pid_set_combo.addItem(name)
        
        if len(self.pid_set_ids) > 0:
            self.widget.pid_set_combo.setCurrentIndex(0)
            self.widget.current_pid_set_id = self.pid_set_ids[0]
            
            self.widget.kp_slider.blockSignals(True)
            self.widget.ki_slider.blockSignals(True)
            self.widget.kd_slider.blockSignals(True)
            self.widget.kp_spin.blockSignals(True)
            self.widget.ki_spin.blockSignals(True)
            self.widget.kd_spin.blockSignals(True)
            
            first_config = pid_configs[0]
            self.widget.kp_slider.setValue(int(first_config[0] * 100))
            self.widget.ki_slider.setValue(int(first_config[1] * 100))
            self.widget.kd_slider.setValue(int(first_config[2] * 100))
            self.widget.kp_spin.setValue(first_config[0])
            self.widget.ki_spin.setValue(first_config[1])
            self.widget.kd_spin.setValue(first_config[2])
            self.widget.kp_value_label.setText(f"{first_config[0]:.3f}")
            self.widget.ki_value_label.setText(f"{first_config[1]:.3f}")
            self.widget.kd_value_label.setText(f"{first_config[2]:.3f}")
            
            self.widget.kp_slider.blockSignals(False)
            self.widget.ki_slider.blockSignals(False)
            self.widget.kd_slider.blockSignals(False)
            self.widget.kp_spin.blockSignals(False)
            self.widget.ki_spin.blockSignals(False)
            self.widget.kd_spin.blockSignals(False)
        
        self.widget.pid_set_combo.blockSignals(False)
        
        print(f"  ✓ Setup {len(self.pid_set_ids)} PID sets")
    
    def set_mw_power(self, dBm):
        """Set microwave source power"""
        try:
            if self.t1_tab is not None:
                self.t1_tab.mw_power_input.setText(str(dBm))
                self.t1_tab.mw_set_btn.click()
                self.t1_tab.mw_on_btn.click()
                print(f"  ✓ MW Power set to {dBm} dBm")
                time.sleep(0.5)
                return True
            return False
        except Exception as e:
            print(f"  ✗ Failed to set MW power: {e}")
            return False
    
    def turn_mw_off(self):
        """Turn off microwave source"""
        try:
            if self.t1_tab is not None:
                self.t1_tab.mw_off_btn.click()
                print("  ✓ MW turned OFF")
                return True
            return False
        except Exception as e:
            print(f"  ✗ Failed to turn OFF MW: {e}")
            return False
    
    def run(self):
        print("\n" + "="*80)
        print("AUTOMATED PID PARAMETER SWEEP")
        print("="*80)
        
        print("\nPlease select a folder to save the sweep results...")
        save_dir = QFileDialog.getExistingDirectory(None, "Select Save Directory", 
                                                     os.path.expanduser("~"),
                                                     QFileDialog.ShowDirsOnly)
        
        if not save_dir:
            print("No directory selected. Using current directory.")
            save_dir = os.getcwd()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results_dir = os.path.join(save_dir, f"pid_sweep_{timestamp}")
        os.makedirs(self.results_dir, exist_ok=True)
        
        print(f"\n📁 Results will be saved to:")
        print(f"   {self.results_dir}")
        print("="*80)
        
        print(f"Each dBm runs ALL {len(PID_CONFIGS[5])} PID sets SIMULTANEOUSLY")
        print(f"Recording duration per dBm: {self.recording_duration / 60:.1f} minutes")
        print(f"Recording at multiple rates: {SAMPLING_RATES} Hz")
        print(f"Total time: {len(self.dBm_values) * self.recording_duration / 60:.1f} minutes")
        print("="*80)
        
        if not TLPMX_AVAILABLE:
            print("ERROR: TLPMX not available.")
            return
        
        from laser_control_gui_0415 import UnifiedLaserControlGUI
        
        self.main_window = UnifiedLaserControlGUI()
        self.main_window.setWindowTitle("Automated PID Sweep - DO NOT CLOSE")
        self.main_window.show()
        
        self.widget = self.main_window.laser_control
        self.t1_tab = self.main_window.t1_measurement
        
        print("\nConnecting to Thorlabs...")
        self.widget.connect_thorlabs()
        
        timeout = 30
        start = time.time()
        while not self.widget.is_connected and (time.time() - start) < timeout:
            self.app.processEvents()
            time.sleep(0.1)
        
        if not self.widget.is_connected:
            print("Failed to connect")
            QMessageBox.critical(None, "Error", "Could not connect to Thorlabs")
            return
        
        print("Connected!")
        self.widget.source_combo.setCurrentText('Thorlabs Live')
        
        self.summary_file = os.path.join(self.results_dir, "master_summary.csv")
        with open(self.summary_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['dBm', 'PID_Set', 'Kp', 'Ki', 'Kd', 
                           'Sampling_Rate_Hz', 'Points', 'Duration_s',
                           'Raw_Mean_mW', 'Raw_Std_mW', 'Raw_RSD_%',
                           'Controlled_Mean_mW', 'Controlled_Std_mW', 'Controlled_RSD_%'])
        
        self.run_next_dBm()
        
        sys.exit(self.app.exec_())
    
    def run_next_dBm(self):
        """Run all PID configurations for the current dBm value"""
        if self.current_dBm_index >= len(self.dBm_values):
            self.finish()
            return
        
        dBm = self.dBm_values[self.current_dBm_index]
        pid_configs = self.get_pid_configs_for_dBm(dBm)
        
        print("\n" + "="*80)
        print(f"Testing dBm = {dBm}")
        print(f"Running ALL {len(pid_configs)} PID sets SIMULTANEOUSLY")
        print(f"Recording for {self.recording_duration / 60:.1f} minutes")
        print("="*80)
        
        print(f"Setting MW power to {dBm} dBm...")
        self.set_mw_power(dBm)
        time.sleep(2)
        
        self.setup_multi_pid_sets(pid_configs)
        
        self.widget.reset_plot()
        self.widget.live_stats.reset()
        
        print(f"  Waiting for stabilization (5 seconds)...")
        self.app.processEvents()
        time.sleep(5)
        
        dBm_str = f"dBm{dBm}".replace('-', 'minus')
        filename = f"pid_sweep_{dBm_str}.csv"
        filepath = os.path.join(self.results_dir, filename)
        
        self.recorder.start_recording(filepath, self.pid_configs_for_recorder)
        self.is_recording = True
        self.recording_start_time = time.time()
        self._last_progress_min = 0
        
        print(f"  Recording for {self.recording_duration / 60:.1f} minutes...")
        print(f"  Data will be saved at {SAMPLING_RATES} Hz")
        
        self.data_collection_timer = QTimer()
        self.data_collection_timer.timeout.connect(self.collect_data_point)
        self.data_collection_timer.start(50)  # 20 Hz
        
        QTimer.singleShot(int(self.recording_duration * 1000), self.stop_and_save)
    
    def collect_data_point(self):
        """Collect a single data point (20 Hz internal)"""
        if self.is_recording and self.widget.is_connected:
            raw_power = self.widget.latest_thorlabs_power
            
            if raw_power is not None and raw_power > 0:
                elapsed = time.time() - self.recording_start_time
                
                if len(self.widget.raw_powers) >= 10:
                    recent_raw = list(self.widget.raw_powers)[-50:] if len(self.widget.raw_powers) >= 50 else list(self.widget.raw_powers)
                    running_avg = np.mean(recent_raw)
                else:
                    running_avg = raw_power
                
                if hasattr(self.widget, 'multi_pid') and len(self.widget.multi_pid.get_all_pids()) > 0:
                    pid_results = self.widget.multi_pid.update_all(running_avg, raw_power)
                    
                    controlled_powers = {}
                    for set_id, result in pid_results.items():
                        controlled_powers[set_id] = result['controlled_power']
                        if set_id not in self.widget.controlled_power_sets:
                            self.widget.controlled_power_sets[set_id] = deque(maxlen=10000)
                        self.widget.controlled_power_sets[set_id].append(result['controlled_power'])
                    
                    if hasattr(self.widget, 'live_stats'):
                        self.widget.live_stats.update_reading(raw_power)
                    
                    self.recorder.add_data_point(elapsed, raw_power, controlled_powers)
                
                current_minute = int(elapsed / 60)
                if current_minute > self._last_progress_min:
                    print(f"    Recording... {current_minute} min / {self.recording_duration / 60:.0f} min")
                    self._last_progress_min = current_minute
    
    def stop_and_save(self):
        """Stop recording and save data"""
        if self.data_collection_timer:
            self.data_collection_timer.stop()
        
        self.is_recording = False
        saved_files = self.recorder.stop_recording()
        
        stats = self.recorder.get_statistics()
        
        dBm = self.dBm_values[self.current_dBm_index]
        
        for rate, rate_stats in stats.items():
            raw_stats = rate_stats.get('raw', {'mean': 0, 'std': 0, 'rsd': 0})
            controlled_stats = rate_stats.get('controlled', {})
            
            for set_id, cstats in controlled_stats.items():
                set_name = "Unknown"
                Kp = Ki = Kd = 0
                for sid, sname, skp, ski, skd in self.pid_configs_for_recorder:
                    if sid == set_id:
                        set_name = sname
                        Kp, Ki, Kd = skp, ski, skd
                        break
                
                with open(self.summary_file, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        dBm, set_name, Kp, Ki, Kd, rate,
                        len(self.recorder.buffers[rate]),
                        self.recording_duration,
                        f"{raw_stats['mean']:.6f}", f"{raw_stats['std']:.6f}", f"{raw_stats['rsd']:.3f}",
                        f"{cstats['mean']:.6f}", f"{cstats['std']:.6f}", f"{cstats['rsd']:.3f}"
                    ])
        
        if saved_files:
            print(f"\n  ✓ Saved {len(saved_files)} files for dBm={dBm}")
            for f in saved_files:
                print(f"      {os.path.basename(f)}")
        
        self.current_dBm_index += 1
        QTimer.singleShot(2000, self.run_next_dBm)
    
    def finish(self):
        """Finish the sweep and generate report"""
        print("\n  Turning off MW source...")
        self.turn_mw_off()
        
        print("\n" + "="*60)
        print("PID SWEEP COMPLETE!")
        print(f"📁 Results saved to: {self.results_dir}")
        print("="*60)
        
        try:
            os.startfile(self.results_dir)
        except:
            pass
        
        self.generate_report()
        
        QMessageBox.information(None, "Sweep Complete", 
            f"PID sweep complete!\n\n"
            f"📁 Results saved to:\n{self.results_dir}\n\n"
            f"dBm values tested: {self.dBm_values}\n"
            f"PID configs per dBm: {len(PID_CONFIGS[5])}\n"
            f"Sampling rates: {SAMPLING_RATES} Hz\n"
            f"Recording duration per dBm: {self.recording_duration / 60:.1f} minutes\n\n"
            f"The folder will open automatically.")
        
        QTimer.singleShot(5000, self.app.quit)
    
    def generate_report(self):
        """Generate a detailed report"""
        report_file = os.path.join(self.results_dir, "sweep_report.txt")
        
        try:
            import pandas as pd
            df = pd.read_csv(self.summary_file)
            
            with open(report_file, 'w') as f:
                f.write("="*80 + "\n")
                f.write("PID PARAMETER SWEEP REPORT\n")
                f.write("="*80 + "\n\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Results Folder: {self.results_dir}\n")
                f.write(f"Recording duration per dBm: {self.recording_duration / 60:.1f} minutes\n")
                f.write(f"Sampling rates: {SAMPLING_RATES} Hz\n\n")
                
                f.write("dBm VALUES TESTED:\n")
                for dBm in self.dBm_values:
                    f.write(f"  {dBm} dBm\n")
                f.write("\n")
                
                f.write("BEST PID SET FOR EACH dBm VALUE (by Controlled RSD):\n")
                f.write("-"*80 + "\n")
                
                for dBm in self.dBm_values:
                    f.write(f"\n  {dBm} dBm:\n")
                    for rate in SAMPLING_RATES:
                        subset = df[(df['dBm'] == dBm) & (df['Sampling_Rate_Hz'] == rate)]
                        if len(subset) > 0:
                            valid = subset[subset['Controlled_RSD_%'].notna()]
                            if len(valid) > 0:
                                best = valid.loc[valid['Controlled_RSD_%'].idxmin()]
                                f.write(f"    {rate}Hz: {best['PID_Set']} -> "
                                       f"Kp={best['Kp']}, Ki={best['Ki']}, Kd={best['Kd']} -> "
                                       f"RSD={best['Controlled_RSD_%']:.3f}%\n")
                
                f.write("\n\nBEST AT 20Hz SAMPLING RATE:\n")
                f.write("-"*80 + "\n")
                
                for dBm in self.dBm_values:
                    subset = df[(df['dBm'] == dBm) & (df['Sampling_Rate_Hz'] == 20)]
                    
                    p_only = subset[(subset['Ki'] == 0) & (subset['Kd'] == 0)]
                    if len(p_only) > 0:
                        best_p = p_only.loc[p_only['Controlled_RSD_%'].idxmin()]
                        f.write(f"  {dBm} dBm - Best P-only: {best_p['PID_Set']} (Kp={best_p['Kp']}) -> RSD={best_p['Controlled_RSD_%']:.3f}%\n")
                    
                    pi_only = subset[(subset['Kd'] == 0) & (subset['Ki'] > 0)]
                    if len(pi_only) > 0:
                        best_pi = pi_only.loc[pi_only['Controlled_RSD_%'].idxmin()]
                        f.write(f"  {dBm} dBm - Best PI-only: {best_pi['PID_Set']} (Kp={best_pi['Kp']}, Ki={best_pi['Ki']}) -> RSD={best_pi['Controlled_RSD_%']:.3f}%\n")
                    
                    full_pid = subset[subset['Kd'] > 0]
                    if len(full_pid) > 0:
                        best_pid = full_pid.loc[full_pid['Controlled_RSD_%'].idxmin()]
                        f.write(f"  {dBm} dBm - Best Full PID: {best_pid['PID_Set']} (Kp={best_pid['Kp']}, Ki={best_pid['Ki']}, Kd={best_pid['Kd']}) -> RSD={best_pid['Controlled_RSD_%']:.3f}%\n")
                
                f.write("\n\nOVERALL BEST ACROSS ALL dBm VALUES (20Hz):\n")
                f.write("-"*80 + "\n")
                all_20hz = df[df['Sampling_Rate_Hz'] == 20]
                if len(all_20hz) > 0:
                    best_overall = all_20hz.loc[all_20hz['Controlled_RSD_%'].idxmin()]
                    f.write(f"  Best Overall: {best_overall['dBm']} dBm - {best_overall['PID_Set']} -> "
                           f"Kp={best_overall['Kp']}, Ki={best_overall['Ki']}, Kd={best_overall['Kd']} -> "
                           f"RSD={best_overall['Controlled_RSD_%']:.3f}%\n")
                
            print(f"📄 Report saved: {report_file}")
            
        except Exception as e:
            print(f"Could not generate report: {e}")


from laser_control_gui import UnifiedLaserControlGUI, TLPMX_AVAILABLE


if __name__ == '__main__':
    sweeper = AutomatedPIDSweep()
    sweeper.run()