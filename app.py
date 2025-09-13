import streamlit as st
import instaloader
import os
import yt_dlp
import requests
from datetime import datetime
import base64
import time
import json

# --- Configurações Gerais ---
FFMPEG_LOCATION = r"C:\Users\Paulo\Desktop\Projetos\Aplicativo para baixar arquivos\ffmpeg\bin" # Use r'' para caminhos no Windows

st.set_page_config(page_title="App do Paulim", layout="centered", page_icon="🎵")

@st.cache_data
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file, config):
    bin_str = get_base64_of_bin_file(png_file)

    # Define a cor de destaque com base na configuração do tema
    accent_color = "rgba(20, 80, 180, 0.8)" # Azul Padrão
    button_accent_color = "rgba(30, 144, 255, 0.7)"
    button_hover_color = "rgba(30, 144, 255, 0.9)" # Azul Hover
    if config.get("tema") == "Vermelho":
        accent_color = "rgba(139, 0, 0, 0.8)" # Vermelho Escuro
        button_accent_color = "rgba(220, 20, 60, 0.7)" # Vermelho Carmesim
        button_hover_color = "rgba(220, 20, 60, 0.9)" # Vermelho Carmesim Hover

    page_bg_img = f'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron&display=swap');
    .stApp {{
        background-image: url("data:image/jpeg;base64,{bin_str}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        font-family: 'Orbitron', sans-serif; /* Aplica a fonte estilo calculadora */
    }}
    /* Regra geral para deixar todo o texto preto */
    body, .st-emotion-cache-16idsys p, .st-emotion-cache-16txtl3, .st-emotion-cache-1y4p8pa, .st-emotion-cache-10trblm, .st-emotion-cache-q8sbsg p, .st-emotion-cache-1kyxreq, .st-emotion-cache-aabcns p, .st-emotion-cache-ocqkz7, .st-emotion-cache-1xarl3l, .st-emotion-cache-1xarl3l p {{
        color: black !important;
    }}
    .css-18e3th9 {{ background-color: {accent_color}; }} /* Sidebar */
    .stButton>button {{ background-color: #1E90FF; color: white; }} /* Botões: Azul (DodgerBlue) */
    .stTextInput>div>div>input {{ background-color: rgba(240, 248, 255, 0.9); }} /* Inputs: Azul bem claro (AliceBlue) */
    /* Estilo para os botões do menu lateral (cards) */
    .st-emotion-cache-1zhiv0l {{
        background-color: {button_accent_color}; /* Fundo do botão (cor de destaque) */
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 10px;
        margin-bottom: 5px;
        transition: background-color 0.3s ease, transform 0.2s ease;
    }}
    .st-emotion-cache-1zhiv0l:hover {{
        background-color: {button_hover_color}; /* Mais opaco no hover */
        transform: scale(1.02);
    }}

    /* --- Media Query para Dispositivos Móveis --- */
    @media (max-width: 768px) {{
        /* Reduz o tamanho dos títulos para caberem melhor na tela */
        h1 {{
            font-size: 28px !important;
        }}
        h2 {{
            font-size: 24px !important;
        }}
        h3 {{
            font-size: 20px !important;
        }}
        /* Garante que as imagens nos resultados de busca não ultrapassem a largura da coluna */
        .st-emotion-cache-1v0mbdj img {{
             max-width: 100%;
        }}
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

# --- Funções de Configuração ---
CONFIG_FILE = "config.json"

def load_config():
    """Carrega as configurações do usuário do arquivo JSON."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    # Retorna um dicionário de configurações padrão se o arquivo não existir
    return {
        "tema": "Padrão",
        "volume": 70,
        "layout": "Moderno",
        "browser_cookies": "Nenhum"
    }

def save_config(config):
    """Salva as configurações do usuário no arquivo JSON."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

# Carrega a configuração no início da execução e armazena no estado da sessão
if 'config' not in st.session_state:
    st.session_state.config = load_config()

# --- Definição das Páginas ---
PAGES = {
    "Baixar Vídeos": "📥",
    "Baixar Filmes": "🎬",
    "Baixar músicas": "🎵",
    "Fila de Downloads": "⏳",
    "Filmes Baixados": "🎞️",
    "Minhas músicas & Playlists": "🎶",
    "Histórico de downloads": "📜",
    "Configurações": "⚙️"
}

# --- Lógica da Página Atual ---
if 'pagina_atual' not in st.session_state:
    st.session_state.pagina_atual = "Baixar Vídeos" # Página padrão

# Sidebar para navegação
st.sidebar.title("App do Paulim")
for page_name, icon in PAGES.items():
    if st.sidebar.button(f"{icon} {page_name}", use_container_width=True):
        st.session_state.pagina_atual = page_name
        st.rerun() # Garante que a página mude imediatamente

pagina = st.session_state.pagina_atual

# Define o papel de parede com base na página selecionada
if pagina == "Baixar Filmes" and os.path.exists("ww.jpg"):
    set_background("ww.jpg", st.session_state.config)
elif pagina == "Baixar músicas" and os.path.exists("ww.jpg"):
    set_background("ww.jpg", st.session_state.config)
elif pagina == "Fila de Downloads" and os.path.exists("ww.jpg"):
    set_background("ww.jpg", st.session_state.config)
elif os.path.exists("wallpaper1.jpg"):  # Papel de parede padrão para as outras páginas
    set_background("wallpaper1.jpg", st.session_state.config)


# Função para salvar histórico
if 'download_queue' not in st.session_state:
    st.session_state.download_queue = []
if 'is_queue_running' not in st.session_state:
    st.session_state.is_queue_running = False
if 'current_download_title' not in st.session_state:
    st.session_state.current_download_title = None

def salvar_historico(tipo, url, arquivo):
    with open("historico.txt", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} | {tipo} | {url} | {arquivo}\n")

def gerenciador_de_download(ydl_opts, url_ou_lista_urls, tipo, download_dir, display_mode='full'):
    """
    Gerencia o processo de download com yt-dlp.
    display_mode: 'full' para barra de progresso e botões, 'toast' para notificações.
    """
    # Reseta os estados no início de um novo download
    st.session_state.is_paused = False
    st.session_state.cancel_download = False

    progress_placeholder, button_placeholder = None, None
    if display_mode == 'full':
        progress_placeholder = st.empty()
        button_placeholder = st.empty()

        # Colunas para os botões
        col1, col2 = button_placeholder.columns(2)
        pause_label = "Retomar" if st.session_state.is_paused else "Pausar"
        if col1.button(pause_label, key="pause_resume"):
            st.session_state.is_paused = not st.session_state.is_paused
            st.rerun() # Força o rerender para atualizar o label do botão

        if col2.button("Cancelar Download", key="cancel"):
            st.session_state.cancel_download = True
            st.warning("Cancelamento solicitado... aguardando o término do bloco atual.")

    def progress_hook(d):
        if st.session_state.get('cancel_download', False):
            raise yt_dlp.utils.DownloadCancelled()
        while st.session_state.get('is_paused', False):
            time.sleep(1)

        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            if total_bytes:
                percent = d['downloaded_bytes'] / total_bytes
                progress_text = f"Baixando... {int(percent * 100)}%"
                if display_mode == 'full' and progress_placeholder:
                    progress_placeholder.progress(percent, text=progress_text)
                elif display_mode == 'toast':
                    # Atualiza o toast apenas em intervalos para não sobrecarregar
                    if int(percent * 100) % 10 == 0:
                        st.toast(progress_text)

        elif d['status'] == 'finished':
            if ydl_opts.get('postprocessors'):
                if display_mode == 'full' and progress_placeholder:
                    progress_placeholder.progress(1.0, text="Download concluído. Convertendo...")
            else:
                if display_mode == 'full' and progress_placeholder:
                    progress_placeholder.progress(1.0, text="Download concluído!")

    ydl_opts['progress_hooks'] = [progress_hook]

    try:
        os.makedirs(download_dir, exist_ok=True)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url_ou_lista_urls, download=True)
            title = info.get('title') if isinstance(info, dict) else url_ou_lista_urls
            st.success(f"Download concluído com sucesso: {title}")
            salvar_historico(tipo, url_ou_lista_urls, download_dir)
            st.balloons()
    except yt_dlp.utils.DownloadCancelled:
        st.info("Download cancelado pelo usuário.")
    except yt_dlp.utils.DownloadError as e:
        st.error(f"Erro no download: {e}")
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado: {e}")
    finally:
        # Limpa os placeholders e reseta o estado
        st.session_state.current_download_title = None
        st.session_state.cancel_download = False
        st.session_state.is_paused = False
        if display_mode == 'full' and progress_placeholder:
            progress_placeholder.empty()
            button_placeholder.empty()

def pagina_baixar_videos():
    st.title("📥 Baixar Vídeos")

    # Inicializa o estado da seleção se não existir
    if 'video_source' not in st.session_state:
        st.session_state.video_source = "YouTube"

    # Cria os cards em colunas
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("YouTube", use_container_width=True):
            st.session_state.video_source = "YouTube"
    with col2:
        if st.button("Instagram Reels", use_container_width=True):
            st.session_state.video_source = "Instagram Reels"
    with col3:
        if st.button("Twitter", use_container_width=True):
            st.session_state.video_source = "Twitter"

    # Exibe o formulário correspondente à seleção
    if st.session_state.video_source == "YouTube":
        with st.form(key="youtube_form"):
            yt_url = st.text_input("URL do vídeo do Youtube:")
            submitted = st.form_submit_button("Adicionar à Fila")
        if submitted and yt_url:
            job = {
                "url": yt_url, "title": yt_url,
                "ydl_opts": {'outtmpl': 'youtube_baixados/%(title)s.%(ext)s'},
                "tipo": "Youtube", "download_dir": "youtube_baixados"
            }
            st.session_state.download_queue.append(job)
            st.success(f"Vídeo do YouTube adicionado à fila.")
        elif submitted:
            st.warning("Insira a URL do vídeo.")

    elif st.session_state.video_source == "Instagram Reels":
        with st.form(key="instagram_form"):
            reel_url = st.text_input("URL do Reel:")
            submitted = st.form_submit_button("Baixar Reel Agora")
        if submitted and reel_url:
            with st.spinner("Baixando o Reel... Por favor, aguarde."):
                try:
                    if "/reel/" not in reel_url:
                        st.error("Por favor, insira uma URL válida de um Reel do Instagram.")
                        return
                    post_code = reel_url.split("/reel/")[1].split("/")[0]
                    download_dir = "reels_baixados"
                    os.makedirs(download_dir, exist_ok=True)
                    L = instaloader.Instaloader()
                    post = instaloader.Post.from_shortcode(L.context, post_code)
                    L.download_post(post, target=download_dir)
                    st.success(f"Reel baixado com sucesso!")
                    salvar_historico("Instagram", reel_url, download_dir)
                    st.balloons()
                except Exception as e:
                    st.error(f"Ocorreu um erro: {e}")
        elif submitted:
            st.warning("Por favor, insira a URL do Reel.")

    elif st.session_state.video_source == "Twitter":
        with st.form(key="twitter_form"):
            tw_url = st.text_input("URL do vídeo do Twitter:")
            submitted = st.form_submit_button("Adicionar à Fila")
        if submitted and tw_url:
            job = {
                "url": tw_url, "title": tw_url,
                "ydl_opts": {'outtmpl': 'twitter_baixados/%(title)s.%(ext)s'},
                "tipo": "Twitter", "download_dir": "twitter_baixados"
            }
            st.session_state.download_queue.append(job)
            st.success(f"Vídeo do Twitter adicionado à fila.")
        elif submitted:
            st.warning("Insira a URL do vídeo do Twitter.")

def adicionar_filme_a_fila(video_url, video_title):
    """Adiciona um filme à fila de downloads."""
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': 'filmes_baixados/%(title)s.%(ext)s',
        'ffmpeg_location': FFMPEG_LOCATION,
    }
    job = {"url": video_url, "title": video_title, "ydl_opts": ydl_opts, "tipo": "Filme", "download_dir": "filmes_baixados"}
    st.session_state.download_queue.append(job)
    st.success(f"Adicionado à fila: {video_title}")

def pagina_filmes():
    st.title("🎬 Baixar Filmes")
    with st.form(key="film_search_form"):
        search_query = st.text_input("Pesquisar filme:", placeholder="Ex: O Senhor dos Anéis")
        submitted = st.form_submit_button("Pesquisar Filme")

    if submitted:
        if search_query:
            # Adiciona "filme" à consulta para refinar a busca
            full_search_query = f"{search_query} filme"
            with st.spinner(f"Pesquisando por '{full_search_query}'..."):
                try:
                    # Limita a busca aos 5 primeiros resultados com 'ytsearch5:'
                    ydl_opts = {'quiet': True, 'default_search': 'ytsearch5', 'extract_flat': 'in_playlist'}

                    # Usa cookies do navegador se configurado, para evitar erros de autenticação do YouTube
                    browser = st.session_state.config.get("browser_cookies", "Nenhum")
                    if browser != "Nenhum":
                        ydl_opts['cookiesfrombrowser'] = (browser.lower(),)

                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        results = ydl.extract_info(full_search_query, download=False)
                        st.session_state.search_results = results.get('entries', [])
                        if not st.session_state.search_results:
                            st.warning("Nenhum resultado encontrado.")
                except Exception as e:
                    st.error(f"Erro na pesquisa: {e}")
                    st.session_state.search_results = []
        else:
            st.warning("Por favor, digite algo para pesquisar.")

    if 'search_results' in st.session_state and st.session_state.search_results:
        st.markdown("---")
        st.subheader("Resultados da Pesquisa")
        for i, entry in enumerate(st.session_state.search_results):
            col1, col2, col3 = st.columns([1, 4, 1])
            with col1:
                thumbnail_url = entry.get('thumbnail')
                if thumbnail_url:
                    st.image(thumbnail_url, width=120)
            with col2:
                st.markdown(f"**{entry.get('title')}**")
                duration = entry.get('duration_string', 'N/A')
                st.caption(f"Duração: {duration}")
            with col3:
                if st.button("Adicionar à Fila", key=f"add_film_{i}"):
                    adicionar_filme_a_fila(entry['webpage_url'], entry.get('title'))
                    
def pagina_fila_de_downloads():
    st.title("⏳ Fila de Downloads")

    # Botão de Exportar Fila
    if st.session_state.download_queue:
        queue_json = json.dumps(st.session_state.download_queue, indent=4)
        st.download_button(
            label="📥 Exportar Fila",
            data=queue_json,
            file_name="fila_downloads.json",
            mime="application/json",
        )
        st.markdown("---")

    col1, col2, col3 = st.columns(3)
    if col1.button("▶️ Iniciar Fila", disabled=st.session_state.is_queue_running):
        st.session_state.is_queue_running = True
        st.rerun()

    if col2.button("⏹️ Parar Fila", disabled=not st.session_state.is_queue_running):
        st.session_state.is_queue_running = False
        st.rerun()

    if col3.button("🗑️ Limpar Fila Completa"):
        st.session_state.download_queue = []
        st.session_state.is_queue_running = False
        st.rerun()

    if st.session_state.is_queue_running:
        st.info("A fila está em execução. Novos downloads serão processados em sequência.")
    else:
        st.warning("A fila está parada.")

    # Lógica de processamento da fila
    if st.session_state.is_queue_running and st.session_state.download_queue:
        job = st.session_state.download_queue[0] # Pega o próximo sem remover ainda
        st.session_state.current_download_title = job['title']
        
        st.markdown("---")
        st.subheader(f"Baixando agora: {job['title']}")
        
        # Chama o gerenciador com UI completa
        gerenciador_de_download(job['ydl_opts'], job['url'], job['tipo'], job['download_dir'], display_mode='full')
        
        # Se o download terminou (não foi pausado/cancelado), remove da fila e reroda
        if st.session_state.current_download_title is None:
            st.session_state.download_queue.pop(0)
            st.rerun()

    if st.session_state.download_queue:
        st.markdown("---")
        st.subheader("Próximos na Fila")
        for i, job in enumerate(st.session_state.download_queue):
            c1, c2 = st.columns([4, 1])
            # Pula o primeiro item se um download já estiver em andamento
            if st.session_state.current_download_title and i == 0:
                continue
            c1.write(f"{i + 1}. {job['title']}")
            if c2.button("Remover", key=f"remove_job_{i}"):
                st.session_state.download_queue.pop(i)
                st.rerun()
    elif not st.session_state.current_download_title:
        st.info("A fila de downloads está vazia.")

def adicionar_musica_a_fila(video_url, video_title):
    """Adiciona uma música à fila de downloads para conversão em MP3."""
    ydl_opts = {
        'ffmpeg_location': FFMPEG_LOCATION,
        'format': 'bestaudio/best',
        'outtmpl': 'musicas_baixadas/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    job = {"url": video_url, "title": video_title, "ydl_opts": ydl_opts, "tipo": "Música", "download_dir": "musicas_baixadas"}
    st.session_state.download_queue.append(job)
    st.success(f"Adicionado à fila: {video_title}")

def pagina_musicas():
    st.title("🎵 Baixar músicas")

    with st.expander("Ou baixar por link direto"):
        with st.form(key="music_link_form"):
            music_url = st.text_input("URL da música (Youtube, SoundCloud, etc.):", key="music_url_direct")
            link_submitted = st.form_submit_button("Baixar pelo link direto")
        if link_submitted:
            if music_url:
                try:
                    # Inicia o download direto sem adicionar à fila
                    st.info("Preparando para baixar a música...")
                    download_dir = "musicas_baixadas"
                    ydl_opts = {
                        'ffmpeg_location': FFMPEG_LOCATION,
                        'format': 'bestaudio/best',
                        'outtmpl': f'{download_dir}/%(title)s.%(ext)s',
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }],
                    }
                    # Chama o gerenciador de download diretamente
                    gerenciador_de_download(ydl_opts, music_url, "Música", download_dir, display_mode='full')

                except Exception as e:
                    st.error(f"Não foi possível obter informações do link: {e}")

    with st.form(key="music_search_form"):
        search_query = st.text_input("Pesquisar música:", placeholder="Ex: Queen - Bohemian Rhapsody")
        search_submitted = st.form_submit_button("Pesquisar Música")

    if search_submitted:
        if search_query:
            with st.spinner(f"Pesquisando por '{search_query}'..."):
                try:
                    ydl_opts = {'quiet': True, 'default_search': 'ytsearch5', 'extract_flat': 'in_playlist'}

                    # Usa cookies do navegador se configurado, para evitar erros de autenticação do YouTube
                    browser = st.session_state.config.get("browser_cookies", "Nenhum")
                    if browser != "Nenhum":
                        ydl_opts['cookiesfrombrowser'] = (browser.lower(),)

                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        results = ydl.extract_info(search_query, download=False)
                        st.session_state.music_search_results = results.get('entries', [])
                        if not st.session_state.music_search_results:
                            st.warning("Nenhum resultado encontrado.")
                except Exception as e:
                    st.error(f"Erro na pesquisa: {e}")
                    st.session_state.music_search_results = []
        else:
            st.warning("Por favor, digite algo para pesquisar.")

    if 'music_search_results' in st.session_state and st.session_state.music_search_results:
        st.markdown("---")
        st.subheader("Resultados da Pesquisa")
        for i, entry in enumerate(st.session_state.music_search_results):
            col1, col2, col3 = st.columns([1, 4, 1])
            with col1:
                thumbnail_url = entry.get('thumbnail')
                if thumbnail_url:
                    st.image(thumbnail_url, width=120)
            with col2:
                st.markdown(f"**{entry.get('title')}**")
                duration = entry.get('duration_string', 'N/A')
                st.caption(f"Duração: {duration}")
            with col3:
                if st.button("Adicionar à Fila", key=f"add_music_{i}"):
                    adicionar_musica_a_fila(entry['webpage_url'], entry.get('title'))

def pagina_historico():
    st.title("📜 Histórico de downloads")
    # Botão de Exportar Histórico
    if os.path.exists("historico.txt"):
        with open("historico.txt", "r", encoding="utf-8") as f:
            st.download_button(
                label="📥 Exportar Histórico",
                data=f.read(),
                file_name="historico_exportado.txt",
                mime="text/plain",
            )

    if os.path.exists("historico.txt"):
        with open("historico.txt", "r", encoding="utf-8") as f:
            linhas = f.readlines()
        for linha in linhas[::-1]:
            st.markdown(linha)
        if st.button("Limpar Histórico"):
            open("historico.txt", "w").close()
            st.rerun()
    else:
        st.info("Nenhum download realizado ainda.")

def pagina_playlist():
    st.title("🎶 Minhas músicas & Playlists")
    download_dir = "musicas_baixadas"
    if os.path.exists(download_dir):
        arquivos = sorted([f for f in os.listdir(download_dir) if f.endswith(".mp3")])

        if not arquivos:
            st.info("Nenhuma música baixada ainda.")
            return

        # Botão de Exportar Lista de Músicas
        lista_musicas_str = "\n".join(arquivos)
        st.download_button(
            label="📥 Exportar Lista de Músicas",
            data=lista_musicas_str,
            file_name="lista_de_musicas.txt",
            mime="text/plain",
        )
        st.markdown("---")

        playlist = st.multiselect("Selecione músicas para criar uma playlist temporária", arquivos)
        if playlist:
            st.audio([os.path.join(download_dir, m) for m in playlist], format="audio/mp3")
            st.markdown("---")

        for i, musica in enumerate(arquivos):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{musica}**")
            with col2:
                if st.button("Deletar", key=f"delete_music_{i}", type="primary"):
                    try:
                        os.remove(os.path.join(download_dir, musica))
                        st.success(f"Música '{musica}' deletada com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao deletar a música: {e}")
            st.audio(os.path.join(download_dir, musica), format="audio/mp3")
            st.markdown("---")
    else:
        st.info("Nenhuma música baixada.")

def pagina_configuracoes():
    st.title("⚙️ Configurações")

    # Carrega as configurações atuais para os widgets
    current_config = st.session_state.config

    st.subheader("Aparência")
    tema = st.selectbox("Tema do app", ["Padrão", "Vermelho"], index=["Padrão", "Vermelho"].index(current_config.get("tema", "Padrão")))
    layout = st.selectbox("Layout", ["Moderno", "Compacto", "Clássico"], index=["Moderno", "Compacto", "Clássico"].index(current_config.get("layout", "Moderno")))

    st.subheader("Player")
    volume = st.slider("Volume padrão do player", 0, 100, current_config.get("volume", 70))
    st.caption("Nota: O controle de volume ainda não é suportado pelos players padrão do Streamlit.")

    st.subheader("Downloads e Pesquisa")
    browser_cookies = st.selectbox(
        "Usar cookies do navegador para pesquisa (resolve erros 'Sign in to confirm you’re not a bot')",
        ["Nenhum", "Chrome", "Firefox", "Edge", "Brave", "Vivaldi", "Opera"],
        index=["Nenhum", "Chrome", "Firefox", "Edge", "Brave", "Vivaldi", "Opera"].index(current_config.get("browser_cookies", "Nenhum"))
    )
    st.info("Para que isso funcione, você precisa estar logado na sua conta do YouTube no navegador escolhido.")

    st.markdown("---")
    # Botão para exportar as configurações atuais
    config_json = json.dumps(st.session_state.config, indent=4)
    st.download_button(
        label="📥 Exportar Configurações",
        data=config_json,
        file_name="config_exportada.json",
        mime="application/json",
    )

    if st.button("Salvar Preferências"):
        # Cria um novo dicionário de configuração com os valores dos widgets
        new_config = {
            "tema": tema,
            "layout": layout,
            "volume": volume,
            "browser_cookies": browser_cookies
        }
        save_config(new_config) # Salva no arquivo config.json
        st.session_state.config = new_config # Atualiza o estado da sessão
        st.success("Preferências salvas com sucesso! As mudanças de tema serão aplicadas ao recarregar a página.")
        st.balloons()

def pagina_filmes_baixados():
    st.title("🎬 Filmes Baixados")
    download_dir = "filmes_baixados"
    if os.path.exists(download_dir):
        # Filtra por extensões de vídeo comuns
        video_extensions = ['.mp4', '.mkv', '.webm', '.flv', '.avi']
        arquivos = [f for f in os.listdir(download_dir) if os.path.splitext(f)[1].lower() in video_extensions]

        if not arquivos:
            st.info("Nenhum filme baixado ainda.")
            return

        # Botão de Exportar Lista de Filmes
        lista_filmes_str = "\n".join(arquivos)
        st.download_button(
            label="📥 Exportar Lista de Filmes",
            data=lista_filmes_str,
            file_name="lista_de_filmes.txt",
            mime="text/plain",
        )
        st.markdown("---")


        for i, filme in enumerate(sorted(arquivos)):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{filme}**")
            with col2:
                if st.button("Deletar", key=f"delete_movie_{i}", type="primary"):
                    try:
                        filepath = os.path.join(download_dir, filme)
                        os.remove(filepath)
                        st.success(f"Filme '{filme}' deletado com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao deletar o filme: {e}")

            st.video(os.path.join(download_dir, filme))
            st.markdown("---")
    else:
        st.info("Nenhum filme baixado ainda.")

# --- Roteamento das Páginas ---
if pagina == "Baixar Vídeos":
    pagina_baixar_videos()
elif pagina == "Baixar Filmes":
    pagina_filmes()
elif pagina == "Fila de Downloads":
    pagina_fila_de_downloads()
elif pagina == "Baixar músicas":
    pagina_musicas()
elif pagina == "Histórico de downloads":
    pagina_historico()
elif pagina == "Filmes Baixados":
    pagina_filmes_baixados()
elif pagina == "Minhas músicas & Playlists":
    pagina_playlist()
elif pagina == "Configurações":
    pagina_configuracoes()

# --- Lógica de Processamento da Fila em "Segundo Plano" ---
# Se a fila estiver rodando e o usuário não estiver na página da fila
if st.session_state.is_queue_running and st.session_state.download_queue and pagina != "Fila de Downloads":
    job = st.session_state.download_queue[0]
    st.session_state.current_download_title = job['title']
    st.toast(f"Iniciando download: {job['title']}")
    gerenciador_de_download(job['ydl_opts'], job['url'], job['tipo'], job['download_dir'], display_mode='toast')
    if st.session_state.current_download_title is None: # Se o download terminou
        st.session_state.download_queue.pop(0)
