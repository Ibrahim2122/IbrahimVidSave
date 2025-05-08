# 📥 IbrahimVidSave - Telegram Video Downloader Bot

Welcome to **IbrahimVidSave**, a simple yet powerful **Telegram bot** that lets users download videos from **TikTok**, **Instagram**, and **YouTube Shorts** – with full support for both **English 🇬🇧** and **Arabic 🇸🇦**!

Built as a personal learning project to explore Telegram Bot APIs, Python async programming, social media downloading, and real-world debugging.

---

## 🚀 Features

- Download videos from TikTok, Instagram, and YouTube Shorts
- Choose download quality:
  - HD 🎥
  - SD 📼
  - Audio Only 🎵
- Multilingual:
  - English 🇬🇧
  - Arabic 🇸🇦
- Friendly UI with inline buttons and reply menus
- Secure file size checking (max 50MB for Telegram sending)
- Automatic re-encoding for safe video formats
- Auto-delete downloaded files after sending

---

## 📸 How it Works

1. User sends `/start`
2. Bot asks to choose language
3. Bot greets the user based on language
4. User clicks "Download Video 🎥"
5. Bot asks for video link
6. User sends link
7. Bot asks for quality (HD / SD / Audio)
8. Bot downloads, re-encodes safely, checks file size
9. Bot sends the file
10. Bot deletes the local copy to stay clean

---

## 🛠 Installation & Setup

1. Clone the repository

   ```bash
   git clone https://github.com/yourusername/IbrahimVidSave.git
   cd IbrahimVidSave
   ```

2. Create virtual environment

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory:

   ```env
   BOT_TOKEN=your-telegram-bot-token-here
   ```

5. Run the bot

   ```bash
   python bot.py
   ```

✅ Bot will start polling and you can interact with it directly.

---

## 📦 Project Structure

| File/Folder  | Purpose                                 |
| :----------- | :-------------------------------------- |
| `bot.py`     | Main bot logic and handlers             |
| `texts.py`   | Multilingual message management         |
| `downloads/` | Temporary storage for downloaded videos |
| `.env`       | Environment variables (hidden secrets)  |

---

## ⚙️ Tech Stack

- Python 3.13
- python-telegram-bot
- yt-dlp
- ffmpeg
- python-dotenv

---

## 🧠 Key Challenges and How I Solved Them

| Challenge                                  | Solution                                               |
| :----------------------------------------- | :----------------------------------------------------- |
| Videos frozen after download               | Forced safe re-encoding using ffmpeg (H.264 + AAC)     |
| Telegram bot freezing after quality choice | Properly handled callback_query vs message types       |
| Secure token management                    | Used `.env` and `python-dotenv`                        |
| File too large to send                     | Checked file size before sending                       |
| Friendly multilingual UX                   | Centralized text in `texts.py` and adapted dynamically |

---

## 📚 What I Learned

- Using yt-dlp and ffmpeg programmatically
- Managing Telegram Bot conversations with multiple states
- Debugging real async bot behavior
- Structuring scalable multilingual bots
- Properly handling API secrets and bot security
- UX design for bots (Menus, cancel options, easy navigation)

---

## 🧹 Credits

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) – The amazing video downloader engine
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) – Best library for building Telegram bots

---

## 📝 License

This project is for educational purposes.  
Feel free to fork, learn, and improve on it!

---

# 👨‍💻 Built with passion by Ibrahim 🚀
