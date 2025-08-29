

# Default setup

CENTER_FREQ = 1.5e9        # 1.5 GHz (center between 1-2 GHz)
SPAN = 1e9                 # 1 GHz span (from 1-2 GHz)
REF_LEVEL = 0              # Reference level in dBm
RBW = 10e3                 # 10 kHz resolution bandwidth
VBW = 10e3                 # 10 kHz video bandwidth
SWEEP_TIME = 'AUTO ON'     # auto sweep time
SWEEP_POINTS = 1001        # Number of trace points


init_command = (
     ":INITiate:CONTinuous ON",
    f":SENSE:FREQUENCY:CENTER {CENTER_FREQ}",
    f":SENSE:FREQUENCY:SPAN {SPAN}",
    f":DISPLAY:TRACE:Y:SCALE:RLEVEL {REF_LEVEL}",
    f":SENSE:BANDWIDTH:RESOLUTION {RBW}",
    f":SENSE:BANDWIDTH:VIDEO {VBW}",
    f":SENSE:SWEEP:TIME {SWEEP_TIME}",
    f":SENSE:SWEEP:POINTS {SWEEP_POINTS}",
)

