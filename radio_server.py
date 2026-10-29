from flask import Flask, redirect, request, jsonify, Response
import yt_dlp
import requests
app = Flask(__name__)
current_song = {
    "title": "Nenhuma musica - Use /set?url=NOME",
    "youtube_url": "",
    "audio_url": "",
}
def get_audio_url(query):
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'http_headers': {'User-Agent': 'Mozilla/5.0'},
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            if not info:
                return None, None
            if 'entries' in info:
                info = info['entries'][0]
            audio_url = info.get('url')
            title = info.get('title', 'Musica')
            if not audio_url and 'formats' in info:
                for f in info['formats']:
                    if f.get('acodec') != 'none' and f.get('url'):
                        audio_url = f['url']
            return audio_url, title
    except Exception as e:
        print(f"ERRO YT: {e}")
        return None, str(e)
@app.route('/')
def index():
    host = request.host_url
    return f"<h1>VusicTrap FREE - {current_song['title']}</h1><p>Radio: {host}radio</p>"
@app.route('/radio')
def radio():
    if not current_song['audio_url']:
        return "Nenhuma musica ainda. Use /set?url=LINK", 200
    return redirect(current_song['audio_url'])
@app.route('/set')
def set_song():
    try:
        query = request.args.get('url', '')
        if not query:
            return jsonify({"error": "Falta ?url="}), 400
        if "youtube.com" in query or "youtu.be" in query:
            if not query.startswith("http"):
                query = "https://" + query
        print(f"SET: {query}")
        audio_url, title = get_audio_url(query)
        if not audio_url:
            return jsonify({"error": f"Nao encontrei audio para: {query}", "detalhe": str(title)}), 404
        current_song['audio_url'] = audio_url
        current_song['title'] = title if isinstance(title, str) else query
        return jsonify({"status": "ok", "now_playing": current_song['title'], "radio": request.host_url + "radio"})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
@app.route('/status')
def status():
    return jsonify(current_song)
if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
