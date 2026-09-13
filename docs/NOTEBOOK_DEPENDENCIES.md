# Recorded installation cells

Extracted from selected notebooks, without claiming a single fully locked historical environment. Run each experiment in its own Colab runtime; follow its installation cell.

### notebooks/training/02_mms_full_specaugment.ipynb — original cell 1

```python
# Cell 1 — Install the exact same dependencies as the no-augmentation experiment

!pip -q install \
    "transformers==4.57.1" \
    "datasets==4.4.1" \
    "accelerate>=1.10,<2" \
    "jiwer==4.0.0" \
    "safetensors>=0.4.5" \
    "soundfile>=0.12.1"

print("✓ Dependencies installed.")
```

### notebooks/training/05_omniasr_full.ipynb — original cell 1

```python
# Cell 1 — Install the exact experiment dependencies

!pip -q install \
    "transformers==4.57.1" \
    "datasets==4.4.1" \
    "accelerate>=1.10,<2" \
    "jiwer==4.0.0" \
    "safetensors>=0.4.5" \
    "soundfile>=0.12.1"

print("✓ Dependencies installed.")
print("If Colab requests a restart after installation, restart once and continue from Cell 2.")

```

### notebooks/training/06_omniasr_half_spk009.ipynb — original cell 1

```python
# Cell 1 — Install dependencies
!pip -q install "transformers==4.57.1" "datasets==4.4.1" "accelerate>=1.10,<2" "jiwer==4.0.0" "safetensors>=0.4.5" "soundfile>=0.12.1"
print("✓ Dependencies installed.")

```

### notebooks/preparation/01_assisted_transcription.ipynb — original cell 2

```python
# ============================================================
# CELL 3: Install dependencies and check GPU
# ============================================================

!pip install -q transformers accelerate soundfile sentencepiece

import torch

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("Device:", DEVICE)

if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))
    print(
        "GPU memory:",
        round(
            torch.cuda.get_device_properties(0).total_memory / 1024**3,
            2
        ),
        "GB"
    )
```

### notebooks/preparation/02_test_transcription_drafts.ipynb — original cell 2

```python
# Cell 3 — Load the MMS-Tachebdant transcription assistant

!pip -q install transformers librosa soundfile

import torch
import librosa

from transformers import (
    AutoProcessor,
    AutoModelForCTC,
)

MODEL_ID = "iukocha/mms-tachebdant-from-tarifit"

device = (
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)

processor = AutoProcessor.from_pretrained(
    MODEL_ID
)

model = AutoModelForCTC.from_pretrained(
    MODEL_ID
).to(device)

model.eval()

print("Device:", device)
```

### notebooks/training/03_mms_specaugment_speed.ipynb — original cell 1

```python
# Cell 1 — Install the exact reproducible dependencies

!pip -q install \
    "transformers==4.57.1" \
    "datasets==4.4.1" \
    "accelerate>=1.10,<2" \
    "jiwer==4.0.0" \
    "safetensors>=0.4.5" \
    "soundfile>=0.12.1"

print("✓ Dependencies installed.")
print("If Colab asks for a runtime restart after installation, restart once and continue from Cell 2.")

```

### notebooks/diagnostics/02_historical_kenlm.ipynb — original cell 8

```python
# ============================================================
# CELL 9: Install CTC beam-search + KenLM dependencies
# ============================================================

!pip install -q pyctcdecode kenlm
```

### notebooks/diagnostics/02_historical_kenlm.ipynb — original cell 11

```python
# ============================================================
# FIX: Install KenLM properly in current Colab runtime
# ============================================================

!apt-get update -qq
!apt-get install -y -qq \
    build-essential \
    cmake \
    libboost-system-dev \
    libboost-thread-dev \
    libboost-program-options-dev \
    libboost-test-dev \
    libeigen3-dev \
    zlib1g-dev \
    libbz2-dev \
    liblzma-dev

# Install pyctcdecode separately
!pip install -q pyctcdecode

# Fresh KenLM source
!rm -rf /content/kenlm
!git clone -q https://github.com/kpu/kenlm.git /content/kenlm

# Build command-line tools
!mkdir -p /content/kenlm/build
!cd /content/kenlm/build && cmake .. > /dev/null
!cd /content/kenlm/build && make -j2 > /dev/null

# Install the Python bindings from the same source tree
!CMAKE_BUILD_PARALLEL_LEVEL=2 pip install -q /content/kenlm

print("KenLM installation attempt finished.")
```

### notebooks/diagnostics/02_historical_kenlm.ipynb — original cell 14

```python
# ============================================================
# REINSTALL clean Python binding
# ============================================================

!pip install -q --force-reinstall kenlm-ex

print("Reinstall finished.")
```

### notebooks/diagnostics/02_historical_kenlm.ipynb — original cell 16

```python
# ============================================================
# CELL 12: Install KenLM and pyctcdecode
# ============================================================

!pip install -q pyctcdecode kenlm

print("Installation finished.")
```

### notebooks/diagnostics/02_historical_kenlm.ipynb — original cell 35

```python
# ============================================================
# INSTALL jiwer
# ============================================================

!pip install -q jiwer

print("jiwer installed.")
```

### notebooks/training/10_kabyle_xlsr_full8_noaug.ipynb — original cell 1

```python
# Cell 1 — Install reproducible XLS-R V1.2 dependencies

!pip -q install "transformers==4.57.1" "datasets==4.4.1" "accelerate>=1.10,<2" "jiwer==4.0.0" "safetensors>=0.4.5" "soundfile>=0.12.1"

```

### notebooks/evaluation/01_main_test_comparison.ipynb — original cell 2

```python
# Cell 2 — Install evaluation dependencies
!pip install -q transformers accelerate jiwer soundfile safetensors sentencepiece scipy pandas tqdm

```

### notebooks/training/01_mms_full_noaug.ipynb — original cell 1

```python
# Cell 1 — Install reproducible dependencies
!pip -q install "transformers==4.57.1" "datasets==4.4.1" "accelerate>=1.10,<2" "jiwer==4.0.0" "safetensors>=0.4.5" "soundfile>=0.12.1"
```

### notebooks/training/04_mms_half_spk009.ipynb — original cell 1

```python
# Cell 1 — Install exact dependencies
!pip -q install "transformers==4.57.1" "datasets==4.4.1" "accelerate>=1.10,<2" "jiwer==4.0.0" "safetensors>=0.4.5" "soundfile>=0.12.1"
print("✓ Dependencies installed. Restart runtime once if Colab requests it.")

```

### notebooks/evaluation/02_kabyle_xlsr_comparison.ipynb — original cell 1

```python
# Cell 1 — Install the fixed evaluation dependencies

!pip -q install "transformers==4.57.1" "datasets==4.4.1" "accelerate>=1.10,<2" "jiwer==4.0.0" "safetensors>=0.4.5" "soundfile>=0.12.1"

```

### notebooks/training/09_xlsr_full8_noaug.ipynb — original cell 1

```python
# Cell 1 — Install reproducible XLS-R V1.2 dependencies

!pip -q install "transformers==4.57.1" "datasets==4.4.1" "accelerate>=1.10,<2" "jiwer==4.0.0" "safetensors>=0.4.5" "soundfile>=0.12.1"

```

### notebooks/training/08_fadhma_quarter_spk009.ipynb — original cell 1

```python
# Cell 1 — Install dependencies
!pip -q install "transformers==4.57.1" "datasets==4.4.1" "accelerate>=1.10,<2" "jiwer==4.0.0" "safetensors>=0.4.5" "soundfile>=0.12.1"
print("✓ Dependencies installed.")

```

### notebooks/diagnostics/01_xlsr_specaugment_blank_collapse.ipynb — original cell 1

```python
# Cell 1 — Install dependencies
!pip -q install "transformers==4.57.1" "datasets==4.4.1" "accelerate>=1.10,<2" "jiwer==4.0.0" "safetensors>=0.4.5" "soundfile>=0.12.1"
print("✓ Dependencies installed.")

```

### notebooks/training/07_fadhma_full.ipynb — original cell 1

```python
# Cell 1 — Install the exact experiment dependencies

!pip -q install \
    "transformers==4.57.1" \
    "datasets==4.4.1" \
    "accelerate>=1.10,<2" \
    "jiwer==4.0.0" \
    "safetensors>=0.4.5" \
    "soundfile>=0.12.1"

print("✓ Dependencies installed.")
print("If Colab requests a restart after installation, restart once and continue from Cell 2.")

```
