from pathlib import Path

import pandas as pd
import soundfile as sf


# --------------------------------------------------
# Project paths
# --------------------------------------------------

PROJECT_ROOT = Path("/Users/mac/masterAI/tarifit_asr_tfm")

INPUT_AUDIO = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "wav_16khz_mono"
    / "tenni_yeccin_mmis.wav"
)

OUTPUT_SEGMENTS_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "segments"
    / "REC138"
)

OUTPUT_METADATA = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "rec138_awal_validation.csv"
)

MASTER_METADATA = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "segments_metadata.csv"
)


# --------------------------------------------------
# New recording information
# --------------------------------------------------

RECORDING_ID = "REC138"
SPEAKER_ID = "SPK010"


# --------------------------------------------------
# Awal transcription
# start, end, transcription
# --------------------------------------------------

segments = [
    (3, 6, "ffɣent ij n třata n tḥenjirin ɣar řeɛrassi"),
    (6, 9, "beddent ṭṭarf i ij n ufeddan n yirden"),
    (9, 14, "beddent ṭṭarf i ufeddan nni n yirden"),
    (14, 19, "u ca tenna as icten tenna as, afeddan ittsemma bayen illa bab nnes labas xas"),
    (19, 22, "iḍehhar dd, tammurt d tameqqrant, ij n ufeddan n yirden ila axirih"),
    (22, 26, "tuɣa deg ij n řweqt xmi dd ɣa taweḍ ṣṣabeyt ittɛawad řemřak"),
    (26, 29, "ij n teḥrant, icten zzaysent tennas mařa yiwey ayi bab n ufeddan a"),
    (29, 34, "ad as ggeɣ tamarraqt s ij n tḥebbuyt n ubaw"),
    (34, 39, "tenn n iḍen tennas aweddi necc mařa yiwey ayi bab n winat a eh bab n ufeddan a"),
    (39, 45, "ad as ggeɣ ij n winat ittsemma ij n teknift s ij n tḥebbuyt n irden"),
    (45, 49, "ten n nneḍni wis třata tenna as mařa yiwey ayi ad as jjeɣ aḥenjir dayes duru di tenyart"),
    (49, 51, "duru di tenyart ixs ad yinni bi'annahu dayes zzin, niɣ dayes ittecceɣ dd zzayes zzin"),
    (51, 53, "qqarn as ma ɣars duru di tneyart"),
    (54, 55, "xenni bab nni n ufeddan tuɣa ittesřa yasent"),
    (56, 67, "yiwey itent s třata"),
    (68, 75, "lmuhim ařami tent yiwey ila axirih inna as i tenni d as innan ad as ggeɣ ij n teknift s ij n řḥebbet n irden, inna as iwa egg ayi taknift ij n teknift nni egg ayi tt s ij n tḥebbuyt n irden, teɛjez, war tzemmar"),
    (76, 81, "inna as i ten nneḍni i d as innan ad as ggeɣ tamarraqt s ij n tḥebbuyt n ubaw inna as iwa egg dd tamarraqt s ij n tḥebbuyt n ubaw!"),
    (81, 84, "ttɣiř as .. ɛala ayyin, ten nneḍni ha ɛejzent s tnayen idsent"),
    (84, 94, "ten nnezḍni i d as innan ad as dd jjeɣ aḥenjir ɣars duru di tenyart"),
    (95, 99, "ad rajan ař ɣa taṛu, li'annahu war ssinen ca mamek dd ɣa ixřeq uḥenjir nni; fiɛlan ařmi dd ixřeq uḥenjir nni, ixřeq dd ɣars duru di tenyart"),
    (99, 101, "xenni u t iẓrin amezwaru d tnayen nni n teḥramin tnayenni n temɣarin nni"),
    (101, 103, "ɣirnt zzayes li'annahu"),
    (103, 107, "mya di mya ad xasent yazzeř"),
    (107, 116, "ařami tenni tkemmeř awař nnes tejja dd aḥram ɣars duru di tenyart"),
    (117, 119, "walakin tin nnedni ɛejzent, idan fekkarnt nitenti biannahu xminni ɣa xmi dd ɣa yas ad yaf nican nitenti ad xasent yazzeř ad ijj illa tenni ikemmřen awař"),
    (120, 126, "min xeḏment? fekkarent xarrasent jarrasent"),
    (126, 129, "ksint aḥenjir nni, ittsemma, wyen net ɣar ij n twessart, beɛɛdent yeɛni ukarn t"),
    (129, 132, "qessent cway n winat tiřeṭṭ nnes"),
    (133, 142, "ggin t as deg uqemmum i temɣart nni yurwen"),
    (143, 154, "ař ami d as ɣa ggent ggint as cwayt n idammen deg uqemmum ammu, min das nnant? nnant as aqa tuṛu it aqa tecca mmis, amenni i d as nnant i wargaz nni nnant as aqa tuṛu aqa tecci t"),
    (154, 158, "lmuhimm ṣafi netta iqtaneɛ bi'annahu aqa fiɛlan ila axirih, yufa idammen deg uqemmum nnes inna as aqa aqa tecca mmis war xas yuzziř ca ijji tt txeddem di taddart"),
    (158, 184, "tteṭṭes di deg winat tteṭṭes di...mamek d as qqarn di tɣaɣart"),
    (184, 190, "ttrass, ttɛic ij n lḥayat cwat teqseḥ, lmuhimm igga as ɛuquba. aḥenjir nni ittsemma imɣar dd tuɣa ddcar nni awmi tenni umi tewcin t imɣar dd, imɣar ila axirih.. ibda ittirar ag iqqrinen nnes, nnan as a weddi aqa cek qa yinni i ɣa ttɛiced aqa war llint ca d yemmak d babak, lmuhimm kuř marra iqqar as i tenni t yarbban, iqqar as ixeṣṣ ad ayi tinid manwen illan d baba, aqa qaɛ iḥramen i ked ttirarɣ qqarn ayi aqa wenni yinni war illi ca war illi ca d yemmak d babak.. u labudda li'anna bnadem yarzzu x l'aṣl"),
    (190, 194, "ittsemma tufa kuř nnhar kuř nnhar kuř nnhar tenna as lḥaqiqa, tenna as ha min iweqɛen ha min iweqɛen ha min iweqɛen"),
    (194, 197, "lmuhimm ittsemma iqerrer bac ad iraḥ ad yarzu x yemmas d babas"),
    (197, 201, "min kides yiwi? yiwey akides tɣaṭ"),
    (202, 205, "iwey akides sslugi, yiwey akides ḥacakum aqzin"),
    (206, 208, "u ca iruḥ ttsemma di arriḥla bac ad yarzu x babas d yemmas"),
    (209, 210, "i xenni jjmaɛet i xef ɣa ikk niɣ ddcar"),
    (210, 223, "qqarn as subḥanllah"),
    (224, 228, "li'anna tɣaṭ war ttmun tɣaṭ war ttmun ag wuccen, uccen war ittmun ag weqzin, lmuhimm ddegg a ca n řḥajet aqa tt dayes, xenni qqarn as subḥanallah, netta ittarra dd xasen iqqar asen tamɣart tecca mmis, idan mařa yina war ttmunen mamek tegga tamɣart a i ɣa yeccen mmis?"),
    (229, 231, "lmuhimm yallah zid zid ad awem xtaṣarɣ, yallah yallah ḥetta ařami yiweḍ ddcar nni i di ittɛic"),
    (231, 251, "ittsemma babas d yemmas ḥaqiqiyyin"),
    (251, 274, "lmuhimm iruḥ ɣars ɣar babas nni, ittar as ḍifllah, issidef it ila axirih inna as aqa necc aqa, igga axmi d anewji waha, inna as qa xseɣ tamɣart nni ittrassen itteṭṭsen di tɣaɣart xseɣ ad kidneɣ t.. ad kidneɣ teqqim, řami teqqim temɣart nni ikkes tcacciyt ammu, teẓri t dayes mamek d as qqarn duru di tenyart"),
    (275, 276, "i xenni issnen ittsemma illa d mmis illa netta d mmis, i d as iɛawed i babas lḥikaya amek, mamek tewqeɛ, i xenni inna as i temɣart nni i řexxu ḥkem xasent s tnayen i d am iggin ittsemma danita, teḥkem xasent ad qqiment lmudda nni i teqqim nettat tkaṛfeṣ marra ttrass di tɣaɣart ila axirih lmudda nni .. xmi ɣa tekemmeř lmudda nni ad dd awyen iksan ad tent ssekken x winat x uɣanim iqess.."),
    (276, 285, "ɣanim d aziza ad t qessen"),
    (276, 285, "ad tent ssekkent sennej nsent, ittsemma teḥkem xasent s l'iɛdam, ittsemma, d wa d lɛuquba i d asent tegga temɣart nni, u ca iqqim lmatal iqqar as sebḥanallah tamɣart tecca mmis"),
]


# --------------------------------------------------
# Safety checks
# --------------------------------------------------

master = pd.read_csv(MASTER_METADATA)

if RECORDING_ID in set(master["recording_id"].astype(str)):
    raise ValueError(
        f"{RECORDING_ID} already exists in segments_metadata.csv. "
        "Choose another recording_id."
    )

if SPEAKER_ID in set(master["speaker_group_id"].astype(str)):
    raise ValueError(
        f"{SPEAKER_ID} already exists in segments_metadata.csv. "
        "Choose another speaker_group_id."
    )

if not INPUT_AUDIO.exists():
    raise FileNotFoundError(INPUT_AUDIO)


# --------------------------------------------------
# Load audio
# --------------------------------------------------

audio, sr = sf.read(INPUT_AUDIO)

if sr != 16000:
    raise ValueError(f"Expected 16000 Hz, found {sr} Hz")

if audio.ndim > 1:
    raise ValueError("Expected mono audio")

audio_duration = len(audio) / sr

print(f"Source duration: {audio_duration:.2f} s")


# --------------------------------------------------
# Create output directory
# --------------------------------------------------

OUTPUT_SEGMENTS_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# Cut segments and create metadata
# --------------------------------------------------

rows = []

for i, (start, end, transcription) in enumerate(segments, start=1):

    if end > audio_duration:
        raise ValueError(
            f"Segment {i}: end={end}s exceeds audio duration "
            f"{audio_duration:.2f}s"
        )

    segment_id = f"{RECORDING_ID}_SEG{i:04d}"
    filename = f"{segment_id}.wav"

    output_path = OUTPUT_SEGMENTS_DIR / filename

    start_sample = int(round(start * sr))
    end_sample = int(round(end * sr))

    segment_audio = audio[start_sample:end_sample]

    sf.write(
        output_path,
        segment_audio,
        sr,
        subtype="PCM_16"
    )

    duration = end - start

    rows.append(
        {
            "segment_id": segment_id,
            "recording_id": RECORDING_ID,
            "speaker_group_id": SPEAKER_ID,
            "dataset_split": "validation",
            "segmentation_version": "awal_original_v1",
            "start_seconds": float(start),
            "end_seconds": float(end),
            "duration_seconds": float(duration),
            "audio_path": str(
                output_path.relative_to(PROJECT_ROOT)
            ),
            "review_status": "needs_review",
            "transcription": transcription.strip(),
            "final_selection": "no",
        }
    )


# --------------------------------------------------
# Save staging metadata
# --------------------------------------------------

df = pd.DataFrame(rows)

df.to_csv(
    OUTPUT_METADATA,
    index=False,
    encoding="utf-8"
)


# --------------------------------------------------
# Report
# --------------------------------------------------

print("\nCreated:", len(df), "segments")
print(
    "Total segmented duration:",
    round(df["duration_seconds"].sum(), 2),
    "seconds"
)
print(
    "Total segmented duration:",
    round(df["duration_seconds"].sum() / 60, 2),
    "minutes"
)

long_segments = df[df["duration_seconds"] > 20]

print("\nSegments > 20 seconds:", len(long_segments))

if len(long_segments):
    print(
        long_segments[
            [
                "segment_id",
                "start_seconds",
                "end_seconds",
                "duration_seconds",
            ]
        ].to_string(index=False)
    )

print("\nSegments saved to:")
print(OUTPUT_SEGMENTS_DIR)

print("\nStaging CSV saved to:")
print(OUTPUT_METADATA)