import re
from pathlib import Path

CORRECTIONS = {
    r"\breikers\b": "hackers",
    r"\breiquer\b": "hacker",
    r"\buatsap\b": "WhatsApp",
    r"\bwhatsapp\b": "WhatsApp",
    r"\bsms\b": "SMS",
    r"\bpin\b": "PIN",
}

def normalize_pt_text(text: str) -> str:
    for pattern, repl in CORRECTIONS.items():
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
    return text.strip()

def format_ass_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def generate_karaoke_ass(audio_path: Path, ass_path: Path, model_size: str = "medium") -> Path:
    """Transcreve o áudio e gera legenda Karaoke (.ass) alinhada na zona direita (1920x1080)."""
    import torch
    import whisper

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = whisper.load_model(model_size, device=device)
    result = model.transcribe(
        str(audio_path),
        language="pt",
        word_timestamps=True,
        initial_prompt="Higiene cibernética, WhatsApp, hackers, engenharia social, SMS, código de seis dígitos, PIN, Angola."
    )

    # PrimaryColour = Verde (&H0066FF00 em BGR), SecondaryColour = Branco (&H00FFFFFF)
    # MarginL=720 e MarginR=220 mantém a legenda perfeitamente centrada sob o ecrã direito
    header = """[Script Info]
Title: MAM Cyber Lab Karaoke 16:9
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 1

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,46,&H0066FF00,&H00FFFFFF,&H00081420,&H80000000,-1,0,0,0,100,100,0,0,1,3,2,2,720,220,95,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    words_buffer = []

    for seg in result.get("segments", []):
        for w in seg.get("words", []):
            word_txt = normalize_pt_text(w["word"])
            if not word_txt:
                continue
            words_buffer.append((w["start"], w["end"], word_txt))
            if len(words_buffer) >= 5 or word_txt.endswith((".", "!", "?", ",")):
                start_t = format_ass_time(words_buffer[0][0])
                end_t = format_ass_time(words_buffer[-1][1])
                karaoke_line = ""
                for ws, we, wt in words_buffer:
                    dur_cs = max(10, int(round((we - ws) * 100)))
                    karaoke_line += f"{{\\k{dur_cs}}}{wt} "
                events.append(f"Dialogue: 0,{start_t},{end_t},Default,,0,0,0,,{karaoke_line.strip()}")
                words_buffer = []

    if words_buffer:
        start_t = format_ass_time(words_buffer[0][0])
        end_t = format_ass_time(words_buffer[-1][1])
        karaoke_line = "".join(f"{{\\k{max(10, int(round((we - ws) * 100)))}}}{wt} " for ws, we, wt in words_buffer)
        events.append(f"Dialogue: 0,{start_t},{end_t},Default,,0,0,0,,{karaoke_line.strip()}")

    ass_path.parent.mkdir(parents=True, exist_ok=True)
    ass_path.write_text(header + "\n".join(events) + "\n", encoding="utf-8")
    return ass_path
