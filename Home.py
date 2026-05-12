import streamlit as st
import os
import base64
import math

# ── 1. CONFIGURAÇÃO ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="iG2P - Inteligência em Gestão",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── 2. LOGO ──────────────────────────────────────────────────────────────────
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

LOGO_PATH = "Logos/LOGOTIPO IG2P - OFICIAL - BRANCO.png"
logo_base64 = get_image_base64(LOGO_PATH)

# ── 3. ESTADO ────────────────────────────────────────────────────────────────
if "setor_ativo" not in st.session_state:
    st.session_state["setor_ativo"] = None

setor = st.session_state["setor_ativo"]

# ── 4. GRADE SIMÉTRICA ───────────────────────────────────────────────────────
def calcular_colunas(n: int) -> int:
    if n <= 3:
        return n
    return min(range(3, 8), key=lambda c: (math.ceil(n / c) * c - n, abs(math.ceil(n / c) - 2)))

# ── 5. ÍCONES SVG (4 variantes) ───────────────────────────────────────────────
def svg(paths: str, stroke: str) -> str:
    c = stroke.replace("#", "%23")
    return (
        f"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
        f"viewBox='0 0 24 24' fill='none' stroke='{c}' "
        f"stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'%3E"
        f"{paths}%3C/svg%3E"
    )

P_EDU = (
    "%3Cpolygon points='12 2 2 7 12 12 22 7 12 2'/%3E"
    "%3Cpolyline points='6 9.5 6 16'/%3E"
    "%3Cpath d='M6 16c0 2 2.686 3.5 6 3.5s6-1.5 6-3.5V9.5'/%3E"
    "%3Cline x1='22' y1='7' x2='22' y2='13'/%3E"
)
P_SAU = (
    "%3Crect x='3' y='3' width='18' height='18' rx='3'/%3E"
    "%3Cline x1='12' y1='7' x2='12' y2='17'/%3E"
    "%3Cline x1='7' y1='12' x2='17' y2='12'/%3E"
)

GRAY  = "#94A3B8"
GREEN = "#2ECC71"

EDU_GRAY  = svg(P_EDU, GRAY)
EDU_GREEN = svg(P_EDU, GREEN)
SAU_GRAY  = svg(P_SAU, GRAY)
SAU_GREEN = svg(P_SAU, GREEN)

# Ícone dos municípios depende do setor ativo
MUNI_DEFAULT = SAU_GRAY  if setor == "Saúde" else EDU_GRAY
MUNI_HOVER   = SAU_GREEN if setor == "Saúde" else EDU_GREEN
ACTIVE_JS    = setor or ""

# ── 6. CSS — usa seletores data-attribute definidos pelo JavaScript ────────────
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&display=swap');

  /* ── RESET ── */
  [data-testid="stSidebar"],
  header[data-testid="stHeader"],
  .stDeployButton, footer {{ display: none !important; }}

  .stApp {{ background-color: #0E1117 !important; }}
  .block-container {{
    padding-top: 0 !important; padding-left: 0 !important;
    padding-right: 0 !important; max-width: 100% !important;
  }}

  /* ── LOGO ── */
  .brand-box {{
    position: absolute; top: 22px; left: 24px;
    display: flex; flex-direction: column; align-items: flex-start; z-index: 1000;
  }}
  .brand-box img  {{ width: 155px; height: auto; }}
  .brand-box span {{
    color: #94A3B8; font-family: 'Outfit', sans-serif;
    font-size: 12.5px; margin: -3px 0 0 4px; white-space: nowrap;
  }}

  /* ── LABEL ── */
  .sector-label {{
    text-align: center; color: #94A3B8;
    font-family: 'Outfit', sans-serif; font-size: 11px;
    letter-spacing: 2.6px; text-transform: uppercase; margin: 0 0 18px; opacity: 0.55;
  }}

  /* ══════════════════════════════════════════════════
     SECTOR CARDS  —  todos os estilos via data-type
  ══════════════════════════════════════════════════ */

  /* Base cinza (nunca verde até clicar) */
  button[data-type="sector"] {{
    width: 100% !important; height: 200px !important; padding: 0 !important;
    background: #1E293B !important;
    border: 1.5px solid rgba(148,163,184,0.12) !important;
    border-radius: 20px !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.40) !important;
    display: flex !important; flex-direction: column !important;
    align-items: center !important; justify-content: center !important;
    color: {GRAY} !important;
    font-family: 'Outfit', sans-serif !important; font-size: 15px !important;
    font-weight: 500 !important; letter-spacing: 0.3px !important;
    line-height: 1 !important; cursor: pointer !important;
    transition: border-color .22s ease, background .22s ease,
                box-shadow .22s ease, color .22s ease, transform .18s ease !important;
  }}

  /* Ícone via ::after */
  button[data-type="sector"]::after {{
    content: '' !important; display: block !important;
    order: -1 !important;
    width: 60px !important; height: 60px !important;
    border-radius: 14px !important;
    background-color: rgba(148,163,184,0.08) !important;
    background-size: 54% !important; background-position: center !important;
    background-repeat: no-repeat !important; margin-bottom: 18px !important;
    transition: background-color .22s ease, background-image .22s ease !important;
  }}

  /* Ícone correto por setor */
  button[data-type="sector"][data-sector="edu"]::after {{ background-image: url("{EDU_GRAY}") !important; }}
  button[data-type="sector"][data-sector="sau"]::after {{ background-image: url("{SAU_GRAY}") !important; }}

  /* Hover — esverdeado suave */
  button[data-type="sector"]:hover {{
    border-color: rgba(46,204,113,0.40) !important;
    background: #1A2A20 !important;
    transform: translateY(-3px) !important;
    box-shadow: 0 10px 30px rgba(46,204,113,0.12) !important;
    color: #ffffff !important;
  }}
  button[data-type="sector"][data-sector="edu"]:hover::after {{
    background-image: url("{EDU_GREEN}") !important;
    background-color: rgba(46,204,113,0.10) !important;
  }}
  button[data-type="sector"][data-sector="sau"]:hover::after {{
    background-image: url("{SAU_GREEN}") !important;
    background-color: rgba(46,204,113,0.10) !important;
  }}

  /* Ativo — verde após clique */
  button[data-type="sector"][data-active="true"] {{
    border-color: {GREEN} !important;
    background: #162B1F !important;
    box-shadow: 0 0 0 3px rgba(46,204,113,0.18),
                0 14px 36px rgba(46,204,113,0.16) !important;
    color: #ffffff !important;
  }}
  button[data-type="sector"][data-sector="edu"][data-active="true"]::after {{
    background-image: url("{EDU_GREEN}") !important;
    background-color: rgba(46,204,113,0.12) !important;
  }}
  button[data-type="sector"][data-sector="sau"][data-active="true"]::after {{
    background-image: url("{SAU_GREEN}") !important;
    background-color: rgba(46,204,113,0.12) !important;
  }}

  /* ══════════════════════════════════════════════════
     MUNICIPALITY BUTTONS  —  card com ícone + texto
  ══════════════════════════════════════════════════ */

  /* Base cinza — inicialmente invisível para animação */
  button[data-type="municipality"] {{
    width: 100% !important; height: 110px !important; padding: 0 !important;
    background: #1E293B !important;
    border: 1.5px solid rgba(148,163,184,0.10) !important;
    border-radius: 14px !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.30) !important;
    display: flex !important; flex-direction: column !important;
    align-items: center !important; justify-content: center !important;
    color: {GRAY} !important;
    font-family: 'Outfit', sans-serif !important; font-size: 12px !important;
    font-weight: 400 !important; line-height: 1.3 !important;
    white-space: normal !important; word-break: break-word !important;
    text-align: center !important; cursor: pointer !important;
    /* Posição inicial para animação (JS vai adicionar .muni-visible) */
    opacity: 0 !important;
    transform: translateX(-18px) !important;
    /* opacity e transform animam com o delay do JS;
       hover props animam sem delay (ver JS) */
    transition:
      opacity .32s ease,
      transform .32s ease,
      border-color .18s ease,
      background   .18s ease,
      box-shadow   .18s ease,
      color        .18s ease !important;
  }}

  /* Estado visível (classe adicionada pelo JS) */
  button[data-type="municipality"].muni-visible {{
    opacity: 1 !important;
    transform: translateX(0) !important;
  }}

  /* Ícone */
  button[data-type="municipality"]::after {{
    content: '' !important; display: block !important;
    order: -1 !important;
    width: 34px !important; height: 34px !important;
    border-radius: 9px !important;
    background-color: rgba(148,163,184,0.08) !important;
    background-image: url("{MUNI_DEFAULT}") !important;
    background-size: 58% !important; background-position: center !important;
    background-repeat: no-repeat !important; margin-bottom: 9px !important;
    transition: background-color .18s ease, background-image .18s ease !important;
  }}

  /* Hover */
  button[data-type="municipality"]:hover {{
    background: #1A2A20 !important;
    border-color: rgba(46,204,113,0.50) !important;
    color: #ffffff !important;
    transform: translateY(-3px) !important;
    box-shadow: 0 6px 20px rgba(46,204,113,0.14) !important;
  }}
  button[data-type="municipality"]:hover::after {{
    background-image: url("{MUNI_HOVER}") !important;
    background-color: rgba(46,204,113,0.12) !important;
  }}

  /* ── DIVIDER E HEADER ── */
  .divider {{
    width: 40px; height: 2px;
    background: linear-gradient(90deg, transparent, {GREEN}, transparent);
    margin: 0 auto 22px; border-radius: 2px;
    opacity: 0; animation: fadeIn 0.38s ease 0.04s both;
  }}
  @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}

  .muni-header {{
    opacity: 0; animation: slideHeader 0.38s ease 0.08s both;
    text-align: center; color: {GRAY};
    font-family: 'Outfit', sans-serif; font-size: 13px;
    font-weight: 400; margin: 0;
  }}
  .muni-header strong {{ color: {GREEN}; font-weight: 600; }}
  @keyframes slideHeader {{
    from {{ opacity: 0; transform: translateX(-14px); }}
    to   {{ opacity: 1; transform: translateX(0); }}
  }}

  /* Gap entre colunas */
  div[data-testid='stColumn'] {{
    padding-left: 5px !important; padding-right: 5px !important;
  }}
</style>
""", unsafe_allow_html=True)

# ── 7. JAVASCRIPT ─────────────────────────────────────────────────────────────
# MutationObserver garante que os data-attributes sejam aplicados mesmo depois
# do React do Streamlit re-renderizar o DOM.
st.markdown(f"""
<script>
(function() {{
  const ACTIVE = "{ACTIVE_JS}";   // setor ativo vindo do Python

  function run() {{
    const btns = Array.from(document.querySelectorAll('button[kind="secondary"]'));
    if (!btns.length) return;

    // ── Sector cards (primeiros 2 botões) ──────────────────────────────
    const sectorMap = ['edu', 'sau'];
    const activeMap = ['Educação', 'Saúde'];
    btns.slice(0, 2).forEach((btn, i) => {{
      btn.dataset.type   = 'sector';
      btn.dataset.sector = sectorMap[i];
      btn.dataset.active = (ACTIVE === activeMap[i]) ? 'true' : 'false';
    }});

    // ── Municipality buttons (todos os restantes) ──────────────────────
    btns.slice(2).forEach((btn, i) => {{
      btn.dataset.type = 'municipality';

      if (!btn.classList.contains('muni-tagged')) {{
        btn.classList.add('muni-tagged');

        // Delay escalonado apenas para opacity + transform (primeiras 2 props)
        // Hover props (border-color, background, box-shadow, color) ficam em 0s
        const d = (i * 0.055).toFixed(3);
        btn.style.transitionDelay = `${{d}}s, ${{d}}s, 0s, 0s, 0s, 0s`;

        // Dois requestAnimationFrame garantem que o navegador renderize
        // a posição inicial antes de aplicar a classe visível
        requestAnimationFrame(() => requestAnimationFrame(() => {{
          btn.classList.add('muni-visible');
        }}));
      }}
    }});
  }}

  // Substitui qualquer observer anterior para evitar duplicatas
  if (window._ig2pObs) window._ig2pObs.disconnect();
  window._ig2pObs = new MutationObserver(() => {{
    clearTimeout(window._ig2pDebounce);
    window._ig2pDebounce = setTimeout(run, 40);
  }});
  window._ig2pObs.observe(document.body, {{ childList: true, subtree: true }});

  // Execuções diretas para capturar elementos já presentes
  run();
  [80, 220, 500].forEach(t => setTimeout(run, t));
}})();
</script>
""", unsafe_allow_html=True)

# ── 8. LOGO ──────────────────────────────────────────────────────────────────
if logo_base64:
    st.markdown(f"""
      <div class="brand-box">
        <img src="data:image/png;base64,{logo_base64}">
        <span>Inteligência em Gestão</span>
      </div>""", unsafe_allow_html=True)
else:
    st.markdown("""
      <div class="brand-box">
        <h2 style="color:white;margin:0">iG2P</h2>
        <span>Inteligência em Gestão</span>
      </div>""", unsafe_allow_html=True)

# ── 9. ESPAÇAMENTO + LABEL ────────────────────────────────────────────────────
st.markdown("<div style='height:130px'></div>", unsafe_allow_html=True)
st.markdown('<p class="sector-label">Selecione o Setor</p>', unsafe_allow_html=True)

# ── 10. CARD-BUTTONS DOS SETORES ──────────────────────────────────────────────
_, col_edu, col_gap, col_sau, _ = st.columns([2.2, 1.4, 0.12, 1.4, 2.2])

with col_edu:
    if st.button("Educação", key="btn_educacao", use_container_width=True):
        st.session_state["setor_ativo"] = "Educação"
        st.rerun()

with col_sau:
    if st.button("Saúde", key="btn_saude", use_container_width=True):
        st.session_state["setor_ativo"] = "Saúde"
        st.rerun()

# ── 11. GRADE DE MUNICÍPIOS ───────────────────────────────────────────────────
if setor:
    st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown(
        f'<p class="muni-header">Municípios &nbsp;·&nbsp; <strong>{setor}</strong></p>',
        unsafe_allow_html=True
    )
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    if setor == "Educação":
        nomes = [
            "Alpinópolis", "Cássia", "Capetinga", "Claraval", "Delfinópolis",
            "Ibiraci", "Itaú de Minas", "Pratápolis", "Restinga",
            "São João Batista Do Glória", "São José da Barra",
            "São Roque de Minas", "São Tomás de Aquino", "Itamogi",
        ]
        suffix = "Educação"
    else:
        nomes  = ["Alpinópolis", "Bom Jesus da Penha", "Cássia", "Delfinópolis", "Itaú de Minas"]
        suffix = "Saúde"

    n_cols = calcular_colunas(len(nomes))

    _, col_grid, _ = st.columns([0.05, 0.90, 0.05])
    with col_grid:
        cols = st.columns(n_cols, gap="small")
        for i, nome in enumerate(nomes):
            with cols[i % n_cols]:
                file_name = nome.replace(" ", "_")
                path = f"pages/{file_name}_{suffix}.py"
                if st.button(nome, key=f"muni_{nome}_{i}", use_container_width=True):
                    st.session_state["setor_ativo"] = setor
                    try:
                        st.switch_page(path)
                    except Exception as e:
                        st.error(f"Página não encontrada: {path}")