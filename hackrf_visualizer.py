import argparse
import shlex
import subprocess
import threading
import queue
import csv
import time
from collections import deque
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime

# python3 hackrf_visualizer.py --sweep-args "-f 174:230 -w 5000" --waterfall --avg 3
# DAB:  -f 174:230 -w 5000
# FM:   -f 88:110 -w 5000
# WiFi: -f 2400:2484 -w 1000000
# WiFi: 
def parse_line(line):
    # parse CSV style line from hackrf_sweep
    parts = next(csv.reader([line.strip()]))
    if len(parts) < 7:
        return None
    date, tm = parts[0].strip(), parts[1].strip()
    ts = f"{date} {tm}"
    try:
        hz_low = float(parts[2])
        hz_high = float(parts[3])
        # parts[4] = bin width, parts[5] = num_samples (often not per-line)
        samples = [float(x) for x in parts[6:]]
    except Exception:
        return None
    # map each sample in this line to frequencies across the range
    if len(samples) == 0:
        return None
    freqs = np.linspace(hz_low, hz_high, len(samples), endpoint=False)
    return ts, freqs, np.array(samples)

def reader_thread(proc, out_q, stop_event):
    current_ts = None
    sweep_chunks = []  # list of (hz_low, freqs, power)
    while not stop_event.is_set():
        line = proc.stdout.readline()
        if not line:
            if proc.poll() is not None:
                break
            time.sleep(0.01)
            continue
        parsed = parse_line(line)
        if not parsed:
            continue
        ts, freqs, power = parsed
        hz_low = freqs[0]  # since linspace start
        if current_ts is None:
            current_ts = ts
        if ts != current_ts:
            # finish previous sweep
            if len(sweep_chunks) > 0:
                # sort by hz_low
                sweep_chunks.sort(key=lambda x: x[0])
                f = np.concatenate([freqs for _, freqs, _ in sweep_chunks])
                p = np.concatenate([power for _, _, power in sweep_chunks])
                out_q.put((current_ts, f, p))
            sweep_chunks = [(hz_low, freqs, power)]
            current_ts = ts
        else:
            sweep_chunks.append((hz_low, freqs, power))
    # push last sweep if any
    if len(sweep_chunks) > 0:
        sweep_chunks.sort(key=lambda x: x[0])
        f = np.concatenate([freqs for _, freqs, _ in sweep_chunks])
        p = np.concatenate([power for _, _, power in sweep_chunks])
        out_q.put((current_ts, f, p))
    out_q.put(None)  # sentinel

def main():
    parser = argparse.ArgumentParser(description="Basic hackrf_sweep live visualizer")
    parser.add_argument("--sweep-args", default="", help="Extra args to pass to hackrf_sweep (e.g. '-f 200:300')")
    parser.add_argument("--waterfall", action="store_true", help="Enable waterfall display")
    parser.add_argument("--avg", type=int, default=1, help="Average last N sweeps for line plot")
    parser.add_argument("--buf", type=int, default=100, help="Number of sweeps to keep in waterfall buffer")
    parser.add_argument("--fps", type=float, default=4.0, help="Update rate (frames per second)")
    args = parser.parse_args()

    cmd = ["hackrf_sweep"] + shlex.split(args.sweep_args)
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
    except FileNotFoundError:
        print("hackrf_sweep not found in PATH.")
        return

    out_q = queue.Queue()
    stop_event = threading.Event()
    t = threading.Thread(target=reader_thread, args=(proc, out_q, stop_event), daemon=True)
    t.start()

    freq_axis = None
    buf = deque(maxlen=args.buf)

    fig, (ax_line, ax_wf) = plt.subplots(2 if args.waterfall else 1, 1, figsize=(10, 6), sharex=args.waterfall) \
        if args.waterfall else (plt.subplots(1,1,figsize=(10,4))[0], None)

    if args.waterfall:
        # ensure ax_wf is the second axes
        if isinstance(ax_line, (list, tuple)):
            ax_line, ax_wf = ax_line

    fig.tight_layout()

    line_plot, = ax_line.plot([], [], lw=1)
    ax_line.set_xlabel("Frequency (MHz)")
    ax_line.set_ylabel("Power (dB)")
    ax_line.grid(True)
    img = None

    last_update = time.time()

    def update(frame):
        nonlocal freq_axis, img, last_update
        # pull all completed sweeps from queue
        changed = False
        while True:
            try:
                item = out_q.get_nowait()
            except queue.Empty:
                break
            if item is None:
                stop_event.set()
                break
            ts, freqs, power = item
            # sort by freq just in case
            order = np.argsort(freqs)
            freqs = freqs[order]
            power = power[order]
            if freq_axis is None:
                freq_axis = freqs
            else:
                # resample to existing freq_axis if shapes differ
                if len(freqs) != len(freq_axis) or not np.allclose(freqs, freq_axis, atol=1e-6):
                    power = np.interp(freq_axis, freqs, power)
            buf.append(power)
            changed = True

        if not changed and len(buf) == 0:
            return

        # compute averaged line
        recent = list(buf)[-args.avg:] if args.avg > 1 else list(buf)[-1:]
        arr = np.vstack(recent)
        mean_line = arr.mean(axis=0)

        x_mhz = (freq_axis / 1e6) if freq_axis is not None else np.array([])

        # interpolate to regular grid for proper alignment
        if len(x_mhz) > 1:
            x_regular = np.linspace(x_mhz[0], x_mhz[-1], len(x_mhz))
            mean_line = np.interp(x_regular, x_mhz, mean_line)
            x_mhz = x_regular

        line_plot.set_data(x_mhz, mean_line)
        ax_line.relim()
        ax_line.autoscale_view()

        if args.waterfall:
            data = np.vstack(buf)  # shape (n_sweeps, n_freqs)
            # interpolate data to regular grid
            if data.shape[1] > 1:
                data = np.array([np.interp(x_mhz, (freq_axis / 1e6), row) for row in data])
            # display with origin='lower' so newest is at top; flip if desired
            if img is None:
                extent = [x_mhz[0], x_mhz[-1], 0, data.shape[0]]
                img = ax_wf.imshow(data, aspect='auto', origin='lower', extent=extent, cmap='viridis')
                ax_wf.set_xlabel("Frequency (MHz)")
                ax_wf.set_ylabel("Sweeps (older->newer)")
            else:
                img.set_data(data)
                img.set_extent([x_mhz[0], x_mhz[-1], 0, data.shape[0]])
        last_update = time.time()

    ani = FuncAnimation(fig, update, interval=max(10, int(1000.0/args.fps)), cache_frame_data=False)
    def on_key(event):
        if event.key == 's':
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            if freq_axis is not None and len(buf)>0:
                np.savetxt(f"hackrf_snapshot_{ts}.csv", np.vstack((freq_axis, np.vstack(buf).mean(axis=0))).T,
                           delimiter=",", header="hz,db", comments='')
                fig.savefig(f"hackrf_snapshot_{ts}.png", dpi=150)
                print("Saved snapshot:", ts)
        elif event.key == 'r':
            # reset buffer (and envelope)
            buf.clear()
            print("Envelope and buffer reset")
    fig.canvas.mpl_connect('key_press_event', on_key)

    try:
        plt.show()
    finally:
        stop_event.set()
        try:
            proc.terminate()
        except Exception:
            pass

if __name__ == "__main__":
    main()
# ...existing code...