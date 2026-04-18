import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal, QDateTime
from datetime import datetime
from ctypes import c_long, c_ulong, c_uint32, byref, create_string_buffer, c_bool, c_char_p, c_int, c_int16, c_double
import time
import warnings
import os
import csv
from collections import deque

sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), "../..")))

try:
    from Hardwares.Swabian_PulseStreamer import PulseGenerator
    PULSE_GEN_AVAILABLE = True
except ImportError:
    PULSE_GEN_AVAILABLE = False
    print("Warning: PulseGenerator not available")

try:
    from Hardwares.SynthNV_Pro_MicrowaveSource import SynthNV_Pro_MicrowaveSource
    MW_SOURCE_AVAILABLE = True
except ImportError:
    MW_SOURCE_AVAILABLE = False
    print("Warning: Microwave source not available")

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from TLPMX import TLPMX, TLPM_DEFAULT_CHANNEL
    TLPMX_AVAILABLE = True
    print("✓ TLPMX module loaded successfully")
except ImportError as e:
    print(f"Warning: TLPMX not available - {e}")
    TLPMX_AVAILABLE = False

warnings.filterwarnings('ignore')

PID_COLORS = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
    '#1a9850', '#fdae61', '#d73027', '#4575b4', '#f46d43',
    '#74add1', '#a6d96a', '#fdae61', '#fee090', '#e0f3f8'
]


class ThorlabsWorker(QThread):
    power_updated = pyqtSignal(float, float)
    error_occurred = pyqtSignal(str)
    connected = pyqtSignal(bool)
    
    def __init__(self):
        super().__init__()
        self.is_running = False
        self.meter = None
        self.is_connected_flag = False
        self.wavelength_nm = 532.5
        self.sampling_period_ms = 50
        
    def connect_meter(self):
        if not TLPMX_AVAILABLE:
            self.error_occurred.emit("TLPMX module not available.")
            self.connected.emit(False)
            return False
            
        try:
            self.meter = RealThorlabsPowerMeter()
            if self.meter.connect():
                self.meter.set_wavelength(self.wavelength_nm)
                self.is_connected_flag = True
                self.connected.emit(True)
                return True
            else:
                self.connected.emit(False)
                return False
        except Exception as e:
            self.error_occurred.emit(f"Connection failed: {str(e)}")
            self.connected.emit(False)
            return False
    
    def disconnect_meter(self):
        self.is_running = False
        if self.meter:
            self.meter.disconnect()
            self.meter = None
        self.is_connected_flag = False
    
    def set_wavelength(self, wavelength_nm):
        self.wavelength_nm = wavelength_nm
        if self.meter and self.is_connected_flag:
            return self.meter.set_wavelength(wavelength_nm)
        return False
    
    def set_sampling_period(self, period_ms):
        self.sampling_period_ms = max(10, min(1000, period_ms))
    
    def run(self):
        self.is_running = True
        while self.is_running:
            if self.meter and self.is_connected_flag:
                try:
                    power = self.meter.read_power_mw()
                    if power is not None and power > 0:
                        current_time = time.time()
                        self.power_updated.emit(power, current_time)
                except Exception as e:
                    print(f"Read error: {e}")
            self.msleep(int(self.sampling_period_ms))
    
    def stop(self):
        self.is_running = False
        self.wait(2000)



class RealThorlabsPowerMeter:
    def __init__(self):
        self.tlPM = None
        self.resource_name = None
        self.is_connected = False
        self.wavelength_nm = 532.5
        
    def connect(self):
        if not TLPMX_AVAILABLE:
            return False
        try:
            self.tlPM = TLPMX()
            deviceCount = c_uint32()
            self.tlPM.findRsrc(byref(deviceCount))
            if deviceCount.value == 0:
                return False
            resourceName = create_string_buffer(1024)
            self.tlPM.getRsrcName(c_int(0), resourceName)
            self.resource_name = c_char_p(resourceName.raw).value.decode('utf-8')
            self.tlPM.close()
            self.tlPM = TLPMX()
            self.tlPM.open(resourceName, c_bool(True), c_bool(True))
            message = create_string_buffer(1024)
            self.tlPM.getCalibrationMsg(message, TLPM_DEFAULT_CHANNEL)
            wavelength = c_double(self.wavelength_nm)
            self.tlPM.setWavelength(wavelength, TLPM_DEFAULT_CHANNEL)
            self.tlPM.setPowerAutoRange(c_int16(1), TLPM_DEFAULT_CHANNEL)
            self.tlPM.setPowerUnit(c_int16(0), TLPM_DEFAULT_CHANNEL)
            self.is_connected = True
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def read_power_mw(self):
        if not self.is_connected or self.tlPM is None:
            return None
        try:
            power = c_double()
            self.tlPM.measPower(byref(power), TLPM_DEFAULT_CHANNEL)
            return power.value * 1000
        except Exception as e:
            print(f"Read error: {e}")
            return None
    
    def set_wavelength(self, wavelength_nm):
        self.wavelength_nm = wavelength_nm
        if self.is_connected and self.tlPM:
            try:
                wavelength = c_double(wavelength_nm)
                self.tlPM.setWavelength(wavelength, TLPM_DEFAULT_CHANNEL)
                return True
            except:
                return False
        return False
    
    def disconnect(self):
        if self.tlPM:
            try:
                self.tlPM.close()
            except:
                pass
            self.tlPM = None
        self.is_connected = False



class DataSimulator:
    def __init__(self):
        self.data = {}
        self.current_dataset = '0 dBm'
        self.current_index = 0
        self.reset_flag = False
        self.current_controlled_cols = []
        
    def load_csv(self, filepath, name):
        try:
            import pandas as pd
            df = pd.read_csv(filepath)
            
            if 'Time (s)' in df.columns:
                times = df['Time (s)'].values
            elif 'Relative Time (s)' in df.columns:
                times = df['Relative Time (s)'].values
            else:
                times = np.arange(len(df)) * 0.1
            
            if 'Raw Power (mW)' in df.columns:
                raw_powers = df['Raw Power (mW)'].values
            else:
                raw_powers = None
            
            controlled_cols = [col for col in df.columns if 'Controlled' in col]
            
            if not controlled_cols:
                for col in df.columns:
                    if col not in ['Time (s)', 'Relative Time (s)', 'Raw Power (mW)', 'Timestamp']:
                        controlled_cols.append(col)
            
            controlled_powers = {}
            for col in controlled_cols:
                controlled_powers[col] = df[col].values
            
            if len(times) > 0 and times[0] != 0:
                times = times - times[0]
            
            self.data[name] = {
                'times': times,
                'raw_powers': raw_powers,
                'controlled_powers': controlled_powers,
                'controlled_cols': controlled_cols
            }
            
            print(f"Loaded {name}: {len(times)} points, {len(controlled_cols)} controlled outputs")
            return True
            
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            return False
    
    def generate_synthetic(self, name, mean_power, amplitude=0.5):
        t = np.arange(0, 120, 0.1)
        drift = 0.005 * t
        power = mean_power + amplitude * np.sin(2 * np.pi * 0.05 * t) + 0.2 * np.random.randn(len(t)) + drift
        self.data[name] = {
            'times': t,
            'raw_powers': power,
            'controlled_powers': {},
            'controlled_cols': []
        }
        return True
    
    def set_dataset(self, name):
        if name in self.data:
            self.current_dataset = name
            self.current_index = 0
            self.current_controlled_cols = self.data[name].get('controlled_cols', [])
            return True
        return False
    
    def reset(self):
        self.current_index = 0
        self.reset_flag = True
    
    def get_next(self):
        if self.current_dataset not in self.data:
            return 0, 88.0, {}
        
        data = self.data[self.current_dataset]
        times = data['times']
        raw_powers = data['raw_powers']
        
        if self.current_index >= len(times):
            self.current_index = 0
        
        t = times[self.current_index]
        raw_power = raw_powers[self.current_index] if raw_powers is not None else 88.0
        
        controlled = {}
        for col, powers in data['controlled_powers'].items():
            if self.current_index < len(powers):
                controlled[col] = powers[self.current_index]
        
        self.current_index += 1
        return t, raw_power, controlled
    
    def get_controlled_cols(self):
        return self.current_controlled_cols


class PIDController:
    def __init__(self, Kp=0.15, Ki=0.5, Kd=0.02, dt=0.05):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.dt = dt
        self.reset()
    
    def reset(self):
        self.integral = 0.0
        self.prev_error = 0.0
        self.prev_measurement = None
        self.output_limit = 10.0
        self.integral_limit = 20.0
    
    def update(self, setpoint, measurement, dt=None):
        if dt is not None and dt > 0:
            self.dt = dt
        
        error = setpoint - measurement
        P = self.Kp * error
        
        self.integral += error * self.dt
        self.integral = np.clip(self.integral, -self.integral_limit, self.integral_limit)
        I = self.Ki * self.integral
        
        if self.prev_measurement is not None and self.dt > 0:
            derivative = -(measurement - self.prev_measurement) / self.dt
            D = self.Kd * derivative
        else:
            D = 0.0
        
        output = P + I + D
        output = np.clip(output, -self.output_limit, self.output_limit)
        
        self.prev_error = error
        self.prev_measurement = measurement
        return output, error


class MultiPIDController:
    def __init__(self, dt=0.05):
        self.dt = dt
        self.pids = {}
        self.next_id = 0
        self.laser_sensitivity = 0.5
        self.last_update_time = None
        
    def add_pid(self, Kp=0.15, Ki=0.5, Kd=0.02, name=None):
        pid = PIDController(Kp, Ki, Kd, self.dt)
        set_id = self.next_id
        self.pids[set_id] = {
            'pid': pid,
            'name': name if name else f"Set {set_id + 1}",
            'Kp': Kp,
            'Ki': Ki,
            'Kd': Kd,
            'color': PID_COLORS[set_id % len(PID_COLORS)]
        }
        self.next_id += 1
        return set_id
    
    def remove_pid(self, set_id):
        if set_id in self.pids:
            del self.pids[set_id]
            return True
        return False
    
    def update_all(self, setpoint, measurement, dt=None):
        current_time = time.time()
        if dt is None:
            if self.last_update_time is None:
                dt = self.dt
            else:
                dt = current_time - self.last_update_time
                if dt <= 0 or dt > 1.0:
                    dt = self.dt
        
        self.last_update_time = current_time
        
        results = {}
        for set_id, data in self.pids.items():
            output, error = data['pid'].update(setpoint, measurement, dt)
            controlled_power = measurement + output * self.laser_sensitivity
            results[set_id] = {
                'output': output,
                'error': error,
                'controlled_power': controlled_power,
                'name': data['name'],
                'color': data['color'],
                'Kp': data['Kp'],
                'Ki': data['Ki'],
                'Kd': data['Kd']
            }
        return results
    
    def update_gains(self, set_id, Kp=None, Ki=None, Kd=None):
        if set_id in self.pids:
            if Kp is not None:
                self.pids[set_id]['Kp'] = Kp
                self.pids[set_id]['pid'].Kp = Kp
            if Ki is not None:
                self.pids[set_id]['Ki'] = Ki
                self.pids[set_id]['pid'].Ki = Ki
            if Kd is not None:
                self.pids[set_id]['Kd'] = Kd
                self.pids[set_id]['pid'].Kd = Kd
            return True
        return False
    
    def reset_all(self):
        self.last_update_time = None
        for data in self.pids.values():
            data['pid'].reset()
    
    def get_pid_count(self):
        return len(self.pids)
    
    def get_all_pids(self):
        return self.pids.copy()


class LiveStatisticsWidget(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Live Statistics", parent)
        self.current_min = float('inf')
        self.current_max = float('-inf')
        self.current_value = 0.0
        self.total_points = 0
        self.elapsed_seconds = 0
        self.raw_power_history = deque(maxlen=200)
        self.running_avg_raw = 88.2
        self.init_ui()
        
    def init_ui(self):
        layout = QGridLayout()
        layout.setSpacing(5)
        
        layout.addWidget(QLabel("Current Raw:"), 0, 0)
        self.current_label = QLabel("-- mW")
        self.current_label.setStyleSheet("font-size: 18px; font-weight: bold; color: blue;")
        layout.addWidget(self.current_label, 0, 1)
        
        layout.addWidget(QLabel("Running Avg:"), 1, 0)
        self.raw_avg_label = QLabel("-- mW")
        self.raw_avg_label.setStyleSheet("font-size: 12px; color: purple;")
        layout.addWidget(self.raw_avg_label, 1, 1)
        
        layout.addWidget(QLabel("Min/Max:"), 2, 0)
        self.min_max_label = QLabel("--/-- mW")
        self.min_max_label.setStyleSheet("font-size: 11px;")
        layout.addWidget(self.min_max_label, 2, 1)
        
        layout.addWidget(QLabel("PTP/RSD:"), 3, 0)
        self.ptp_rsd_label = QLabel("--/--%")
        self.ptp_rsd_label.setStyleSheet("font-size: 11px;")
        layout.addWidget(self.ptp_rsd_label, 3, 1)
        
        layout.addWidget(QLabel("Samples:"), 4, 0)
        self.samples_label = QLabel("0")
        layout.addWidget(self.samples_label, 4, 1)
        
        layout.addWidget(QLabel("Time:"), 5, 0)
        self.time_elapsed_label = QLabel("00:00:00")
        self.time_elapsed_label.setStyleSheet("font-size: 12px; font-weight: bold; color: darkblue;")
        layout.addWidget(self.time_elapsed_label, 5, 1)
        
        self.reset_btn = QPushButton("Reset Stats")
        self.reset_btn.clicked.connect(self.reset)
        layout.addWidget(self.reset_btn, 6, 0, 1, 2)
        
        self.setLayout(layout)
    
    def format_time_elapsed(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def update_time_elapsed(self, elapsed_seconds):
        self.elapsed_seconds = elapsed_seconds
        self.time_elapsed_label.setText(self.format_time_elapsed(elapsed_seconds))
    
    def update_reading(self, raw_power):
        self.current_value = raw_power
        self.current_label.setText(f"{raw_power:.3f} mW")
        
        if raw_power < self.current_min:
            self.current_min = raw_power
        if raw_power > self.current_max:
            self.current_max = raw_power
        self.min_max_label.setText(f"{self.current_min:.2f}/{self.current_max:.2f}")
        
        self.raw_power_history.append(raw_power)
        
        if len(self.raw_power_history) >= 5:
            recent = list(self.raw_power_history)[-50:] if len(self.raw_power_history) >= 50 else list(self.raw_power_history)
            mean_power = np.mean(recent)
            if mean_power > 0:
                std_power = np.std(recent)
                rsd = (std_power / mean_power) * 100
                ptp_val = max(recent) - min(recent)
                self.ptp_rsd_label.setText(f"{ptp_val:.2f}/{rsd:.2f}%")
                if rsd < 0.5:
                    self.ptp_rsd_label.setStyleSheet("font-size: 11px; color: green;")
                elif rsd < 1.0:
                    self.ptp_rsd_label.setStyleSheet("font-size: 11px; color: orange;")
                else:
                    self.ptp_rsd_label.setStyleSheet("font-size: 11px; color: red;")
        
        if len(self.raw_power_history) >= 10:
            recent_raw = list(self.raw_power_history)[-50:] if len(self.raw_power_history) >= 50 else list(self.raw_power_history)
            self.running_avg_raw = np.mean(recent_raw)
            self.raw_avg_label.setText(f"{self.running_avg_raw:.2f} mW")
        
        self.total_points += 1
        self.samples_label.setText(str(self.total_points))
    
    def reset(self):
        self.current_min = float('inf')
        self.current_max = float('-inf')
        self.current_value = 0.0
        self.total_points = 0
        self.elapsed_seconds = 0
        self.raw_power_history.clear()
        self.running_avg_raw = 88.2
        
        self.current_label.setText("-- mW")
        self.raw_avg_label.setText("-- mW")
        self.min_max_label.setText("--/--")
        self.ptp_rsd_label.setText("--/--%")
        self.samples_label.setText("0")
        self.time_elapsed_label.setText("00:00:00")


class T1MeasurementWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pb = None
        self.aom_mw = None
        self.init_hardware()
        self.init_ui()
    
    def init_hardware(self):
        if PULSE_GEN_AVAILABLE:
            try:
                self.pb = PulseGenerator()
                self.pb.setTrigger('internal_software')
                print("✓ PulseGenerator initialized")
            except:
                self.pb = None
        if MW_SOURCE_AVAILABLE:
            try:
                self.aom_mw = SynthNV_Pro_MicrowaveSource()
                print("✓ Microwave source initialized")
            except:
                self.aom_mw = None
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        status_group = QGroupBox("Hardware Status")
        status_layout = QGridLayout()
        self.pb_status_label = QLabel("⚫ Not Connected")
        if PULSE_GEN_AVAILABLE and self.pb:
            self.pb_status_label.setText("🟢 Connected")
        self.mw_status_label = QLabel("⚫ Not Connected")
        if MW_SOURCE_AVAILABLE and self.aom_mw:
            self.mw_status_label.setText("🟢 Connected")
        status_layout.addWidget(QLabel("Pulse Generator:"), 0, 0)
        status_layout.addWidget(self.pb_status_label, 0, 1)
        status_layout.addWidget(QLabel("MW Source:"), 1, 0)
        status_layout.addWidget(self.mw_status_label, 1, 1)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        pb_group = QGroupBox("Pulse Blaster")
        pb_layout = QVBoxLayout()
        pb_layout.addWidget(QLabel("Channels (; separated):"))
        self.pb_channels_input = QLineEdit()
        pb_layout.addWidget(self.pb_channels_input)
        pb_btn_layout = QHBoxLayout()
        self.pb_on_btn = QPushButton("ON")
        self.pb_on_btn.clicked.connect(self.pb_on)
        self.pb_off_btn = QPushButton("OFF")
        self.pb_off_btn.clicked.connect(self.pb_off)
        pb_btn_layout.addWidget(self.pb_on_btn)
        pb_btn_layout.addWidget(self.pb_off_btn)
        pb_layout.addLayout(pb_btn_layout)
        pb_group.setLayout(pb_layout)
        layout.addWidget(pb_group)
        
        mw_group = QGroupBox("MW Source")
        mw_layout = QGridLayout()
        mw_layout.addWidget(QLabel("Power (dBm):"), 0, 0)
        self.mw_power_input = QLineEdit()
        self.mw_power_input.setPlaceholderText("Max 10")
        mw_layout.addWidget(self.mw_power_input, 0, 1)
        self.mw_set_btn = QPushButton("SET")
        self.mw_set_btn.clicked.connect(self.pushButton_MW_set_Clicked)
        mw_layout.addWidget(self.mw_set_btn, 1, 0, 1, 2)
        mw_btn_layout = QHBoxLayout()
        self.mw_on_btn = QPushButton("ON")
        self.mw_on_btn.clicked.connect(self.pushButton_MW_on_Clicked)
        self.mw_off_btn = QPushButton("OFF")
        self.mw_off_btn.clicked.connect(self.pushButton_MW_off_Clicked)
        mw_btn_layout.addWidget(self.mw_on_btn)
        mw_btn_layout.addWidget(self.mw_off_btn)
        mw_layout.addLayout(mw_btn_layout, 2, 0, 1, 2)
        mw_group.setLayout(mw_layout)
        layout.addWidget(mw_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def pb_on(self):
        if self.pb:
            channels_str = self.pb_channels_input.text()
            channels = [int(ch) for ch in channels_str.replace('\n', '').split(';') if ch.strip()]
            self.pb.high(channels)
    
    def pb_off(self):
        if self.pb:
            self.pb.high([])
    
    def pushButton_MW_set_Clicked(self):
        if self.aom_mw:
            power = self.mw_power_input.text()
            if power and float(power) <= 10:
                self.aom_mw.Set(power)
                self.aom_mw.ON()
    
    def pushButton_MW_on_Clicked(self):
        if self.aom_mw:
            self.aom_mw.ON()
    
    def pushButton_MW_off_Clicked(self):
        if self.aom_mw:
            self.aom_mw.OFF()


class LaserControlWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.multi_pid = MultiPIDController(dt=0.05)
        self.simulator = DataSimulator()
        
        self.thorlabs_worker = None
        self.latest_thorlabs_power = 88.2
        self.plot_start_time = None
        
        self.times = deque(maxlen=500)
        self.raw_powers = deque(maxlen=500)
        self.controlled_power_sets = {}
        self.csv_controlled_histories = {}
        self.csv_controlled_colors = {}
        
        self.is_paused = False
        self.is_connected = False
        self.laser_sensitivity = 0.5
        self.sampling_period_ms = 50
        
        self.zoom_factor = 2.0
        self.wavelength_nm = 532.5
        self.mw_power_dbm = 0.0
        
        self.current_pid_set_id = 0
        self.current_kp = 0.15
        self.current_ki = 0.5
        self.current_kd = 0.02
        
        self.collection_start_time = None
        self.pause_start_time = None
        self.total_paused_time = 0.0
        self._last_pid_update_time = None
        
        self.multi_pid.add_pid(0.15, 0.5, 0.02, "PID Set 1")
        
        self.init_ui()
        self.load_default_data()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_loop)
        self.timer.start(self.sampling_period_ms)
    
    def init_ui(self):
        main_splitter = QSplitter(Qt.Horizontal)
        
        #Plot
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        self.figure = Figure(figsize=(8, 7), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.figure.set_tight_layout(True)
        
        self.ax1 = self.figure.add_subplot(211)
        self.ax2 = self.figure.add_subplot(212)
        
        left_layout.addWidget(self.canvas)
        main_splitter.addWidget(left_widget)
        
        #Controls
        right_widget = QScrollArea()
        right_widget.setWidgetResizable(True)
        right_widget.setMaximumWidth(580)
        right_widget.setMinimumWidth(450)
        
        controls_container = QWidget()
        controls_layout = QVBoxLayout(controls_container)
        controls_layout.setSpacing(8)
        controls_layout.setContentsMargins(10, 10, 10, 10)
        
        #TLPMX Status
        status_group = QGroupBox("TLPMX Status")
        status_layout = QVBoxLayout()
        self.tlpmx_status_label = QLabel("✓ LOADED" if TLPMX_AVAILABLE else "✗ NOT FOUND")
        self.tlpmx_status_label.setStyleSheet(f"color: {'green' if TLPMX_AVAILABLE else 'red'}; font-weight: bold;")
        status_layout.addWidget(self.tlpmx_status_label)
        status_group.setLayout(status_layout)
        controls_layout.addWidget(status_group)
        
        #Live Statistics
        self.live_stats = LiveStatisticsWidget()
        controls_layout.addWidget(self.live_stats)
        
        #Sampling Rate Controls
        sampling_group = QGroupBox("Sampling Rate")
        sampling_layout = QVBoxLayout()
        
        # Period control in miliseconds
        period_layout = QHBoxLayout()
        period_layout.addWidget(QLabel("Period (ms):"))
        self.period_slider = QSlider(Qt.Horizontal)
        self.period_slider.setRange(10, 1000)
        self.period_slider.setValue(50)
        self.period_slider.setTickPosition(QSlider.TicksBelow)
        self.period_slider.setTickInterval(100)
        self.period_slider.valueChanged.connect(self.on_period_slider_changed)
        period_layout.addWidget(self.period_slider)
        self.period_spin = QSpinBox()
        self.period_spin.setRange(10, 1000)
        self.period_spin.setValue(50)
        self.period_spin.setSuffix(" ms")
        self.period_spin.valueChanged.connect(self.on_period_spin_changed)
        period_layout.addWidget(self.period_spin)
        sampling_layout.addLayout(period_layout)
        
        # Frequency control in Hz
        freq_layout = QHBoxLayout()
        freq_layout.addWidget(QLabel("Frequency (Hz):"))
        self.freq_slider = QSlider(Qt.Horizontal)
        self.freq_slider.setRange(1, 100)
        self.freq_slider.setValue(20)
        self.freq_slider.setTickPosition(QSlider.TicksBelow)
        self.freq_slider.setTickInterval(10)
        self.freq_slider.valueChanged.connect(self.on_freq_slider_changed)
        freq_layout.addWidget(self.freq_slider)
        self.freq_spin = QSpinBox()
        self.freq_spin.setRange(1, 100)
        self.freq_spin.setValue(20)
        self.freq_spin.setSuffix(" Hz")
        self.freq_spin.valueChanged.connect(self.on_freq_spin_changed)
        freq_layout.addWidget(self.freq_spin)
        sampling_layout.addLayout(freq_layout)
        
        sampling_group.setLayout(sampling_layout)
        controls_layout.addWidget(sampling_group)
        
        #Wavelength Control
        wavelength_group = QGroupBox("Wavelength")
        wavelength_layout = QHBoxLayout()
        wavelength_layout.addWidget(QLabel("λ (nm):"))
        self.wavelength_slider = QSlider(Qt.Horizontal)
        self.wavelength_slider.setRange(400, 1700)
        self.wavelength_slider.setValue(532)
        self.wavelength_slider.setTickPosition(QSlider.TicksBelow)
        self.wavelength_slider.setTickInterval(100)
        self.wavelength_slider.valueChanged.connect(self.on_wavelength_slider_changed)
        wavelength_layout.addWidget(self.wavelength_slider)
        self.wavelength_spin = QSpinBox()
        self.wavelength_spin.setRange(400, 1700)
        self.wavelength_spin.setValue(532)
        self.wavelength_spin.setSuffix(" nm")
        self.wavelength_spin.valueChanged.connect(self.on_wavelength_spin_changed)
        wavelength_layout.addWidget(self.wavelength_spin)
        wavelength_group.setLayout(wavelength_layout)
        controls_layout.addWidget(wavelength_group)
        
        #MW Power Control
        mw_group = QGroupBox("MW Power (dBm)")
        mw_layout = QHBoxLayout()
        mw_layout.addWidget(QLabel("Power:"))
        self.mw_slider = QSlider(Qt.Horizontal)
        self.mw_slider.setRange(-30, 10)
        self.mw_slider.setValue(0)
        self.mw_slider.setTickPosition(QSlider.TicksBelow)
        self.mw_slider.setTickInterval(5)
        self.mw_slider.valueChanged.connect(self.on_mw_slider_changed)
        mw_layout.addWidget(self.mw_slider)
        self.mw_spin = QSpinBox()
        self.mw_spin.setRange(-30, 10)
        self.mw_spin.setValue(0)
        self.mw_spin.setSuffix(" dBm")
        self.mw_spin.valueChanged.connect(self.on_mw_spin_changed)
        mw_layout.addWidget(self.mw_spin)
        mw_group.setLayout(mw_layout)
        controls_layout.addWidget(mw_group)
        
        #Laser Sensitivity Control
        sens_group = QGroupBox("Laser Sensitivity")
        sens_layout = QHBoxLayout()
        sens_layout.addWidget(QLabel("Sensitivity:"))
        self.sensitivity_slider = QSlider(Qt.Horizontal)
        self.sensitivity_slider.setRange(10, 200)
        self.sensitivity_slider.setValue(50)
        self.sensitivity_slider.setTickPosition(QSlider.TicksBelow)
        self.sensitivity_slider.setTickInterval(20)
        self.sensitivity_slider.valueChanged.connect(self.on_sensitivity_slider_changed)
        sens_layout.addWidget(self.sensitivity_slider)
        self.sensitivity_spin = QDoubleSpinBox()
        self.sensitivity_spin.setRange(0.1, 2.0)
        self.sensitivity_spin.setSingleStep(0.01)
        self.sensitivity_spin.setValue(0.5)
        self.sensitivity_spin.setDecimals(2)
        self.sensitivity_spin.valueChanged.connect(self.on_sensitivity_spin_changed)
        sens_layout.addWidget(self.sensitivity_spin)
        sens_group.setLayout(sens_layout)
        controls_layout.addWidget(sens_group)
        
        #PID Control Section
        pid_group = QGroupBox("PID Control")
        pid_group.setStyleSheet("QGroupBox { font-weight: bold; border: 2px solid #4CAF50; margin-top: 10px; }")
        pid_layout = QVBoxLayout()
        
        # PID Set selection
        set_layout = QHBoxLayout()
        set_layout.addWidget(QLabel("PID Set:"))
        self.pid_set_combo = QComboBox()
        self.pid_set_combo.addItems(["PID Set 1"])
        self.pid_set_combo.currentIndexChanged.connect(self.on_pid_set_changed)
        set_layout.addWidget(self.pid_set_combo)
        
        self.add_pid_btn = QPushButton("+ Add")
        self.add_pid_btn.clicked.connect(self.add_pid_set)
        set_layout.addWidget(self.add_pid_btn)
        
        self.remove_pid_btn = QPushButton("- Remove")
        self.remove_pid_btn.clicked.connect(self.remove_pid_set)
        set_layout.addWidget(self.remove_pid_btn)
        pid_layout.addLayout(set_layout)
        
        # Kp control
        kp_layout = QVBoxLayout()
        kp_label_layout = QHBoxLayout()
        kp_label_layout.addWidget(QLabel("Kp:"))
        kp_label_layout.addStretch()
        kp_label_layout.addWidget(QLabel("Value:"))
        self.kp_value_label = QLabel("0.150")
        self.kp_value_label.setStyleSheet("color: blue; font-weight: bold; min-width: 50px;")
        kp_label_layout.addWidget(self.kp_value_label)
        kp_layout.addLayout(kp_label_layout)
        
        kp_slider_layout = QHBoxLayout()
        self.kp_slider = QSlider(Qt.Horizontal)
        self.kp_slider.setRange(0, 1000)
        self.kp_slider.setValue(15)
        self.kp_slider.setTickPosition(QSlider.TicksBelow)
        self.kp_slider.setTickInterval(100)
        self.kp_slider.valueChanged.connect(self.on_kp_slider_changed)
        kp_slider_layout.addWidget(self.kp_slider)
        self.kp_spin = QDoubleSpinBox()
        self.kp_spin.setRange(0, 10.0)
        self.kp_spin.setSingleStep(0.01)
        self.kp_spin.setValue(0.15)
        self.kp_spin.setDecimals(3)
        self.kp_spin.valueChanged.connect(self.on_kp_spin_changed)
        kp_slider_layout.addWidget(self.kp_spin)
        kp_layout.addLayout(kp_slider_layout)
        pid_layout.addLayout(kp_layout)
        
        # Ki control
        ki_layout = QVBoxLayout()
        ki_label_layout = QHBoxLayout()
        ki_label_layout.addWidget(QLabel("Ki:"))
        ki_label_layout.addStretch()
        ki_label_layout.addWidget(QLabel("Value:"))
        self.ki_value_label = QLabel("0.500")
        self.ki_value_label.setStyleSheet("color: blue; font-weight: bold; min-width: 50px;")
        ki_label_layout.addWidget(self.ki_value_label)
        ki_layout.addLayout(ki_label_layout)
        
        ki_slider_layout = QHBoxLayout()
        self.ki_slider = QSlider(Qt.Horizontal)
        self.ki_slider.setRange(0, 1000)
        self.ki_slider.setValue(50)
        self.ki_slider.setTickPosition(QSlider.TicksBelow)
        self.ki_slider.setTickInterval(100)
        self.ki_slider.valueChanged.connect(self.on_ki_slider_changed)
        ki_slider_layout.addWidget(self.ki_slider)
        self.ki_spin = QDoubleSpinBox()
        self.ki_spin.setRange(0, 10.0)
        self.ki_spin.setSingleStep(0.01)
        self.ki_spin.setValue(0.5)
        self.ki_spin.setDecimals(3)
        self.ki_spin.valueChanged.connect(self.on_ki_spin_changed)
        ki_slider_layout.addWidget(self.ki_spin)
        ki_layout.addLayout(ki_slider_layout)
        pid_layout.addLayout(ki_layout)
        
        # Kd control
        kd_layout = QVBoxLayout()
        kd_label_layout = QHBoxLayout()
        kd_label_layout.addWidget(QLabel("Kd:"))
        kd_label_layout.addStretch()
        kd_label_layout.addWidget(QLabel("Value:"))
        self.kd_value_label = QLabel("0.020")
        self.kd_value_label.setStyleSheet("color: blue; font-weight: bold; min-width: 50px;")
        kd_label_layout.addWidget(self.kd_value_label)
        kd_layout.addLayout(kd_label_layout)
        
        kd_slider_layout = QHBoxLayout()
        self.kd_slider = QSlider(Qt.Horizontal)
        self.kd_slider.setRange(0, 1000)
        self.kd_slider.setValue(2)
        self.kd_slider.setTickPosition(QSlider.TicksBelow)
        self.kd_slider.setTickInterval(100)
        self.kd_slider.valueChanged.connect(self.on_kd_slider_changed)
        kd_slider_layout.addWidget(self.kd_slider)
        self.kd_spin = QDoubleSpinBox()
        self.kd_spin.setRange(0, 10.0)
        self.kd_spin.setSingleStep(0.001)
        self.kd_spin.setValue(0.02)
        self.kd_spin.setDecimals(3)
        self.kd_spin.valueChanged.connect(self.on_kd_spin_changed)
        kd_slider_layout.addWidget(self.kd_spin)
        kd_layout.addLayout(kd_slider_layout)
        pid_layout.addLayout(kd_layout)
        
        pid_group.setLayout(pid_layout)
        controls_layout.addWidget(pid_group)
        
        #Zoom Control
        zoom_group = QGroupBox("Y-Axis Zoom")
        zoom_layout = QVBoxLayout()
        
        zoom_slider_layout = QHBoxLayout()
        zoom_slider_layout.addWidget(QLabel("± mW:"))
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(1, 1000)
        self.zoom_slider.setValue(200)
        self.zoom_slider.setTickPosition(QSlider.TicksBelow)
        self.zoom_slider.setTickInterval(100)
        self.zoom_slider.valueChanged.connect(self.on_zoom_slider_changed)
        zoom_slider_layout.addWidget(self.zoom_slider)
        self.zoom_spin = QDoubleSpinBox()
        self.zoom_spin.setRange(0.01, 10.0)
        self.zoom_spin.setSingleStep(0.01)
        self.zoom_spin.setValue(2.0)
        self.zoom_spin.setDecimals(2)
        self.zoom_spin.valueChanged.connect(self.on_zoom_spin_changed)
        zoom_slider_layout.addWidget(self.zoom_spin)
        zoom_layout.addLayout(zoom_slider_layout)
        
        self.auto_zoom_checkbox = QCheckBox("Auto-zoom")
        self.auto_zoom_checkbox.setChecked(True)
        self.auto_zoom_checkbox.stateChanged.connect(self.update_zoom_mode)
        zoom_layout.addWidget(self.auto_zoom_checkbox)
        
        zoom_group.setLayout(zoom_layout)
        controls_layout.addWidget(zoom_group)
        
        #Data Source
        source_group = QGroupBox("Data Source")
        source_layout = QVBoxLayout()
        self.source_combo = QComboBox()
        self.source_combo.addItems(['Synthetic', 'CSV Playback'])
        if TLPMX_AVAILABLE:
            self.source_combo.addItem('Thorlabs Live')
        self.source_combo.currentTextChanged.connect(self.on_source_changed)
        source_layout.addWidget(self.source_combo)
        
        self.csv_selection_widget = QWidget()
        csv_layout = QVBoxLayout()
        csv_layout.setContentsMargins(0, 0, 0, 0)
        self.preset_csv_combo = QComboBox()
        self.preset_csv_combo.addItems(['0 dBm', '2 dBm', '8 dBm'])
        self.preset_csv_combo.currentTextChanged.connect(self.on_preset_csv_selected)
        csv_layout.addWidget(self.preset_csv_combo)
        self.import_csv_btn = QPushButton("📂 Import CSV")
        self.import_csv_btn.clicked.connect(self.import_custom_csv)
        csv_layout.addWidget(self.import_csv_btn)
        self.csv_selection_widget.setLayout(csv_layout)
        self.csv_selection_widget.setVisible(False)
        source_layout.addWidget(self.csv_selection_widget)
        
        self.thorlabs_status = QLabel("⚫ Not Connected")
        source_layout.addWidget(self.thorlabs_status)
        
        btn_layout = QHBoxLayout()
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setEnabled(TLPMX_AVAILABLE)
        self.connect_btn.clicked.connect(self.connect_thorlabs)
        btn_layout.addWidget(self.connect_btn)
        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.clicked.connect(self.disconnect_thorlabs)
        self.disconnect_btn.setEnabled(False)
        btn_layout.addWidget(self.disconnect_btn)
        source_layout.addLayout(btn_layout)
        
        source_group.setLayout(source_layout)
        controls_layout.addWidget(source_group)
        
        #Action Buttons
        action_group = QGroupBox("Actions")
        action_layout = QVBoxLayout()
        self.save_btn = QPushButton("💾 Save Plot Data")
        self.save_btn.clicked.connect(self.save_current_plot_data)
        action_layout.addWidget(self.save_btn)
        
        btn_layout2 = QHBoxLayout()
        self.pause_btn = QPushButton("⏸️ Pause")
        self.pause_btn.clicked.connect(self.pause_all)
        btn_layout2.addWidget(self.pause_btn)
        self.start_btn = QPushButton("▶️ Start")
        self.start_btn.clicked.connect(self.start_all)
        self.start_btn.setEnabled(False)
        btn_layout2.addWidget(self.start_btn)
        action_layout.addLayout(btn_layout2)
        
        self.reset_btn = QPushButton("🔄 Reset")
        self.reset_btn.clicked.connect(self.reset_plot)
        action_layout.addWidget(self.reset_btn)
        
        action_group.setLayout(action_layout)
        controls_layout.addWidget(action_group)
        
        controls_layout.addStretch()
        right_widget.setWidget(controls_container)
        main_splitter.addWidget(right_widget)
        main_splitter.setSizes([800, 500])
        
        main_layout = QHBoxLayout()
        main_layout.addWidget(main_splitter)
        self.setLayout(main_layout)
        
        self.update_plot()
    
    #Spin box and slider
    
    def on_period_slider_changed(self, value):
        self.period_spin.blockSignals(True)
        self.period_spin.setValue(value)
        self.period_spin.blockSignals(False)
        self.update_sampling_rate(value)
    
    def on_period_spin_changed(self, value):
        self.period_slider.blockSignals(True)
        self.period_slider.setValue(value)
        self.period_slider.blockSignals(False)
        self.update_sampling_rate(value)
        
        freq = 1000.0 / value
        self.freq_slider.blockSignals(True)
        self.freq_spin.blockSignals(True)
        self.freq_slider.setValue(int(freq))
        self.freq_spin.setValue(int(freq))
        self.freq_slider.blockSignals(False)
        self.freq_spin.blockSignals(False)
    
    def on_freq_slider_changed(self, value):
        self.freq_spin.blockSignals(True)
        self.freq_spin.setValue(value)
        self.freq_spin.blockSignals(False)
        period = 1000.0 / value
        self.period_slider.blockSignals(True)
        self.period_spin.blockSignals(True)
        self.period_slider.setValue(int(period))
        self.period_spin.setValue(int(period))
        self.period_slider.blockSignals(False)
        self.period_spin.blockSignals(False)
        self.update_sampling_rate(period)
    
    def on_freq_spin_changed(self, value):
        self.freq_slider.blockSignals(True)
        self.freq_slider.setValue(value)
        self.freq_slider.blockSignals(False)
        period = 1000.0 / value
        self.period_slider.blockSignals(True)
        self.period_spin.blockSignals(True)
        self.period_slider.setValue(int(period))
        self.period_spin.setValue(int(period))
        self.period_slider.blockSignals(False)
        self.period_spin.blockSignals(False)
        self.update_sampling_rate(period)
    
    def on_wavelength_slider_changed(self, value):
        self.wavelength_spin.blockSignals(True)
        self.wavelength_spin.setValue(value)
        self.wavelength_spin.blockSignals(False)
        self.wavelength_nm = value
        self.set_wavelength(value)
    
    def on_wavelength_spin_changed(self, value):
        self.wavelength_slider.blockSignals(True)
        self.wavelength_slider.setValue(value)
        self.wavelength_slider.blockSignals(False)
        self.wavelength_nm = value
        self.set_wavelength(value)
    
    def on_mw_slider_changed(self, value):
        self.mw_spin.blockSignals(True)
        self.mw_spin.setValue(value)
        self.mw_spin.blockSignals(False)
        self.mw_power_dbm = value
        if hasattr(self.parent(), 't1_measurement') and self.parent().t1_measurement.aom_mw:
            self.parent().t1_measurement.mw_power_input.setText(str(value))
            self.parent().t1_measurement.pushButton_MW_set_Clicked()
    
    def on_mw_spin_changed(self, value):
        self.mw_slider.blockSignals(True)
        self.mw_slider.setValue(value)
        self.mw_slider.blockSignals(False)
        self.mw_power_dbm = value
        if hasattr(self.parent(), 't1_measurement') and self.parent().t1_measurement.aom_mw:
            self.parent().t1_measurement.mw_power_input.setText(str(value))
            self.parent().t1_measurement.pushButton_MW_set_Clicked()
    
    def on_sensitivity_slider_changed(self, value):
        sensitivity = value / 100.0
        self.sensitivity_spin.blockSignals(True)
        self.sensitivity_spin.setValue(sensitivity)
        self.sensitivity_spin.blockSignals(False)
        self.laser_sensitivity = sensitivity
        self.multi_pid.laser_sensitivity = sensitivity
    
    def on_sensitivity_spin_changed(self, value):
        self.sensitivity_slider.blockSignals(True)
        self.sensitivity_slider.setValue(int(value * 100))
        self.sensitivity_slider.blockSignals(False)
        self.laser_sensitivity = value
        self.multi_pid.laser_sensitivity = value
    
    def on_kp_slider_changed(self, value):
        kp = value / 100.0
        self.kp_spin.blockSignals(True)
        self.kp_spin.setValue(kp)
        self.kp_spin.blockSignals(False)
        self.kp_value_label.setText(f"{kp:.3f}")
        self.current_kp = kp
        self.multi_pid.update_gains(self.current_pid_set_id, Kp=kp)
    
    def on_kp_spin_changed(self, value):
        self.kp_slider.blockSignals(True)
        self.kp_slider.setValue(int(value * 100))
        self.kp_slider.blockSignals(False)
        self.kp_value_label.setText(f"{value:.3f}")
        self.current_kp = value
        self.multi_pid.update_gains(self.current_pid_set_id, Kp=value)
    
    def on_ki_slider_changed(self, value):
        ki = value / 100.0
        self.ki_spin.blockSignals(True)
        self.ki_spin.setValue(ki)
        self.ki_spin.blockSignals(False)
        self.ki_value_label.setText(f"{ki:.3f}")
        self.current_ki = ki
        self.multi_pid.update_gains(self.current_pid_set_id, Ki=ki)
    
    def on_ki_spin_changed(self, value):
        self.ki_slider.blockSignals(True)
        self.ki_slider.setValue(int(value * 100))
        self.ki_slider.blockSignals(False)
        self.ki_value_label.setText(f"{value:.3f}")
        self.current_ki = value
        self.multi_pid.update_gains(self.current_pid_set_id, Ki=value)
    
    def on_kd_slider_changed(self, value):
        kd = value / 100.0
        self.kd_spin.blockSignals(True)
        self.kd_spin.setValue(kd)
        self.kd_spin.blockSignals(False)
        self.kd_value_label.setText(f"{kd:.3f}")
        self.current_kd = kd
        self.multi_pid.update_gains(self.current_pid_set_id, Kd=kd)
    
    def on_kd_spin_changed(self, value):
        self.kd_slider.blockSignals(True)
        self.kd_slider.setValue(int(value * 100))
        self.kd_slider.blockSignals(False)
        self.kd_value_label.setText(f"{value:.3f}")
        self.current_kd = value
        self.multi_pid.update_gains(self.current_pid_set_id, Kd=value)
    
    def on_zoom_slider_changed(self, value):
        zoom = value / 100.0
        self.zoom_spin.blockSignals(True)
        self.zoom_spin.setValue(zoom)
        self.zoom_spin.blockSignals(False)
        self.zoom_factor = zoom
        self.update_plot()
    
    def on_zoom_spin_changed(self, value):
        self.zoom_slider.blockSignals(True)
        self.zoom_slider.setValue(int(value * 100))
        self.zoom_slider.blockSignals(False)
        self.zoom_factor = value
        self.update_plot()
    
    def update_zoom_mode(self):
        self.zoom_slider.setEnabled(not self.auto_zoom_checkbox.isChecked())
        self.zoom_spin.setEnabled(not self.auto_zoom_checkbox.isChecked())
        self.update_plot()
    
    def update_sampling_rate(self, period_ms):
        self.sampling_period_ms = period_ms
        self.timer.setInterval(int(period_ms))
        if self.thorlabs_worker:
            self.thorlabs_worker.set_sampling_period(period_ms)
    
    def on_pid_set_changed(self, index):
        self.multi_pid.update_gains(self.current_pid_set_id, Kp=self.current_kp, Ki=self.current_ki, Kd=self.current_kd)
        
        set_ids = list(self.multi_pid.get_all_pids().keys())
        if index < len(set_ids):
            self.current_pid_set_id = set_ids[index]
            data = self.multi_pid.get_all_pids()[self.current_pid_set_id]
            self.current_kp = data['Kp']
            self.current_ki = data['Ki']
            self.current_kd = data['Kd']
            
            self.kp_slider.blockSignals(True)
            self.ki_slider.blockSignals(True)
            self.kd_slider.blockSignals(True)
            self.kp_spin.blockSignals(True)
            self.ki_spin.blockSignals(True)
            self.kd_spin.blockSignals(True)
            
            self.kp_slider.setValue(int(self.current_kp * 100))
            self.ki_slider.setValue(int(self.current_ki * 100))
            self.kd_slider.setValue(int(self.current_kd * 100))
            self.kp_spin.setValue(self.current_kp)
            self.ki_spin.setValue(self.current_ki)
            self.kd_spin.setValue(self.current_kd)
            self.kp_value_label.setText(f"{self.current_kp:.3f}")
            self.ki_value_label.setText(f"{self.current_ki:.3f}")
            self.kd_value_label.setText(f"{self.current_kd:.3f}")
            
            self.kp_slider.blockSignals(False)
            self.ki_slider.blockSignals(False)
            self.kd_slider.blockSignals(False)
            self.kp_spin.blockSignals(False)
            self.ki_spin.blockSignals(False)
            self.kd_spin.blockSignals(False)
    
    def add_pid_set(self):
        if self.multi_pid.get_pid_count() >= 20:
            QMessageBox.warning(self, "Limit", "Maximum 20 PID sets")
            return
        
        new_name = f"PID Set {self.multi_pid.get_pid_count() + 1}"
        new_id = self.multi_pid.add_pid(0.15, 0.5, 0.02, new_name)
        self.pid_set_combo.addItem(new_name)
        self.controlled_power_sets[new_id] = deque(maxlen=500)
        print(f"Added PID set: {new_name}")
    
    def remove_pid_set(self):
        if self.multi_pid.get_pid_count() <= 1:
            QMessageBox.warning(self, "Cannot Remove", "At least one PID set is required.")
            return
        
        current_index = self.pid_set_combo.currentIndex()
        set_ids = list(self.multi_pid.get_all_pids().keys())
        if current_index < len(set_ids):
            set_id_to_remove = set_ids[current_index]
            self.multi_pid.remove_pid(set_id_to_remove)
            if set_id_to_remove in self.controlled_power_sets:
                del self.controlled_power_sets[set_id_to_remove]
            
            self.pid_set_combo.clear()
            for set_id, data in self.multi_pid.get_all_pids().items():
                self.pid_set_combo.addItem(data['name'])
            self.pid_set_combo.setCurrentIndex(0)
            self.on_pid_set_changed(0)
            print(f"Removed PID set")
    
    def on_source_changed(self, source):
        is_csv = (source == 'CSV Playback')
        self.csv_selection_widget.setVisible(is_csv)
        if is_csv:
            self.on_preset_csv_selected(self.preset_csv_combo.currentText())
    
    def on_preset_csv_selected(self, preset_name):
        self.simulator.set_dataset(preset_name)
        self.reset_plot()
    
    def import_custom_csv(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Select CSV", "", "CSV Files (*.csv)")
        if filepath:
            name = os.path.basename(filepath).replace('.csv', '')
            if self.simulator.load_csv(filepath, name):
                self.preset_csv_combo.addItem(name)
                self.preset_csv_combo.setCurrentText(name)
                cols = self.simulator.get_controlled_cols()
                for i, col in enumerate(cols):
                    self.csv_controlled_colors[col] = PID_COLORS[i % len(PID_COLORS)]
                QMessageBox.information(self, "Success", f"Loaded {name}\nFound {len(cols)} controlled outputs")
            else:
                QMessageBox.warning(self, "Error", "Failed to load CSV")
    
    def load_default_data(self):
        self.simulator.generate_synthetic('0 dBm', 88.2, 0.8)
        self.simulator.generate_synthetic('2 dBm', 89.1, 0.5)
        self.simulator.generate_synthetic('8 dBm', 6.3, 0.2)
        self.simulator.set_dataset('0 dBm')
    
    def connect_thorlabs(self):
        if not TLPMX_AVAILABLE:
            QMessageBox.critical(self, "Error", "TLPMX not available")
            return
        if self.thorlabs_worker:
            return
        self.thorlabs_worker = ThorlabsWorker()
        self.thorlabs_worker.set_sampling_period(self.sampling_period_ms)
        self.thorlabs_worker.power_updated.connect(self.on_thorlabs_power)
        self.thorlabs_worker.connected.connect(self.on_thorlabs_connected)
        self.thorlabs_status.setText("🟡 Connecting...")
        self.connect_btn.setEnabled(False)
        if self.thorlabs_worker.connect_meter():
            self.thorlabs_worker.start()
    
    def disconnect_thorlabs(self):
        if self.thorlabs_worker:
            self.thorlabs_worker.stop()
            self.thorlabs_worker = None
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        self.is_connected = False
        self.thorlabs_status.setText("⚫ Not Connected")
    
    def on_thorlabs_connected(self, success):
        if success:
            self.is_connected = True
            self.thorlabs_status.setText("🟢 Connected")
            self.disconnect_btn.setEnabled(True)
            self.plot_start_time = time.time()
            self.set_wavelength(self.wavelength_nm)
        else:
            self.thorlabs_status.setText("🔴 Failed")
            self.connect_btn.setEnabled(True)
    
    def on_thorlabs_power(self, power_mw, timestamp):
        if self.source_combo.currentText() == 'Thorlabs Live':
            self.latest_thorlabs_power = power_mw
    
    def set_wavelength(self, wl):
        if self.thorlabs_worker and self.is_connected:
            self.thorlabs_worker.set_wavelength(wl)
    
    def pause_all(self):
        if not self.is_paused:
            self.is_paused = True
            self.pause_start_time = time.time()
            self.pause_btn.setEnabled(False)
            self.start_btn.setEnabled(True)
    
    def start_all(self):
        if self.is_paused:
            self.is_paused = False
            if self.pause_start_time:
                self.total_paused_time += time.time() - self.pause_start_time
                self.pause_start_time = None
            self._last_pid_update_time = time.time()
            self.pause_btn.setEnabled(True)
            self.start_btn.setEnabled(False)
    
    def reset_plot(self):
        self.times.clear()
        self.raw_powers.clear()
        self.controlled_power_sets.clear()
        self.csv_controlled_histories.clear()
        
        self.live_stats.reset()
        self.multi_pid.reset_all()
        self._last_pid_update_time = None
        self.simulator.reset()
        
        current_time = time.time()
        self.plot_start_time = current_time
        self.collection_start_time = current_time
        self.total_paused_time = 0.0
        self.pause_start_time = None
        
        self.update_plot()
    
    def save_current_plot_data(self):
        if len(self.times) == 0:
            QMessageBox.warning(self, "No Data", "No data to save.")
            return
        
        filename, _ = QFileDialog.getSaveFileName(self, "Save Data",
            f"laser_data_{QDateTime.currentDateTime().toString('yyyyMMdd_hhmmss')}.csv",
            "CSV Files (*.csv)")
        
        if filename:
            try:
                with open(filename, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    header = ['Time (s)', 'Raw Power (mW)']
                    for set_id, data in self.multi_pid.get_all_pids().items():
                        header.append(f'Controlled Power ({data["name"]})')
                    writer.writerow(header)
                    
                    times_list = list(self.times)
                    raw_list = list(self.raw_powers)
                    
                    for i in range(len(times_list)):
                        row = [f"{times_list[i]:.3f}", f"{raw_list[i]:.6f}"]
                        for set_id, data in self.multi_pid.get_all_pids().items():
                            if set_id in self.controlled_power_sets and i < len(self.controlled_power_sets[set_id]):
                                row.append(f"{list(self.controlled_power_sets[set_id])[i]:.6f}")
                            else:
                                row.append("")
                        writer.writerow(row)
                QMessageBox.information(self, "Saved", f"Data saved to:\n{filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save: {e}")
    
    def update_loop(self):
        if self.is_paused:
            return
        
        if self.collection_start_time is None:
            self.collection_start_time = time.time()
        
        source = self.source_combo.currentText()
        current_time = time.time()
        
        if self._last_pid_update_time is None:
            pid_dt = self.sampling_period_ms / 1000.0
        else:
            pid_dt = current_time - self._last_pid_update_time
            if pid_dt <= 0 or pid_dt > 1.0:
                pid_dt = self.sampling_period_ms / 1000.0
        
        if source == 'Thorlabs Live' and self.is_connected:
            raw_power = self.latest_thorlabs_power
            if self.plot_start_time is None:
                self.plot_start_time = current_time
            t = current_time - self.plot_start_time
            self.csv_controlled_histories.clear()
        elif source == 'CSV Playback':
            t, raw_power, controlled = self.simulator.get_next()
            for col, power in controlled.items():
                if col not in self.csv_controlled_histories:
                    self.csv_controlled_histories[col] = []
                self.csv_controlled_histories[col].append(power)
        else:
            t, raw_power, _ = self.simulator.get_next()
            self.csv_controlled_histories.clear()
        
        elapsed = current_time - self.collection_start_time - self.total_paused_time
        self.live_stats.update_time_elapsed(elapsed)
        
        if len(self.raw_powers) >= 10:
            recent = list(self.raw_powers)[-50:] if len(self.raw_powers) >= 50 else list(self.raw_powers)
            running_avg = np.mean(recent)
        else:
            running_avg = raw_power
        
        if source == 'CSV Playback':
            self.controlled_power_sets.clear()
        else:
            pid_results = self.multi_pid.update_all(running_avg, raw_power, dt=pid_dt)
            self._last_pid_update_time = current_time
            
            for set_id, result in pid_results.items():
                if set_id not in self.controlled_power_sets:
                    self.controlled_power_sets[set_id] = deque(maxlen=500)
                self.controlled_power_sets[set_id].append(result['controlled_power'])
        
        self.times.append(t)
        self.raw_powers.append(raw_power)
        self.live_stats.update_reading(raw_power)
        self.update_plot()
    
    def update_plot(self):
        self.ax1.clear()
        self.ax2.clear()
        
        source = self.source_combo.currentText()
        
        if len(self.times) > 0:
            times_list = list(self.times)
            raw_list = list(self.raw_powers)
            running_avg_raw = self.live_stats.running_avg_raw
            
            self.ax1.plot(times_list, raw_list, 'b-', linewidth=1.5, alpha=0.8)
            self.ax1.axhline(y=running_avg_raw, color='purple', linestyle='--', linewidth=1.5,
                            label=f'Avg: {running_avg_raw:.2f} mW')
            self.ax1.set_ylabel('Power (mW)')
            self.ax1.set_title('Raw Laser Power')
            self.ax1.legend(loc='upper right', fontsize=8)
            self.ax1.grid(True, alpha=0.3)
            
            self.ax2.plot(times_list, raw_list, 'k-', linewidth=2.0, alpha=0.9, label='Raw Power', zorder=10)
            
            if source == 'CSV Playback':
                for col, powers in self.csv_controlled_histories.items():
                    if len(powers) == len(times_list):
                        if col not in self.csv_controlled_colors:
                            color_idx = len(self.csv_controlled_colors) % len(PID_COLORS)
                            self.csv_controlled_colors[col] = PID_COLORS[color_idx]
                        color = self.csv_controlled_colors[col]
                        short_name = col.replace('Controlled Power ', '').replace('(', '').replace(')', '')
                        if len(short_name) > 30:
                            short_name = short_name[:27] + '...'
                        self.ax2.plot(times_list, powers, color=color, linewidth=1.2, 
                                    label=short_name, alpha=0.8)
            else:
                for set_id, data in self.multi_pid.get_all_pids().items():
                    if set_id in self.controlled_power_sets and len(self.controlled_power_sets[set_id]) > 0:
                        controlled_list = list(self.controlled_power_sets[set_id])
                        min_len = min(len(times_list), len(controlled_list))
                        label = f"{data['name']} (Kp={data['Kp']:.2f}, Ki={data['Ki']:.2f}, Kd={data['Kd']:.3f})"
                        self.ax2.plot(times_list[:min_len], controlled_list[:min_len], 
                                     color=data['color'], linewidth=1.2, 
                                     label=label, alpha=0.8)
            
            self.ax2.set_ylabel('Power (mW)')
            self.ax2.set_xlabel('Time (s)')
            
            if source == 'CSV Playback' and self.csv_controlled_histories:
                num_controlled = len(self.csv_controlled_histories)
                self.ax2.set_title(f'Comparison: Raw vs {num_controlled} Controlled Outputs')
            else:
                self.ax2.set_title('Comparison: Raw vs PID-Controlled Power (K values shown)')
            
            self.ax2.legend(loc='upper right', fontsize=7, ncol=2)
            self.ax2.grid(True, alpha=0.3)
            
            if self.auto_zoom_checkbox.isChecked():
                if len(raw_list) > 10:
                    recent = raw_list[-100:] if len(raw_list) >= 100 else raw_list
                    std_raw = np.std(recent)
                    y_range = max(3 * std_raw, 0.5)
                    y_center = running_avg_raw
                    y_min = max(y_center - y_range, 0)
                    y_max = y_center + y_range
                else:
                    y_center = running_avg_raw
                    y_min = max(y_center - self.zoom_factor, 0)
                    y_max = y_center + self.zoom_factor
            else:
                y_center = running_avg_raw
                y_min = max(y_center - self.zoom_factor, 0)
                y_max = y_center + self.zoom_factor
            
            self.ax1.set_ylim(y_min, y_max)
            self.ax2.set_ylim(y_min, y_max)
        
        self.canvas.draw()
        self.canvas.flush_events()


class UnifiedLaserControlGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Laser Control - PID with Sliders & Number Inputs | K values on Legend")
        self.setGeometry(100, 100, 1550, 1000)
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        tabs = QTabWidget()
        
        self.laser_control = LaserControlWidget()
        tabs.addTab(self.laser_control, "🔬 Laser Control")
        
        self.t1_measurement = T1MeasurementWidget()
        tabs.addTab(self.t1_measurement, "📡 T1 Measurement")
        
        main_layout.addWidget(tabs)
        
        self.statusBar().showMessage("Ready | Both slider and number inputs available | K values shown on graph legend")
        
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        view_menu = menubar.addMenu('View')
        fullscreen_action = QAction('Fullscreen', self)
        fullscreen_action.setShortcut('F11')
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        help_menu = menubar.addMenu('Help')
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def show_about(self):
        QMessageBox.about(self, "About",
            "<h2>Laser Power Stabilization System</h2>"
            "<p>Version 5.0 - Dual Input Interface</p>"
            "<p><b>Key Features:</b></p>"
            "<ul>"
            "<li><b>Dual Input Methods:</b> Adjust parameters using sliders OR numeric entry fields</li>"
            "<li><b>PID Values on Graph:</b> Each PID configuration displays its Kp, Ki, Kd values in the legend</li>"
            "<li><b>Full PID Functionality:</b> Complete Kp, Ki, Kd adjustment capabilities</li>"
            "<li><b>Multiple Configurations:</b> Create and manage up to 20 different PID sets</li>"
            "<li><b>Comprehensive Controls:</b> Sampling rate, wavelength, MW power, sensitivity, and zoom</li>"
            "<li><b>CSV Data Playback:</b> Visualize all recorded controlled outputs in distinct colors</li>"
            "<li><b>Live Monitoring:</b> Track current power, min/max values, RSD percentage, and elapsed time</li>"
            "</ul>"
            "<p>© 2026 - Achieving Stable Laser Power Output Using PID Control</p>")
    
    def closeEvent(self, event):
        if hasattr(self.laser_control, 'timer'):
            self.laser_control.timer.stop()
        if hasattr(self.laser_control, 'thorlabs_worker') and self.laser_control.thorlabs_worker:
            self.laser_control.thorlabs_worker.stop()
        event.accept()


def main():
    import pandas as pd
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = UnifiedLaserControlGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()