from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os
import re

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


def clean_filename(name):
    name = re.sub(r'[\U00010000-\U0010ffff]', '', name)
    name = re.sub(r'[\\/*?:"<>|]', '', name)
    return name.strip()


# ================= HOME =================
@app.route('/')
def home():
    return render_template('index.html')


# ================= FETCH INFO =================
@app.route('/fetch', methods=['POST'])
def fetch():
    data = request.get_json()
    url = data['url']

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'noplaylist': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0'
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        return jsonify({
            'success': True,
            'title': info.get('title'),
            'thumbnail': info.get('thumbnail'),
            'duration': info.get('duration')
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ================= VIDEO DOWNLOAD =================
@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data['url']
    quality = data.get('quality', 'best')

    fmt = {
        "1080": "bestvideo[height<=1080]+bestaudio/best",
        "720": "bestvideo[height<=720]+bestaudio/best",
        "480": "bestvideo[height<=480]+bestaudio/best",
        "360": "bestvideo[height<=360]+bestaudio/best",
    }.get(quality, "best")

    ydl_opts = {
        'format': fmt,
        'outtmpl': 'downloads/%(title).80s.%(ext)s',
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'http_headers': {'User-Agent': 'Mozilla/5.0'},
        'retries': 3,
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

            if not os.path.exists(filename):
                base = os.path.splitext(filename)[0]
                for ext in ['mp4', 'mkv', 'webm']:
                    if os.path.exists(f"{base}.{ext}"):
                        filename = f"{base}.{ext}"
                        break

        return send_file(filename, as_attachment=True)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ================= MP3 DOWNLOAD =================
@app.route('/download_mp3', methods=['POST'])
def download_mp3():
    data = request.get_json()
    url = data['url']
    quality = data.get('mp3_quality', '192')

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/audio-%(id)s.%(ext)s',
        'noplaylist': True,
        'http_headers': {'User-Agent': 'Mozilla/5.0'},
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': quality
        }],
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_id = info.get("id")
            filename = f"downloads/audio-{file_id}.mp3"

        return send_file(filename, as_attachment=True, download_name="audio.mp3")

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ================= RUN =================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
