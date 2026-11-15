import subprocess
from pathlib import Path
from config.settings import TARGET_LUFS

def master_voice_audio(raw_audio_path: Path, output_wav: Path) -> Path:
    """
    Aplica cadeia de masterização DSP broadcast na gravação original:
    1. Corte automático de silêncios mortos no início e no fim.
    2. Filtro passa-alta (85Hz) e passa-baixa (12kHz) para limpeza de ruído de sala.
    3. Compressão dinâmica suave para nivelar a voz.
    4. Normalização EBU R128 (-14 LUFS) padrão Reels/TikTok/LinkedIn.
    """
    if not raw_audio_path.exists():
        raise FileNotFoundError(f"Áudio bruto não encontrado em: {raw_audio_path}")

    output_wav.parent.mkdir(parents=True, exist_ok=True)

    dsp_chain = (
        "silenceremove=start_periods=1:start_duration=0.05:start_threshold=-45dB,"
        "areverse,silenceremove=start_periods=1:start_duration=0.05:start_threshold=-45dB,areverse,"
        "highpass=f=85,lowpass=f=12000,"
        "acompressor=threshold=-18dB:ratio=3:attack=10:release=100:makeup=2,"
        f"loudnorm=I={TARGET_LUFS}:LRA=7:TP=-1.5"
    )

    cmd = (
        f'ffmpeg -y -i "{raw_audio_path}" -vn -ar 44100 -ac 1 '
        f'-af "{dsp_chain}" "{output_wav}"'
    )
    subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_wav

if __name__ == "__main__":
    print("🎙️ Motor de Masterização DSP (Voz Real) pronto.")
