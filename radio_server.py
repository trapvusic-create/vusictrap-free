from flask import Flask, redirect, request, jsonify, Response
import yt_dlp
import requests
app = Flask(__name__)
current_song = {
    "title": "Nenhuma musica - Use /set?url=NOME",
    "youtube_url": "",
    "audio_url": "",
    "requester": "ztk"
}
def get_audio_url(query):
    try:
        if "youtube.com" in query or "youtu.be" in query:
            youtube_url = query
        else:
            ydl_opts_search = {
                'format': 'bestaudio/best',
                'noplaylist': True,
                'quiet': True,
                'default_search': 'ytsearch1',
                'no_warnings': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts_search) as ydl:
                info = ydl.extract_info(f"ytsearch1:{query}", download=False)
                if not info or 'entries' not in info or not info['entries']:
                    return None, None
                v = info['entries'][0]
                youtube_url = f"https://www.youtube.com/watch?v={v['id']}"
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            if not info:
                return None, None
            audio_url = info.get('url')
            title = info.get('title', 'Musica')
            if not audio_url and 'formats' in info:
                for f in reversed(info['formats']):
                    if f.get('acodec') != 'none' and f.get('url'):
                        audio_url = f['url']
                        break
            return audio_url, title
    except Exception as e:
        print(f"Erro: {e}")
        return None, None
@app.route('/')
def index():
    host = request.host_url
    return f"<h1>VusicTrap FREE - {current_song['title']}</h1><p>Radio: {host}radio</p><p>Trocar: {host}set?url=NOME</p>"
@app.route('/radio')
def radio():
    if not current_song['audio_url']:
        return "Nenhuma musica. Use /set?url=matue", 200
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(current_song['audio_url'], stream=True, headers=headers, timeout=15)
        def generate():
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk
        return Response(generate(), content_type=r.headers.get('Content-Type', 'audio/mp4'))
    except:
        return redirect(current_song['audio_url'])
@app.route('/set')
def set_song():
    try:
        query = request.args.get('url', '')
        if not query:
            return jsonify({"error": "Falta ?url="}), 400
        audio_url, title = get_audio_url(query)
        if not audio_url:
            return jsonify({"error": f"Nao encontrei {query}"}), 404
        current_song['audio_url'] = audio_url
        current_song['title'] = title
        return jsonify({"status": "ok", "now_playing": title, "radio_url": request.host_url + "radio"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/status')
def status():
    return jsonify(current_song)
if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
