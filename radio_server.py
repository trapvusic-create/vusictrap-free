
# VusicTrap FREE - Servidor de Radio Gratis para IMVU
# Substitui o Vusic pago
# Room: 363074242 - Dono: ztk

from flask import Flask, redirect, request, jsonify, Response
import yt_dlp
import requests

app = Flask(__name__)

# Guarda musica atual
current_song = {
    "title": "Nenhuma musica - Use !play no bot",
    "youtube_url": "",
    "audio_url": "",
    "requester": "ztk"
}

ydl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'default_search': 'ytsearch'
}

def get_audio_url(youtube_url_or_search):
    # Se for pesquisa, procura primeiro
    if not youtube_url_or_search.startswith("http"):
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{youtube_url_or_search}", download=False)
            if info and 'entries' in info and info['entries']:
                v = info['entries'][0]
                youtube_url_or_search = f"https://www.youtube.com/watch?v={v['id']}"
                title = v.get('title')
            else:
                return None, None
    else:
        title = youtube_url_or_search

    # Extrai URL direto de audio do YouTube
    ydl_opts_audio = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
        try:
            info = ydl.extract_info(youtube_url_or_search, download=False)
            # Pega melhor URL de audio
            audio_url = info.get('url')
            if not audio_url and 'formats' in info:
                # Pega formato audio
                for f in info['formats']:
                    if f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                        audio_url = f['url']
                        break
                if not audio_url:
                    audio_url = info['formats'][-1]['url']
            
            title = info.get('title', title)
            return audio_url, title
        except Exception as e:
            print(f"Erro: {e}")
            return None, None

@app.route('/')
def index():
    return f"""
    <h1>VusicTrap FREE - TRAPST*R - Room 363074242</h1>
    <p>Dono: ztk</p>
    <p><b>Agora a tocar:</b> {current_song['title']}</p>
    <p>Para usar no IMVU, cola isto no Radio Streaming e clica LOAD:</p>
    <code style="background:#000;color:#0f0;padding:10px;">{request.host_url}radio</code>
    <p>Para trocar musica, usa o bot ou acessa: {request.host_url}set?url=NOME_DA_MUSICA</p>
    <p>Ex: {request.host_url}set?url=matue%20-%20777</p>
    """

@app.route('/radio')
def radio():
    """Este é o link que colas no IMVU - NUNCA da failed to load"""
    if not current_song['audio_url']:
        return "Nenhuma musica definida. Use /set?url=NOME", 200
    
    # Redireciona para o audio direto do YouTube (IMVU aceita)
    # Ou faz proxy do audio
    try:
        # Faz proxy para garantir que IMVU aceita
        r = requests.get(current_song['audio_url'], stream=True, timeout=10)
        return Response(r.iter_content(chunk_size=8192), content_type=r.headers.get('Content-Type', 'audio/mpeg'))
    except:
        # Se proxy falhar, redireciona
        return redirect(current_song['audio_url'])

@app.route('/set')
def set_song():
    """Define nova musica: /set?url=matue ou /set?url=https://youtube.com/..."""
    query = request.args.get('url', '')
    if not query:
        return "Falta ?url=", 400
    
    audio_url, title = get_audio_url(query)
    if not audio_url:
        return f"Nao encontrei: {query}", 404
    
    current_song['audio_url'] = audio_url
    current_song['title'] = title
    current_song['youtube_url'] = query
    current_song['requester'] = request.args.get('by', 'ztk')
    
    return jsonify({"status": "ok", "now_playing": title, "radio_url": request.host_url + "radio"})

@app.route('/status')
def status():
    return jsonify(current_song)

if __name__ == '__main__':
    # Render usa PORT env
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
