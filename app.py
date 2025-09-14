import streamlit as st
import os
import requests
from datetime import datetime
import base64
import json
import time # Mantido caso alguma função futura precise dele

# --- Configurações Gerais ---

# Diretórios de download (apenas para fins de organização de código, não salvam permanentemente na nuvem)
DOWNLOAD_DIRS = {
    "Youtube": "youtube_baixados",
    "Instagram": "reels_baixados",
    "Twitter": "twitter_baixados",
    "Filme": "filmes_baixados",
    "Música": "musicas_baixadas"
}

st.set_page_config(page_title="App do Paulim", layout="centered", page_icon="🎵")

@st.cache_data
def get_base64_of_bin_file(bin_file):
    """Converte um arquivo de imagem em base64 para ser usado como fundo."""
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        st.warning(f"Arquivo de imagem não encontrado: {bin_file}")
        return None

def set_background(png_file, config):
    """Define o papel de parede do aplicativo com base no arquivo de imagem e tema."""
    bin_str = get_base64_of_bin_file(png_file)
    if not bin_str:
        return # Não faz nada se o arquivo de imagem não foi encontrado

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
        h1 {{ font-size: 28px !important; }}
        h2 {{ font-size: 24px !important; }}
        h3 {{ font-size: 20px !important; }}
        .st-emotion-cache-1v0mbdj img {{ max-width: 100%; }}
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

# --- Funções de Configuração ---
CONFIG_FILE = "config.json"

def load_config():
    """Carrega as configurações do usuário do arquivo JSON."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            st.warning("Arquivo de configuração corrompido. Usando configurações padrão.")
            return { "tema": "Padrão", "volume": 70, "layout": "Moderno", "browser_cookies": "Nenhum" }
    return {
        "tema": "Padrão",
        "volume": 70,
        "layout": "Moderno",
        "browser_cookies": "Nenhum"
    }

def save_config(config):
    """Salva as configurações do usuário no arquivo JSON."""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
    except IOError as e:
        st.error(f"Erro ao salvar configurações: {e}")

# Carrega a configuração no início da execução e armazena no estado da sessão
if 'config' not in st.session_state:
    st.session_state.config = load_config()

# --- Função para criar diretórios (apenas organizacionais) ---
def criar_diretorios():
    """Cria os diretórios de download se não existirem."""
    for diretorio in DOWNLOAD_DIRS.values():
        try:
            os.makedirs(diretorio, exist_ok=True)
        except OSError as e:
            st.error(f"Erro ao criar diretório {diretorio}: {e}")

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

# Cria os diretórios na inicialização
criar_diretorios()

# --- Lógica de Estado da Sessão ---
if 'pagina_atual' not in st.session_state:
    st.session_state.pagina_atual = "Baixar Vídeos" # Página padrão
if 'download_queue' not in st.session_state:
    st.session_state.download_queue = []
if 'is_queue_running' not in st.session_state:
    st.session_state.is_queue_running = False
if 'current_download_title' not in st.session_state:
    st.session_state.current_download_title = None
if 'video_source' not in st.session_state: # Para página Baixar Vídeos
    st.session_state.video_source = "YouTube"
if 'film_search_results' not in st.session_state:
    st.session_state.film_search_results = []
if 'music_search_results' not in st.session_state:
    st.session_state.music_search_results = []
if 'cancel_download' not in st.session_state:
    st.session_state.cancel_download = False
if 'is_paused' not in st.session_state:
    st.session_state.is_paused = False


# --- Sidebar para navegação ---
st.sidebar.title("App do Paulim")
for page_name, icon in PAGES.items():
    # Use a chave única para cada botão para evitar conflitos
    button_key = f"sidebar_button_{page_name.replace(' ', '_')}"
    if st.sidebar.button(f"{icon} {page_name}", key=button_key, use_container_width=True):
        st.session_state.pagina_atual = page_name
        st.rerun() # Garante que a página mude imediatamente

pagina = st.session_state.pagina_atual

# Define o papel de parede com base na página selecionada
wallpaper_file = "wallpaper1.jpg" # Papel de parede padrão
if pagina == "Baixar Filmes" or pagina == "Baixar músicas" or pagina == "Fila de Downloads":
    if os.path.exists("ww.jpg"):
        wallpaper_file = "ww.jpg"

if os.path.exists(wallpaper_file):
    set_background(wallpaper_file, st.session_state.config)
else:
    st.warning("Papel de parede não encontrado. Verifique os arquivos 'ww.jpg' ou 'wallpaper1.jpg'.")


# --- Funções Auxiliares ---

def salvar_historico(tipo, url, download_dir):
    """Salva o registro de um download no arquivo historico.txt."""
    try:
        with open("historico.txt", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {tipo} | {url} | {download_dir}\n")
    except IOError as e:
        st.error(f"Erro ao salvar histórico: {e}")

# --- REMOVIDO: Gerenciador de download e related logic (yt-dlp) ---
# Como yt-dlp e instaloader não funcionam no Streamlit Cloud,
# a lógica de download direto e adição à fila foi removida.
# As páginas que dependiam delas (Baixar Vídeos, Baixar Filmes, Baixar Músicas)
# foram adaptadas para apenas exibir formulários de busca ou links,
# sem a funcionalidade de download ativa.


# --- Páginas do Aplicativo ---

def pagina_baixar_videos():
    st.title("📥 Baixar Vídeos (Pesquisa)")
    st.info("A funcionalidade de download direto não está disponível no Streamlit Cloud. Use para pesquisar.")

    # Cria os cards em colunas
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("YouTube", use_container_width=True, key="btn_yt_search"):
            st.session_state.video_source = "YouTube"
    with col2:
        if st.button("Instagram Reels", use_container_width=True, key="btn_ig_search"):
            st.session_state.video_source = "Instagram Reels"
    with col3:
        if st.button("Twitter", use_container_width=True, key="btn_tw_search"):
            st.session_state.video_source = "Twitter"

    # Exibe o formulário correspondente à seleção
    if st.session_state.video_source == "YouTube":
        with st.form(key="youtube_search_form"):
            yt_url = st.text_input("URL do vídeo do Youtube:")
            submitted = st.form_submit_button("Pesquisar (Informações)")
        if submitted and yt_url:
            st.info(f"Pesquisando informações para a URL: {yt_url}")
            st.warning("A funcionalidade de download direto não está disponível.")
        elif submitted:
            st.warning("Insira a URL do vídeo.")

    elif st.session_state.video_source == "Instagram Reels":
        with st.form(key="instagram_search_form"):
            reel_url = st.text_input("URL do Reel:")
            submitted = st.form_submit_button("Pesquisar (Informações)")
        if submitted and reel_url:
            st.info(f"Pesquisando informações para a URL: {reel_url}")
            st.warning("A funcionalidade de download direto não está disponível.")
        elif submitted:
            st.warning("Por favor, insira a URL do Reel.")

    elif st.session_state.video_source == "Twitter":
        with st.form(key="twitter_search_form"):
            tw_url = st.text_input("URL do vídeo do Twitter:")
            submitted = st.form_submit_button("Pesquisar (Informações)")
        if submitted and tw_url:
            st.info(f"Pesquisando informações para a URL: {tw_url}")
            st.warning("A funcionalidade de download direto não está disponível.")
        elif submitted:
            st.warning("Insira a URL do vídeo do Twitter.")

def pagina_filmes():
    st.title("🎬 Pesquisar Filmes")
    st.info("A funcionalidade de download direto não está disponível no Streamlit Cloud. Use para pesquisar.")
    with st.form(key="film_search_form"):
        search_query = st.text_input("Pesquisar filme:", placeholder="Ex: O Senhor dos Anéis")
        submitted = st.form_submit_button("Pesquisar Filme")

    if submitted:
        if search_query:
            st.info(f"Pesquisando por filmes relacionados a: '{search_query}'")
            st.warning("A funcionalidade de download direto não está disponível.")
        else:
            st.warning("Por favor, digite algo para pesquisar.")

def pagina_musicas():
    st.title("🎵 Baixar músicas (Pesquisa)")
    st.info("A funcionalidade de download direto não está disponível no Streamlit Cloud. Use para pesquisar.")

    with st.expander("Ou pesquise por link direto"):
        with st.form(key="music_link_form"):
            music_url = st.text_input("URL da música (Youtube, SoundCloud, etc.):", key="music_url_direct")
            link_submitted = st.form_submit_button("Buscar Informações do Link")
        if link_submitted:
            if music_url:
                st.info(f"Buscando informações para a URL: {music_url}")
                st.warning("A funcionalidade de download direto não está disponível.")
            else:
                st.warning("Por favor, insira a URL da música.")

    with st.form(key="music_search_form"):
        search_query = st.text_input("Pesquisar música:", placeholder="Ex: Queen - Bohemian Rhapsody")
        search_submitted = st.form_submit_button("Pesquisar Música")

    if search_submitted:
        if search_query:
            st.info(f"Pesquisando por músicas relacionadas a: '{search_query}'")
            st.warning("A funcionalidade de download direto não está disponível.")
        else:
            st.warning("Por favor, digite algo para pesquisar.")

def pagina_fila_de_downloads():
    st.title("⏳ Fila de Downloads")
    st.warning("Esta página é apenas informativa. A funcionalidade de download está desativada no Streamlit Cloud.")

    # Botão de Exportar Fila (sem funcionalidade real de download)
    if st.session_state.download_queue:
        queue_json = json.dumps(st.session_state.download_queue, indent=4)
        st.download_button(
            label="📥 Exportar Fila (Simulado)",
            data=queue_json,
            file_name="fila_downloads_simulada.json",
            mime="application/json",
            disabled=True # Desabilitado pois não há downloads reais para exportar
        )
        st.markdown("---")

    col1, col2, col3 = st.columns(3)
    col1.button("▶️ Iniciar Fila", disabled=True) # Desabilitado
    col2.button("⏹️ Parar Fila", disabled=True) # Desabilitado
    col3.button("🗑️ Limpar Fila Completa", disabled=True) # Desabilitado

    st.info("A fila de downloads está vazia ou desativada.")

    if st.session_state.download_queue:
        st.markdown("---")
        st.subheader("Próximos na Fila (Simulado)")
        for i, job in enumerate(st.session_state.download_queue):
            c1, c2 = st.columns([4, 1])
            c1.write(f"{i + 1}. {job['title']} (Tipo: {job['tipo']})")
            c2.button("Remover", key=f"remove_job_{i}", disabled=True) # Desabilitado
    elif not st.session_state.current_download_title:
        st.info("A fila de downloads está vazia.")


def pagina_historico():
    st.title("📜 Histórico de downloads")
    st.info("O histórico de downloads é mantido apenas para referência.")
    # Botão de Exportar Histórico
    if os.path.exists("historico.txt"):
        try:
            with open("historico.txt", "r", encoding="utf-8") as f:
                st.download_button(
                    label="📥 Exportar Histórico",
                    data=f.read(),
                    file_name="historico_exportado.txt",
                    mime="text/plain",
                )
        except IOError as e:
            st.error(f"Erro ao ler o histórico para exportar: {e}")

    if os.path.exists("historico.txt"):
        try:
            with open("historico.txt", "r", encoding="utf-8") as f:
                linhas = f.readlines()
            for linha in reversed(linhas): # Exibe do mais recente para o mais antigo
                st.markdown(linha.strip()) # .strip() remove novas linhas extras
        except IOError as e:
            st.error(f"Erro ao ler o histórico: {e}")
        
        if st.button("Limpar Histórico"):
            try:
                open("historico.txt", "w").close()
                st.success("Histórico limpo com sucesso!")
                st.rerun()
            except IOError as e:
                st.error(f"Erro ao limpar o histórico: {e}")
    else:
        st.info("Nenhum download registrado ainda.")

def pagina_playlist():
    st.title("🎶 Minhas músicas & Playlists")
    st.info("As funcionalidades de áudio e playlist não estão ativas pois os downloads foram removidos.")
    download_dir = DOWNLOAD_DIRS["Música"]
    if os.path.exists(download_dir) and os.listdir(download_dir):
        arquivos = sorted([f for f in os.listdir(download_dir) if f.endswith(".mp3")])

        if not arquivos:
            st.info("Nenhuma música baixada ainda.")
            return

        # Botão de Exportar Lista de Músicas
        lista_musicas_str = "\n".join(arquivos)
        st.download_button(
            label="📥 Exportar Lista de Músicas (Simulado)",
            data=lista_musicas_str,
            file_name="lista_de_musicas_simulada.txt",
            mime="text/plain",
            disabled=True # Desabilitado pois não há downloads reais
        )
        st.markdown("---")

        # A funcionalidade de multiselect e st.audio foi desativada.
        st.info("A reprodução de áudio e criação de playlists não está disponível nesta versão.")

        st.subheader("Músicas Baixadas (Apenas lista)")
        for i, musica in enumerate(arquivos):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{musica}**")
            with col2:
                if st.button("Deletar (Simulado)", key=f"delete_music_{i}", type="primary", disabled=True):
                    st.warning("Funcionalidade de deleção desativada.")
            st.markdown("---")
    else:
        st.info("Nenhuma música baixada.")

def pagina_configuracoes():
    st.title("⚙️ Configurações")

    current_config = st.session_state.config

    st.subheader("Aparência")
    tema = st.selectbox("Tema do app", ["Padrão", "Vermelho"], index=["Padrão", "Vermelho"].index(current_config.get("tema", "Padrão")))
    layout = st.selectbox("Layout", ["Moderno", "Compacto", "Clássico"], index=["Moderno", "Compacto", "Clássico"].index(current_config.get("layout", "Moderno")))

    st.subheader("Player")
    volume = st.slider("Volume padrão do player", 0, 100, current_config.get("volume", 70))
    st.caption("Nota: O controle de volume ainda não é suportado pelos players padrão do Streamlit.")

    st.subheader("Downloads e Pesquisa")
    # Opção de cookies removida, pois não funciona em produção no Streamlit Cloud
    browser_cookies = st.selectbox(
        "Usar cookies do navegador para pesquisa",
        ["Nenhum (Não suportado em nuvem)"],
        index=0,
        disabled=True # Desabilitado
    )

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
        new_config = {
            "tema": tema,
            "layout": layout,
            "volume": volume,
            "browser_cookies": browser_cookies # Mantido, mas desabilitado
        }
        save_config(new_config) # Salva no arquivo config.json
        st.session_state.config = new_config # Atualiza o estado da sessão
        st.success("Preferências salvas com sucesso! Algumas mudanças de tema podem requerer recarregar a página.")
        st.balloons()

def pagina_filmes_baixados():
    st.title("🎬 Filmes Baixados")
    st.info("A funcionalidade de exibição de filmes baixados não está ativa pois os downloads foram removidos.")
    download_dir = DOWNLOAD_DIRS["Filme"]
    
    # Simula a exibição de uma lista, mas sem arquivos reais
    st.info("Nenhum filme baixado nesta versão.")
    
    # Se existisse o diretório e arquivos, o código seria:
    # if os.path.exists(download_dir):
    #     video_extensions = ['.mp4', '.mkv', '.webm', '.flv', '.avi']
    #     arquivos = [f for f in os.listdir(download_dir) if os.path.splitext(f)[1].lower() in video_extensions]
    #
    #     if not arquivos:
    #         st.info("Nenhum filme baixado ainda.")
    #         return
    #
    #     lista_filmes_str = "\n".join(arquivos)
    #     st.download_button(
    #         label="📥 Exportar Lista de Filmes (Simulado)",
    #         data=lista_filmes_str,
    #         file_name="lista_de_filmes_simulada.txt",
    #         mime="text/plain",
    #         disabled=True
    #     )
    #     st.markdown("---")
    #
    #     for i, filme in enumerate(sorted(arquivos)):
    #         col1, col2 = st.columns([4, 1])
    #         with col1:
    #             st.markdown(f"**{filme}**")
    #         with col2:
    #             if st.button("Deletar (Simulado)", key=f"delete_movie_{i}", type="primary", disabled=True):
    #                 st.warning("Funcionalidade de deleção desativada.")
    #         st.video(os.path.join(download_dir, filme)) # Desativado pois o arquivo não existe
    #         st.markdown("---")
    # else:
    #     st.info("Nenhum filme baixado ainda.")


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
# Esta lógica é mantida apenas para demonstrar a estrutura,
# mas não terá funcionalidade real de download no Streamlit Cloud.
if st.session_state.is_queue_running and st.session_state.download_queue and pagina != "Fila de Downloads":
    st.toast("Processamento em segundo plano da fila desativado no Streamlit Cloud.")
    # O código abaixo seria executado se houvesse downloads reais:
    # job = st.session_state.download_queue[0]
    # st.session_state.current_download_title = job['title']
    # st.toast(f"Iniciando download: {job['title']}")
    # Aqui seria chamada uma função que simula o download ou mostra um progresso.
    # Como não há download real, esta parte é apenas um placeholder.
    # Se o download terminasse (simuladamente):
    # st.session_state.download_queue.pop(0)
    # st.rerun()
