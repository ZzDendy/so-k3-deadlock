#!/usr/bin/env bash
# Bukti terminal asli untuk laporan K-3: perhitungan Banker dijalankan di terminal.
set -u
DIR=${1:?butuh folder kerja}; OUT=${2:?butuh folder keluaran}
FIFO=/tmp/shotest/k3.fifo; mkdir -p "$OUT"; rm -f "$FIFO"; mkfifo "$FIFO"
cd "$DIR" || exit 1
io.elementary.terminal -n -w "$DIR" -x "bash --noprofile --rcfile $HOME/.bashrc -i < $FIFO" > /dev/null 2>&1 &
TERM_PID=$!; sleep 4; exec 3>"$FIFO"
tangkap() { sleep 0.9; gdbus call --session --dest org.gnome.Shell.Screenshot --object-path /org/gnome/Shell/Screenshot --method org.gnome.Shell.Screenshot.ScreenshotWindow true false false "$OUT/ss-$1.png" > /dev/null 2>&1; echo "  -> ss-$1.png"; }
ketik() { printf '%s\n' "$1" >&3; }
ketik 'clear'; sleep 1; tangkap "01-prompt"
ketik 'python3 banker.py --periksa'; sleep 3; tangkap "02-hitung"
ketik 'head -20 results/banker.json'; tangkap "03-keluaran"
ketik '../.venv/bin/python figures.py'; sleep 2; tangkap "04-gambar"
exec 3>&-; sleep 1; kill "$TERM_PID" 2>/dev/null; rm -f "$FIFO"
echo "selesai: $(ls -1 "$OUT"/ss-*.png | wc -l) tangkapan layar"
