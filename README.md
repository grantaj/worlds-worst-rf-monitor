# World's Worst RF Monitor

A visualizer for hackrf_sweep - just wanted something to look at signals.

## Installation

### macOS

#### 1. Install Homebrew (if not already installed)

Homebrew is a package manager for macOS. To install it, open Terminal and run:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Follow the on-screen instructions. You may need to install Xcode Command Line Tools if prompted:

```bash
xcode-select --install
```

#### 2. Install HackRF Tools

Once Homebrew is installed, install the HackRF tools:

```bash
brew install hackrf
```

This will install the necessary HackRF command-line tools including `hackrf_sweep`.

#### 3. Set up Python Virtual Environment

Create a virtual environment for the project dependencies:

```bash
python3 -m venv rf_monitor_env
```

#### 4. Activate the Virtual Environment

Activate the virtual environment:

```bash
source rf_monitor_env/bin/activate
```

Your terminal prompt should now show `(rf_monitor_env)` at the beginning.

#### 5. Install Python Dependencies

With the virtual environment activated, install the required packages:

```bash
pip install -r requirements.txt
```

#### 6. Run the Application

Make sure your HackRF device is connected, then run:

```bash
python hackrf_visualizer.py
```

#### Deactivating the Virtual Environment

When you're done, deactivate the virtual environment:

```bash
deactivate
```

## Usage

The `hackrf_visualizer.py` script provides a live visualization of RF spectrum data captured by your HackRF device. It uses `hackrf_sweep` under the hood and displays the results in real-time.

### Basic Usage

Run the visualizer with default settings:

```bash
python hackrf_visualizer.py
```

### Command Line Options

- `--sweep-args "ARGS"`: Pass additional arguments to `hackrf_sweep` (e.g., frequency ranges, bandwidth)
- `--waterfall`: Enable waterfall display showing spectrum history
- `--avg N`: Average the last N sweeps for smoother line plotting (default: 1)
- `--buf N`: Number of sweeps to keep in waterfall buffer (default: 100)
- `--fps N`: Update rate in frames per second (default: 4.0)

### Keyboard Shortcuts

While the visualizer is running:
- `s`: Save a snapshot (CSV data and PNG image)
- `r`: Reset the buffer and envelope

### Australian Frequency Band Examples

Here are some examples of frequency bands commonly used in Australia:

#### FM Radio Broadcasting (87.5-108 MHz)

```bash
python hackrf_visualizer.py --sweep-args "-f 87.5:108 -w 5000" --waterfall
```

#### DAB+ Digital Radio (174-230 MHz)

```bash
python hackrf_visualizer.py --sweep-args "-f 174:230 -w 5000" --waterfall --avg 3
```

#### UHF Television (470-820 MHz)

```bash
python hackrf_visualizer.py --sweep-args "-f 470:820 -w 100000" --waterfall
```

#### 2.4 GHz WiFi (2.4-2.484 GHz)

```bash
python hackrf_visualizer.py --sweep-args "-f 2400:2484 -w 1000000" --waterfall
```

#### 5 GHz WiFi (5.15-5.85 GHz)

```bash
python hackrf_visualizer.py --sweep-args "-f 5150:5850 -w 2000000" --waterfall
```

#### Mobile/Cellular Bands (700-2600 MHz)

```bash
python hackrf_visualizer.py --sweep-args "-f 700:2600 -w 500000" --waterfall --avg 5
```

#### Emergency Services & Aviation (VHF/UHF)

```bash
python hackrf_visualizer.py --sweep-args "-f 118:137 -f 138:174 -f 403:520 -w 25000" --waterfall
```

### Tips

- Use `--waterfall` for a historical view of spectrum activity
- Increase `--avg` for smoother plots in noisy environments
- Adjust `--fps` based on your system's performance (lower values reduce CPU usage)
- Use narrower bandwidth (`-w`) for higher frequency resolution, wider for faster scanning
- Multiple frequency ranges can be specified with multiple `-f` arguments

## Requirements

- HackRF One device
- macOS with Homebrew
- Python 3.7+
- Required Python packages (installed via requirements.txt):
  - numpy
  - matplotlib
  - Optional: pyqtgraph (for faster interactive plotting)
