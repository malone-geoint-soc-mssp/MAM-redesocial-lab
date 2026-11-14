import os
import re
import subprocess
from pathlib import Path
from config.settings import VOICE_LANGUAGE, TARGET_LUFS, VOICE_REF_DIR

def prepare_voice_reference(raw_audio_path: Path, output_name: str = "ref_malone.wav") -> Path:
    """Extrai um trecho limpo de 18s contínuos sem silêncios longos para máxima fidelidade vocal."""
    VOICE_REF_DIR.mkdir(parents=True, exist_ok=True)
    ref_path = VOICE_REF_DIR / output_name
    # Remove silêncios intermediários e recorta 18 segundos densos da voz (entre 00:05 e 00:23)
    cmd = (
        f'ffmpeg -y -i "{raw_audio_path}" -vn -ac 1 -ar 22050 '
        f'-af "highpass=f=90,lowpass=f=8000,silenceremove=stop_periods=-1:stop_duration=0.35:stop_threshold=-38dB,atrim=start=3:duration=18" '
        f'"{ref_path}"'
    )
    subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return ref_path

def sanitize_text_for_tts(text: str) -> str:
    """Evita que o sintetizador leia pontuação colada a siglas (ex: 'SMS.' -> 'ponto SMS')."""
    text = re.sub(r'\bSMS\b', 'S M S', text)
    text = re.sub(r'\b2FA\b', 'autenticação em dois fatores', text)
    text = re.sub(r'\biOS\b', 'i O S', text)
    return text.strip()

def synthesize_speech(text: str, output_wav: Path, ref_wav: Path | None = None) -> Path:
    """Gera fala clonando a voz de referência com parâmetros de alta aderência ao timbre."""
    import torch
    from TTS.api import TTS

    os.environ["COQUI_TOS_AGREED"] = "1"
    speaker_path = ref_wav or (VOICE_REF_DIR / "ref_malone.wav")
    if not speaker_path.exists():
        raise FileNotFoundError(f"Amostra de voz não encontrada em: {speaker_path}")

    output_wav.parent.mkdir(parents=True, exist_ok=True)
    raw_tts_path = output_wav.with_name(f"raw_{output_wav.name}")
    clean_text = sanitize_text_for_tts(text)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
    tts.tts_to_file(
        text=clean_text,
        speaker_wav=str(speaker_path),
        language=VOICE_LANGUAGE,
        file_path=str(raw_tts_path),
        temperature=0.35,
        repetition_penalty=5.0,
        speed=1.0
    )

    cmd_master = (
        f'ffmpeg -y -i "{raw_tts_path}" -ar 44100 -ac 1 '
        f'-af "highpass=f=85,loudnorm=I={TARGET_LUFS}:LRA=7:TP=-1.5" '
        f'"{output_wav}"'
    )
    subprocess.run(cmd_master, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if raw_tts_path.exists():
        raw_tts_path.unlink()

    return output_wav
