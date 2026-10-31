<br />
<div align="center">
  <a href="https://github.com/ayoubzulfiqar/clipit">
    <img src="assets/images/clipit-logo-8x.png" alt="Logo" width="350">
  </a>

  <h3 align="center">Clipit</h3>

  <p align="center">
    <strong>Ultimate AI Auto-Clipper & Teaser Generator</strong><br>
    Open-source фабрика контента, превращающая длинные видео в кинематографические короткие клипы с хуками, караоке-субтитрами и авто-миниатюрами.
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
    <a href="https://github.com/ayoubzulfiqar/clipit/issues/new">Сообщить об ошибке</a>
    &middot;
    <a href="https://github.com/ayoubzulfiqar/clipit/issues/new">Предложить функцию</a>
  </p>
</div>

---

🟢 **Активно поддерживается**: приветствуются контрибьюции, баг-репорты и PR.

---

## ✨ Возможности

| Функция | Описание |
|---|---|
| **AI Transcriber** | Потранскрипт на уровне слов с Faster-Whisper (large-v3) |
| **AI Content Curator** | Gemini анализирует контекст и выбирает вирусные моменты |
| **Smart Auto-Framing** | Отслеживание лица через MediaPipe с Smooth Pan и Deadzone |
| **Cinematic Teaser Hook** | 3-секундный хук с тёмным оверлеем и TV Glitch |
| **Karaoke Subtitles** | Слово-за-словом подсвеченные .ASS субтитры |
| **Kinetic Typography** | AI-выделение слов с bounce/stagger анимациями |
| **B-Roll Integration** | Автозагрузка стокового видео из Pexels |
| **Multi-Hook Intro (V2)** | 3-4 микро-хука высокого удержания |
| **Smart Segment Trimming** | AI выбирает лучшие сегменты |
| **Auto-BGM & Ducking** | Локальная библиотека BGM с ducking |
| **Auto-Thumbnail** | Извлечение кадров с тёмным оверлеем |
| **Watermark Engine** | Текстовые/графические водяные знаки |
| **Cross-Platform Metadata** | Заголовок/описание/теги для YouTube и TikTok |
| **Auto YouTube Uploader** | Автозагрузка с расписанием |
| **Auto Facebook Reels Uploader** | Загрузка Reels в Facebook Pages |
| **Podcast Split-Screen** | Диаризация + split-screen макет |
| **Podcast Camera Switch** | Автоопределение активного спикера |
| **AI Voice-Over** | Комментарии через Gemini + edge-tts |

> 🎬 **Новое: Story Clip Mode (`--story-mode`)**  
> 👉 **[Документация Story Clip](docs/STORY_CLIP.md)**

## 📋 Требования

- Python 3.10+
- FFmpeg установлен и доступен в PATH
- CUDA GPU рекомендуется (есть CPU fallback)
- Google Gemini API Key

## 🚀 Установка

```bash
git clone https://github.com/ayoubzulfiqar/clipit.git
cd clipit
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.sample .env
# Добавьте GOOGLE_API_KEY в .env
```

## 🎬 Использование

```bash
python main.py --url "https://youtube.com/watch?v=..." --clips 5 --ratio 9:16
python main.py --url "url1" "url2" "url3" --clips 3
python main.py --story-mode --story-recipe story_recipe.json --sources-json sources.json
```

## 📄 Лицензия

Проект лицензирован под GNU AGPLv3 License — см. файл [LICENSE](LICENSE).

Copyright (c) 2026 Ayoub Zulfiqar