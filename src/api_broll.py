import requests
from pathlib import Path
from config.settings import PEXELS_API_KEY, PIXABAY_API_KEY, BROLL_CACHE_DIR

def fetch_from_pexels(query: str, out_path: Path) -> bool:
    if not PEXELS_API_KEY or "sua_chave" in PEXELS_API_KEY:
        return False
    url = f"https://api.pexels.com/videos/search?query={requests.utils.quote(query)}&per_page=3"
    headers = {"Authorization": PEXELS_API_KEY}
    try:
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code != 200:
            return False
        for video in res.json().get("videos", []):
            for vf in video.get("video_files", []):
                if vf.get("quality") == "hd" and vf.get("file_type") == "video/mp4":
                    video_bytes = requests.get(vf["link"], timeout=30).content
                    out_path.write_bytes(video_bytes)
                    return True
    except Exception as e:
        print(f"[Pexels] Erro na busca '{query}': {e}")
    return False

def fetch_from_pixabay(query: str, out_path: Path) -> bool:
    if not PIXABAY_API_KEY or "sua_chave" in PIXABAY_API_KEY:
        return False
    url = f"https://pixabay.com/api/videos/?key={PIXABAY_API_KEY}&q={requests.utils.quote(query)}&per_page=3"
    try:
        res = requests.get(url, timeout=15)
        if res.status_code != 200:
            print(f"[Pixabay] Status HTTP inesperado: {res.status_code}")
            return False
        hits = res.json().get("hits", [])
        if hits:
            videos_dict = hits[0].get("videos", {})
            video_url = (
                videos_dict.get("medium", {}).get("url")
                or videos_dict.get("small", {}).get("url")
                or videos_dict.get("large", {}).get("url")
            )
            if video_url:
                video_bytes = requests.get(video_url, timeout=30).content
                out_path.write_bytes(video_bytes)
                return True
    except Exception as e:
        print(f"[Pixabay] Erro na busca '{query}': {e}")
    return False

def get_broll_video(query: str, filename: str) -> Path | None:
    BROLL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    out_path = BROLL_CACHE_DIR / filename

    if fetch_from_pexels(query, out_path):
        print(f"✔ [Pexels] Vídeo descarregado: {out_path}")
        return out_path

    if fetch_from_pixabay(query, out_path):
        print(f"✔ [Pixabay] Vídeo descarregado: {out_path}")
        return out_path

    print(f"❌ Nenhuma API retornou vídeo para: '{query}'")
    return None

if __name__ == "__main__":
    print("🔎 A testar ligação com APIs de B-Roll (termo: 'cybersecurity code')...")
    resultado = get_broll_video("cybersecurity code", "teste_fase1.mp4")
    if resultado and resultado.exists():
        tamanho_kb = resultado.stat().st_size / 1024
        print(f"✅ VALIDAÇÃO FASE 1 CONCLUÍDA! Ficheiro guardado ({tamanho_kb:.1f} KB).")
    else:
        print("⚠️ Falha na validação. Verifique a chave no ficheiro .env.")
