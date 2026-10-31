<br />
<div align="center">
  <a href="https://github.com/ayoubzulfiqar/clipit">
    <img src="assets/images/clipit-logo-8x.png" alt="Logo" width="350">
  </a>

  <h3 align="center">Clipit</h3>

  <p align="center">
    <strong>Ultimate AI Auto-Clipper & Teaser Generator</strong><br>
    긴 영상을 Hook, 카라오케 자막, 자동 썸네일이 포함된 시네마틱 숏폼 클립으로 변환하는 오픈소스 콘텐츠 팩토리.
    <br />
    <br />
    <a href="README.md">🇬🇧 English</a>
    &middot;
    <a href="README_AR.md">🇸🇦 العربية</a>
    &middot;
    <a href="README_RU.md">🇷🇺 Русский</a>
    &middot;
    <a href="README_ZH.md">🇨🇳 中文</a>
    &middot;
    <a href="README_KO.md">🇰🇷 한국어</a>
    &middot;
    <a href="https://github.com/ayoubzulfiqar/clipit/issues/new">버그 신고</a>
    &middot;
    <a href="https://github.com/ayoubzulfiqar/clipit/issues/new">기능 요청</a>
  </p>
</div>

---

🟢 **적극 유지보수 중**: 기여, 버그 리포트, PR 환영.

---

## ✨ 기능

| 기능 | 설명 |
|---|---|
| **AI Transcriber** | Faster-Whisper (large-v3) 를 이용한 단어 단위 전사 |
| **AI Content Curator** | Gemini 가 맥락을 분석하고 바이럴 순간을 선택, 메타데이터 생성 |
| **Smart Auto-Framing** | MediaPipe 얼굴 추적, Smooth Pan, Deadzone |
| **Cinematic Teaser Hook** | 3초 Hook, 다크 오버레이, TV Glitch 전환 |
| **Karaoke Subtitles** | 단어 단위 하이라이트 .ASS 자막 |
| **Kinetic Typography** | AI 기반 단어 강조, bounce/stagger 애니메이션 |
| **B-Roll Integration** | Pexels 에서 stock footage 자동 가져오기 |
| **Multi-Hook Intro (V2)** | 3-4 개의 고유지 마이크로 Hook |
| **Smart Segment Trimming** | AI 가 최적 세그먼트 선택 |
| **Auto-BGM & Ducking** | 로컬 BGM 풀, sidechain ducking 또는 배경 모드 |
| **Auto-Thumbnail** | 다크 오버레이 + 큰 제목 텍스트 프레임 추출 |
| **Watermark Engine** | 텍스트/이미지 워터마크, 9개 앵커 |
| **Cross-Platform Metadata** | YouTube 제목/설명/태그 + TikTok 캡션 |
| **Auto YouTube Uploader** | 스케줄링 지원 자동 업로드 |
| **Auto Facebook Reels Uploader** | Facebook Pages 에 Reels 업로드, 스마트 스케줄링 |
| **Podcast Split-Screen** | 자동 화자 분리, 상하 split-screen |
| **Podcast Camera Switch** | 자동 활성 화자 감지 |
| **AI Voice-Over** | Gemini + edge-tts 로 코멘터리 트랙 생성 |

> 🎬 **신규: Story Clip Mode (`--story-mode`)**  
> 👉 **[Story Clip 문서 읽기](docs/STORY_CLIP.md)**

## 📋 사전 요구사항

- Python 3.10+
- FFmpeg 설치 및 PATH 등록
- CUDA GPU 권장 (CPU fallback 가능)
- Google Gemini API Key

## 🚀 설치

```bash
git clone https://github.com/ayoubzulfiqar/clipit.git
cd clipit
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.sample .env
# .env 에 GOOGLE_API_KEY 추가
```

## 🎬 사용법

```bash
python main.py --url "https://youtube.com/watch?v=..." --clips 5 --ratio 9:16
python main.py --url "url1" "url2" "url3" --clips 3
python main.py --story-mode --story-recipe story_recipe.json --sources-json sources.json
```

## 📄 라이선스

본 프로젝트는 GNU AGPLv3 License 하에 배포됩니다 — [LICENSE](LICENSE) 파일 참조.

Copyright (c) 2026 Ayoub Zulfiqar