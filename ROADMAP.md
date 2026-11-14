# Roadmap de Engenharia — MAM-redesocial-lab

Laboratório automatizado de produção de vídeos e audiogramas educativos sobre Higiene Cibernética e OSINT, focado no mercado angolano.

---

## Regras de Governança do Projeto
1. **Execução Sequencial:** Nenhuma fase avança sem a validação técnica da fase anterior.
2. **Zero Hardcoding:** Todas as chaves de API residem exclusivamente no ficheiro `.env`.
3. **Padrão de Saída:** Todos os vídeos renderizados devem garantir dimensões pares (`scale=x:-2`) e áudio normalizado em `-14 LUFS` (padrão EBU R128).

---

## Fase 1: Configuração de Ambiente & Validação das APIs de Mídia (B-Roll)
**Objetivo:** Garantir a obtenção automatizada e sem falhas de clipes de vídeo e imagens HD via APIs dedicadas.
- [x] **1.1** Configurar chaves `PEXELS_API_KEY` e `PIXABAY_API_KEY` no ficheiro `.env`.
- [x] **1.2** Implementar `config/settings.py` para leitura segura das variáveis de ambiente.
- [x] **1.3** Desenvolver `src/api_broll.py` com função de pesquisa por palavras-chave, download automático e tratamento de *fallback* (caso a API falhe ou não encontre resultados).
- [x] **Critério de Validação:** Executar teste unitário que recebe o termo `"cybersecurity code"` e guarda um ficheiro `.mp4` válido em `assets/broll_cache/`.

---

## Fase 2: Motor de Clonagem de Voz & Masterização DSP
**Objetivo:** Gerar narração natural em Português clonando o timbre vocal do autor a partir de um roteiro em texto.
- [ ] **2.1** Calibrar e validar o ficheiro de referência vocal (`config/voice_ref/ref_malone.wav` — 15 a 30s, mono, 22050Hz, sem ruído).
- [ ] **2.2** Desenvolver `src/voice_engine.py` utilizando XTTS-v2 (compatível com GPU Colab/Local).
- [ ] **2.3** Integrar pós-processamento DSP (`highpass`, redução de ruído e normalização `loudnorm` a `-14 LUFS`).
- [ ] **Critério de Validação:** Gerar um áudio `.wav` de teste a partir de uma frase e confirmar clareza vocal, pronúncia em Português e volume padronizado.

---

## Fase 3: Motor de Transcrição & Legendas Dinâmicas (.ASS)
**Objetivo:** Sincronizar automaticamente o áudio gerado com legendas estilo Karaoke e marcações de tempo.
- [ ] **3.1** Desenvolver `src/subtitle_engine.py` usando `openai-whisper` com `word_timestamps=True`.
- [ ] **3.2** Criar dicionário de sanitização ortográfica para termos técnicos e locais (ex: `MULTICAIXA Express`, `OSINT`, `2FA`, `Phishing`, `iOS`).
- [ ] **3.3** Gerar ficheiros `.ass` com estilos visuais de alto contraste e cabeçalho editorial.
- [ ] **Critério de Validação:** Gerar um ficheiro `.ass` a partir do áudio da Fase 2 e verificar a precisão dos *timestamps* e da grafia.

---

## Fase 4: Motor de Composição & Renderização Final (FFmpeg)
**Objetivo:** Unir todas as camadas num produto final pronto para publicação (1080x1080 ou 1080x1920).
- [ ] **4.1** Desenvolver `src/video_composer.py` construindo dinamicamente o `filter_complex` do FFmpeg.
- [ ] **4.2** Integrar camadas: Fundo escuro editorial + B-Rolls sincronizados por cena + Retrato/Branding + Onda sonora reativa (`showwaves`) + Legendas `.ass`.
- [ ] **4.3** Garantir compatibilidade de codificação (`libx264`, `yuv420p`, dimensões pares).
- [ ] **Critério de Validação:** Renderizar o Episódio 01 completo em `output/` sem erros de execução (`exit status 0`).

---

## Fase 5: Orquestração & Portabilidade (WSL <-> Google Colab)
**Objetivo:** Permitir execução com um único comando a partir de ficheiros JSON de roteiro.
- [ ] **5.1** Criar `main.py` para ler `episodes/ep01.json` e executar sequencialmente as Fases 1 a 4.
- [ ] **5.2** Criar notebook conector para puxar o repositório Git diretamente no Google Colab (GPU T4) para renderização acelerada.
- [ ] **Critério de Validação:** Produzir um episódio completo do zero alterando apenas o ficheiro JSON de entrada.
