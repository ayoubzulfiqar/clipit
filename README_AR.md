<br />
<div align="center">
  <a href="https://github.com/ayoubzulfiqar/clipit">
    <img src="assets/images/clipit-logo-8x.png" alt="Logo" width="350">
  </a>

  <h3 align="center">Clipit</h3>

  <p align="center">
    <strong>أداة AI Auto-Clipper & Teaser Generator 궁극적</strong><br>
    مصنع محتوى مفتوح المصدر يحوّل الفيديوهات الطويلة إلى مقاطع قصيرة سينمائية مع خطافات، ترجمات كاريوكي، وصور مصغرة تلقائية.
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
    <a href="https://github.com/ayoubzulfiqar/clipit/issues/new">الإبلاغ عن خطأ</a>
    &middot;
    <a href="https://github.com/ayoubzulfiqar/clipit/issues/new">طلب ميزة</a>
  </p>
</div>

---

🟢 **قيد الصيانة بنشاط**: المساهمات، تقارير الأخطاء، وPRs مرحب بها.

---

## ✨ الميزات

| الميزة | الوصف |
|---|---|
| **AI Transcriber** | تفريغ على مستوى الكلمة باستخدام Faster-Whisper (large-v3) |
| **AI Content Curator** | Gemini يحلل السياق ويختار أكثر اللحظات انتشارًا ويولد البيانات الوصفية |
| **Smart Auto-Framing** | تتبع الوجه عبر MediaPipe مع Smooth Pan وDeadzone |
| **Cinematic Teaser Hook** | خطاف 3 ثوانٍ مع تراكب داكن وانتقال TV Glitch |
| **Karaoke Subtitles** | ترجمات .ASS مميزة كلمة بكلمة |
| **Kinetic Typography** | تأكيد كلمات مدعوم بـ AI مع حركات bounce/stagger |
| **B-Roll Integration** | جلب لقطات stock من Pexels مع crossfade و Ken Burns |
| **Multi-Hook Intro (V2)** | 3-4 خطافات مصغرة عالية الاحتفاظ |
| **Smart Segment Trimming** | AI يختار أفضل المقاطع ويقص الأجزاء المملة |
| **Auto-BGM & Ducking** | مكتبة BGM محلية مع ducking جانبي أو خلفية |
| **Auto-Thumbnail** | استخراج إطارات مع تراكب داكن ونص عنوان كبير |
| **Watermark Engine** | علامات مائية نصية/صورية بموضع قابل للتعديل |
| **Cross-Platform Metadata** | عنوان/وصف/وسوم YouTube + TikTok |
| **Auto YouTube Uploader** | رفع تلقائي مع جدولة وبيانات وصفية كاملة |
| **Auto Facebook Reels Uploader** | رفع Reels إلى صفحات Facebook مع جدولة ذكية |
| **Podcast Split-Screen** | diarization تلقائي مع تخطيط split-screen |
| **Podcast Camera Switch** | كشف المتحدث النشط مع تبديل المشاهد |
| **AI Voice-Over** | تحويل المقاطع إلى videos تعليق باستخدام Gemini + edge-tts |

> 🎬 **جديد: Story Clip Mode (`--story-mode`)**  
> 👉 **[اقرأ توثيق Story Clip](docs/STORY_CLIP.md)**

## 📋 المتطلبات

- Python 3.10+
- FFmpeg مثبت وموجود في PATH
- GPU CUDA موصى به (CPU fallback متاح)
- Google Gemini API Key

## 🚀 التثبيت

```bash
git clone https://github.com/ayoubzulfiqar/clipit.git
cd clipit
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.sample .env
# أضف GOOGLE_API_KEY في .env
```

## 🎬 الاستخدام

```bash
python main.py --url "https://youtube.com/watch?v=..." --clips 5 --ratio 9:16
python main.py --url "url1" "url2" "url3" --clips 3
python main.py --story-mode --story-recipe story_recipe.json --sources-json sources.json
```

## 📄 الترخيص

هذا المشروع مرخص تحت رخصة جنو أفيرو العمومية GNU AGPLv3 — راجع ملف [LICENSE](LICENSE).

Copyright (c) 2026 Ayoub Zulfiqar