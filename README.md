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

## Requirements

- HackRF One device
- macOS with Homebrew
- Python 3.7+
- Required Python packages (installed via requirements.txt):
  - numpy
  - matplotlib
  - Optional: pyqtgraph (for faster interactive plotting)
