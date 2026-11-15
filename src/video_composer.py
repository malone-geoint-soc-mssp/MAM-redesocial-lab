import subprocess
from pathlib import Path

def get_audio_duration(audio_path: Path) -> float:
    cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{audio_path}"'
    out = subprocess.check_output(cmd, shell=True).decode().strip()
    return float(out)

def build_branded_video(
    audio_path: Path,
    ass_path: Path,
    broll_clips: list[Path],
    background_img: Path,
    output_mp4: Path,
    banner_title: str = "HIGIENE CIBERNÉTICA • BLINDAGEM DE WHATSAPP"
) -> Path:
    """
    Compõe vídeo 1920x1080 usando background.png como palco fixo,
    projetando B-Rolls dinâmicos, audiograma verde (#00FF66) e legendas Karaoke à direita.
    """
    duration = get_audio_duration(audio_path)
    output_mp4.parent.mkdir(parents=True, exist_ok=True)

    # 1. Prepara e concatena os B-Rolls no tamanho do ecrã tático direito (980x520)
    clip_dur = duration / max(1, len(broll_clips))
    norm_clips = []
    for idx, clip in enumerate(broll_clips):
        norm_p = output_mp4.parent / f"tmp_broll_{idx}.mp4"
        cmd_norm = (
            f'ffmpeg -y -stream_loop -1 -i "{clip}" -t {clip_dur:.2f} '
            f'-vf "scale=980:520:force_original_aspect_ratio=increase,crop=980:520,fps=30,format=yuv420p" '
            f'-an "{norm_p}"'
        )
        subprocess.run(cmd_norm, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        norm_clips.append(norm_p)

    concat_list = output_mp4.parent / "concat_list.txt"
    concat_list.write_text("\n".join(f"file '{p.resolve()}'" for p in norm_clips) + "\n", encoding="utf-8")

    broll_track = output_mp4.parent / "tmp_broll_track.mp4"
    subprocess.run(
        f'ffmpeg -y -f concat -safe 0 -i "{concat_list}" -c copy "{broll_track}"',
        shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )

    # 2. Composição em camadas: Palco Marca + B-Roll + Audiograma Verde + Banner + Legenda Karaoke
    ass_escaped = str(ass_path).replace("\\", "/").replace(":", "\\:")
    filter_complex = (
        f"[0:v]scale=1920:1080[bg];"
        f"[1:v]pad=986:526:3:3:color=0x00FF66@0.85[broll_framed];"
        f"[bg][broll_framed]overlay=x=720:y=190:enable='gte(t,2.5)'[v1];"
        f"[2:a]showwaves=s=980x95:mode=cline:rate=30:colors=0x00FF66[waves];"
        f"[v1][waves]overlay=x=720:y=735[v2];"
        f"[v2]drawbox=x=720:y=115:w=980:h=60:color=0x061320@0.90:t=fill,"
        f"drawtext=text='{banner_title}':fontcolor=0x00FF66:fontsize=27:x=745:y=132,"
        f"ass='{ass_escaped}'[v_out]"
    )

    cmd_final = (
        f'ffmpeg -y -loop 1 -i "{background_img}" -i "{broll_track}" -i "{audio_path}" '
        f'-filter_complex "{filter_complex}" '
        f'-map "[v_out]" -map 2:a -c:v libx264 -preset medium -crf 20 -c:a aac -b:a 192k -t {duration:.2f} "{output_mp4}"'
    )
    subprocess.run(cmd_final, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    for tmp in norm_clips + [concat_list, broll_track]:
        if tmp.exists():
            tmp.unlink()

    return output_mp4
