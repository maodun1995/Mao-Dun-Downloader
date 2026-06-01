from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os
import re

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)


def clean_filename(name):

    name = re.sub(
        r'[\U00010000-\U0010ffff]',
        '',
        name
    )

    name = re.sub(
        r'[\\/*?:"<>|]',
        '',
        name
    )

    return name.strip()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/fetch', methods=['POST'])
def fetch():

    data = request.get_json()

    url = data['url']

    ydl_opts = {
        'quiet': True,
        'skip_download': True
    }

    try:

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(
                url,
                download=False
            )

        return jsonify({

            'success': True,
            'title': info.get('title'),
            'thumbnail': info.get('thumbnail'),
            'duration': info.get('duration'),
            'url': url

        })

    except Exception as e:

        return jsonify({

            'success': False,
            'error': str(e)

        })


@app.route('/download', methods=['POST'])
def download():

    data = request.get_json()

    url = data['url']
    quality = data.get('quality', 'best')

    if quality == "1080":

        fmt = (
            "bestvideo[height<=1080]"
            "+bestaudio/"
            "best[height<=1080]"
        )

    elif quality == "720":

        fmt = (
            "bestvideo[height<=720]"
            "+bestaudio/"
            "best[height<=720]"
        )

    elif quality == "480":

        fmt = (
            "bestvideo[height<=480]"
            "+bestaudio/"
            "best[height<=480]"
        )

    elif quality == "360":

        fmt = (
            "bestvideo[height<=360]"
            "+bestaudio/"
            "best[height<=360]"
        )

    else:

        fmt = "best"

    ydl_opts = {

        'format': fmt,

        'outtmpl':
            'downloads/%(title).80s.%(ext)s',

        'merge_output_format': 'mp4',

        'windowsfilenames': True,

        'noplaylist': True

    }

    try:

        with yt_dlp.YoutubeDL(
            ydl_opts
        ) as ydl:

            info = ydl.extract_info(
                url,
                download=True
            )

            filename = (
                ydl.prepare_filename(
                    info
                )
            )

            if not os.path.exists(
                filename
            ):

                base = os.path.splitext(
                    filename
                )[0]

                for ext in [
                    'mp4',
                    'mkv',
                    'webm'
                ]:

                    test_file = (
                        f"{base}.{ext}"
                    )

                    if os.path.exists(
                        test_file
                    ):

                        filename = (
                            test_file
                        )

                        break

        return send_file(
            filename,
            as_attachment=True
        )

    except Exception as e:

        return jsonify({

            'success': False,
            'error': str(e)

        })


@app.route('/download_mp3', methods=['POST'])
def download_mp3():

    data = request.get_json()
    url = data['url']
    quality = data.get('mp3_quality', '192')

    ydl_opts = {
        'format': 'bestaudio/best',

        # ✅ use stable filename (IMPORTANT)
        'outtmpl': 'downloads/audio-%(id)s.%(ext)s',

        'windowsfilenames': True,
        'noplaylist': True,

        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': quality
        }]
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(url, download=True)

            file_id = info.get("id")

            filename = f"downloads/audio-{file_id}.mp3"

        return send_file(
            filename,
            as_attachment=True,
            download_name="audio.mp3"
        )

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        })

    ydl_opts = {

        'format':
            'bestaudio/best',

        'outtmpl':
            'downloads/%(title).80s.%(ext)s',

        'windowsfilenames':
            True,

        'postprocessors': [{

            'key':
                'FFmpegExtractAudio',

            'preferredcodec':
                'mp3',

            'preferredquality':
                quality

        }],

        'noplaylist':
            True

    }

    try:

        with yt_dlp.YoutubeDL(
            ydl_opts
        ) as ydl:

            info = ydl.extract_info(
                url,
                download=True
            )

            title = clean_filename(
                info.get('title')
            )

            filename = (
                f"downloads/{title}.mp3"
            )

        return send_file(

            filename,

            as_attachment=True,

            download_name=
                f"{title}.mp3"

        )

    except Exception as e:

        return jsonify({

            'success': False,
            'error': str(e)

        })


if __name__ == '__main__':

    app.run(host="0.0.0.0", port=5000, debug=True)