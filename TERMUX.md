# RIME v0.012 on Termux

## Open the package

After downloading `RIME_v0_012.zip`:

```bash
cd ~
unzip ~/storage/downloads/RIME_v0_012.zip
cd RIME_v0_012
```

Confirm:

```bash
ls
```

You should see `run_rime.py`, `rime`, `README.md`, and this file.

## Dependencies

If your previous RIME versions already run, you should not need anything new.

Otherwise:

```bash
pkg install python python-numpy python-pillow
python -m pip install mido
```

## Generate a normal track

```bash
python run_rime.py ~/storage/downloads/YOUR_IMAGE.png \
  --length 32 \
  --evolve 3 \
  --grid-mode layered \
  --rhythm-strength 3 \
  --visual-authority 2 \
  --solar-breakdown auto \
  --foreshadow auto \
  --max-stops 3 \
  --stop-window 80 \
  --output ~/storage/downloads/RIME
```

## Run the new mapping laboratory

For the complete transformation test:

```bash
python run_rime.py ~/storage/downloads/YOUR_IMAGE.png \
  --length 16 \
  --evolve 2 \
  --visual-authority 2 \
  --mapping-test full \
  --output ~/storage/downloads/RIME
```

The mapping-test folder inside `Download/RIME` will contain transformed images, audio, MIDI, genome JSON files, and the visual mapping report.

For a faster brightness-only test:

```bash
python run_rime.py ~/storage/downloads/YOUR_IMAGE.png --mapping-test brightness --output ~/storage/downloads/RIME
```
