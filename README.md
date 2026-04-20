# Achieving_Stable_Laser_Power_Output_Using_PID_Control
                    LASER POWER STABILIZATION SYSTEM
                    PID Control with Thorlabs Power Meter

REQUIRED FILES (same folder):
---------------------------
- TLPMX.py          - Thorlabs power meter wrapper
- TLPMX_64.dll      - Thorlabs driver
- Hardwares/ folder - For T1/MW source

INSTALLATION:
------------
pip install PyQt5 numpy matplotlib pandas scipy


                         PROGRAM 1: LASER CONTROL GUI
                        (laser_control_gui.py)


WHAT IT DOES:
------------
Real-time laser power monitoring and stabilization with PID control.

KEY FEATURES:
------------
• Connect Thorlabs power meter via USB
• Adjust Kp, Ki, Kd with sliders OR number inputs
• Up to 20 simultaneous PID sets (each with different colors)
• K values shown on graph legend
• Three data sources: Thorlabs Live / Synthetic / CSV Playback
• Dual graphs: Raw power (top) vs Controlled outputs (bottom)
• Auto/manual Y-axis zoom
• Save plot data to CSV
• Time elapsed display (HH:MM:SS)
• T1 measurement tab (MW source control)

QUICK START:
-----------
1. Run: py laser_control_gui.py
2. Click "Connect" (wait for green status)
3. Select "Thorlabs Live" as data source
4. Adjust PID gains using sliders or spin boxes
5. Click "Start" to begin data collection
6. Use "Save Plot Data" to export CSV

HOTKEYS:
--------
F11 = Fullscreen | Ctrl+Q = Exit


                      PROGRAM 2: AUTOMATED PID SWEEPER
                        (sweeper.py)


WHAT IT DOES:
------------
Automatically tests all PID configurations for each dBm value.

TEST CONFIGURATIONS (15 per dBm):
-------------------------------
• 5 P-only sets    (Kp=0.1 to 1.0)
• 5 PI-only sets   (Kp=0.2-0.6, Ki=0.05-0.25)
• 5 Full PID sets  (Kp=0.2-0.8, Ki=0.04-0.2, Kd=0.02-0.1)

dBm VALUES TESTED:
-----------------
5 dBm, 2 dBm, 0 dBm, -2 dBm, -5 dBm

SAMPLING RATES:
--------------
1 Hz, 2 Hz, 5 Hz, 10 Hz, 20 Hz (all recorded simultaneously)

DURATION:
--------
5 minutes per dBm (configurable) → ~25 minutes total

QUICK START:
-----------
1. Run: py sweeper.py
2. Select save folder when prompted
3. Wait for completion (folder opens automatically)

OUTPUT FILES (in timestamped folder):
-----------------------------------
• pid_sweep_dBmX_YHz.csv - Data for each dBm & sampling rate
• master_summary.csv     - Statistics summary
• sweep_report.txt       - Best performing configurations

CUSTOMIZE DURATION:
------------------
Edit in sweeper.py: RECORDING_DURATION = 300  # seconds


                           PID TUNING QUICK GUIDE


Kp (Proportional) = Response speed     (start: 0.3-0.5)
Ki (Integral)     = Steady-state error (start: 0.05-0.1)
Kd (Derivative)   = Damping/overshoot  (start: 0.02-0.05)

Tuning Steps:
------------
1. Start with Kp only (Ki=0, Kd=0)
2. Increase Kp until oscillation, then reduce by 50%
3. Add Ki (start = Kp/3) to eliminate error
4. Add Kd (start = Kp/10) to reduce overshoot

Power Level Guidelines:
-----------------------
High power (5 dBm)   → Larger gains (Kp up to 1.0)
Low power (-5 dBm)   → Smaller gains (Kp < 0.4)


                         TROUBLESHOOTING


"TLPMX not available"        → Check TLPMX.py and TLPMX_64.dll in folder
"Could not connect"          → Check USB, close other software, restart meter
"No data recording"          → Ensure "Thorlabs Live" selected, check connection
"Sweeper not saving"         → Check folder permissions, run as administrator


                               FILE STRUCTURE


Your_Folder/
├── laser_control_gui.py
├── sweeper.py
├── TLPMX.py
├── TLPMX_64.dll
└── Hardwares

Output: pid_sweep_YYYYMMDD_HHMMSS/
        ├── pid_sweep_dBm5.csv_1Hz.csv
        ├── master_summary.csv
        └── sweep_report.txt


                                  NOTES


• Both programs require TLPMX.py and TLPMX_64.dll in the same folder
• Synthetic data mode works without hardware (for testing)
• CSV Playback can load previously recorded data
• The sweeper saves results to your chosen location
• All settings adjustable via sliders AND number inputs

================================================================================
