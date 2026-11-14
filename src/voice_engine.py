import os
import subprocess
from pathlib import Path
from config.settings import VOICE_LANGUAGE, TARGET_LUFS, VOICE_REF_DIR

def prepare_voice_reference(raw_audio_path: Path, output_name: str = "ref_malone.wav") -> Path:
    """Converte e limpa a amostra de voz para o padrão ideal do XTTS-v2 (mono, 22050Hz)."""
    VOICE_REF_DIR.mkdir(parents=True, exist_ok=True)
    ref_path = VOICE_REF_DIR / output_name
    cmd = (
        f'ffmpeg -y -i "{raw_audio_path}" -vn -ac 1 -ar 22050 '
        f'-af "highpass=f=85,silenceremove=start_periods=1:start_duration=0.1:start_threshold=-40dB" '
        f'"{ref_path}"'
    )
    subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return ref_path

def synthesize_speech(text: str, output_wav: Path, ref_wav: Path | None = None) -> Path:
    """Gera fala em Português clonando a voz de referência e aplica masterização EBU R128."""
    import torch
    from TTS.api import TTS

    os.environ["COQUI_TOS_AGREED"] = "1"
    speaker_path = ref_wav or (VOICE_REF_DIR / "ref_malone.wav")
    if not speaker_path.exists():
        raise FileNotFoundError(f"Amostra de voz não encontrada em: {speaker_path}")

    output_wav.parent.mkdir(parents=True, exist_ok=True)
    raw_tts_path = output_wav.with_name(f"raw_{output_wav.name}")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
    tts.tts_to_file(
        text=text,
        speaker_wav=str(speaker_path),
        language=VOICE_LANGUAGE,
        file_path=str(raw_tts_path)
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
