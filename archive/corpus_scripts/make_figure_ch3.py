import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np

# Replace these with one real segment from your corpus
wav_path = "//Users/mac/masterAI/tarifit_asr_tfm/data/pilot_audio/REC036_SEG0016.wav"
transcript = "l kara wanitin aneɣ yawi a rejḍuḍ nneɣ anza mux ira ddan mux ira tiɛicen"

# Load audio at the project sampling rate
y, sr = librosa.load(wav_path, sr=16000, mono=True)
duration = len(y) / sr
time = np.linspace(0, duration, len(y))

# Create log-Mel spectrogram
mel = librosa.feature.melspectrogram(
    y=y,
    sr=sr,
    n_fft=400,
    hop_length=160,
    n_mels=80,
    fmin=0,
    fmax=8000
)

log_mel = librosa.power_to_db(mel, ref=np.max)

# Create figure
fig, axes = plt.subplots(
    3, 1,
    figsize=(12, 8),
    gridspec_kw={"height_ratios": [1, 2, 0.8]}
)

# Waveform
axes[0].plot(time, y, color="steelblue", linewidth=0.7)
axes[0].set_title("Waveform")
axes[0].set_ylabel("Amplitude")
axes[0].set_xlim(0, duration)

# Log-Mel spectrogram
img = librosa.display.specshow(
    log_mel,
    sr=sr,
    hop_length=160,
    x_axis="time",
    y_axis="mel",
    fmax=8000,
    cmap="magma",
    ax=axes[1]
)
axes[1].set_title("Log-Mel spectrogram")
axes[1].set_ylabel("Mel frequency")
fig.colorbar(img, ax=axes[1], format="%+2.0f dB")

# Transcript panel
axes[2].axis("off")
axes[2].text(
    0.5, 0.5,
    transcript,
    ha="center",
    va="center",
    fontsize=15,
    wrap=True
)
axes[2].set_title("Normalized transcript")

plt.tight_layout()
plt.savefig("figure_3_1_waveform_spectrogram_transcript.png", dpi=300)
plt.show()