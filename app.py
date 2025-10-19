import streamlit as st
import json
import os
import re
from datetime import datetime
from typing import List, Dict
from utils import simpan_ke_file
from proyek import tambah_proyek_form, edit_proyek_form
from fitur import ambil_data_mal, refresh_data, edit_sinopsis
from fitur1 import sidebar_kiri, tampilkan_menu_khusus
from penggarap_resmi import tampilkan_penggarap_resmi_page

st.set_page_config(page_title="Anime Indonesia", layout="wide")

DATA_FILE = "anime_db.json"
tahun_sekarang = datetime.now().year
query_params = st.query_params
selected_url = query_params.get("anime", None)
menu = query_params.get("menu", None)

if "anime_list" not in st.session_state:
    st.session_state["anime_list"] = []

if "is_mobile" not in st.session_state:
    st.session_state["is_mobile"] = False

sidebar_kiri()
tampilkan_menu_khusus()

def muat_dari_file(path: str = DATA_FILE) -> List[Dict]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def validasi_url_mal(url: str) -> bool:
    return bool(re.match(r"^https://myanimelist\.net/anime/\d+(/[a-zA-Z0-9_\-]+)?$", url))

def bersihkan_url_mal(url: str) -> str:
    match = re.match(r"(https://myanimelist\.net/anime/\d+(/[a-zA-Z0-9_\-]+)?)", url)
    return match.group(1) if match else url

st.session_state["anime_list"] = muat_dari_file()

judul_filter = ""
genre_filter = "Semua"
format_filter = "Semua"
tahun_filter = "Semua"
musim_filter = "Semua"

# Routing Modular
if menu == "penggarap_resmi":
    tampilkan_penggarap_resmi_page(st.session_state["anime_list"])
    st.markdown("---")

# Halaman Utama
if not selected_url and menu != "penggarap_resmi":
    # Responsive Filter Layout
    if st.session_state.get("is_mobile"):
        # Mobile Layout - Stack filters vertically
        judul_filter = st.text_input("🔍 Cari Judul")
        col1, col2 = st.columns(2)
        with col1:
            genre_filter = st.selectbox("Genre", ["Semua", "Action", "Romance", "Comedy", "Fantasy"])
            tahun_filter = st.selectbox("Tahun", ["Semua"] + [str(t) for t in range(tahun_sekarang, 1899, -1)])
        with col2:
            format_filter = st.selectbox("Format", ["Semua", "TV", "OVA", "ONA", "Spesial", "Movie"])
            musim_filter = st.selectbox("Musim", ["Semua", "Musim Semi", "Musim Panas", "Musim Gugur", "Musim Dingin"])
    else:
        # Desktop Layout - Horizontal filters
        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 2])
        with col1:
            judul_filter = st.text_input("🔍 Cari Judul")
        with col2:
            genre_filter = st.selectbox("Genre", ["Semua", "Action", "Romance", "Comedy", "Fantasy"])
        with col3:
            format_filter = st.selectbox("Format", ["Semua", "TV", "OVA", "ONA", "Spesial", "Movie"])
        with col4:
            tahun_filter = st.selectbox("Tahun", ["Semua"] + [str(t) for t in range(tahun_sekarang, 1899, -1)])
        with col5:
            musim_filter = st.selectbox("Musim", ["Semua", "Musim Semi", "Musim Panas", "Musim Gugur", "Musim Dingin"])

    with st.expander("➕ Tambah Anime Baru"):
        with st.form("form_tambah"):
            url = st.text_input("Masukkan URL MAL")
            simpan = st.form_submit_button("Simpan")
            batal = st.form_submit_button("Batal")

        if simpan:
            url_bersih = bersihkan_url_mal(url)
            if not validasi_url_mal(url_bersih):
                st.error("URL tidak valid.")
            elif any(a.get("mal_url") == url_bersih for a in st.session_state["anime_list"]):
                st.warning("Anime ini sudah ada di database.")
            else:
                data = ambil_data_mal(url_bersih)
                if "error" in data:
                    st.error(f"Gagal scraping: {data['error']}")
                elif not data.get("title"):
                    st.error("Judul gagal diambil.")
                else:
                    st.session_state["anime_list"].append(data)
                    simpan_ke_file(st.session_state["anime_list"])
                    st.success("Anime berhasil ditambahkan.")
                    st.query_params = {}

        if batal:
            st.info("Penambahan dibatalkan.")
    def filter_anime(list_anime: List[Dict]) -> List[Dict]:
        hasil = []
        for a in list_anime:
            if judul_filter and judul_filter.lower() not in a.get("title", "").lower():
                continue
            if genre_filter != "Semua" and genre_filter not in a.get("genres", []):
                continue
            if format_filter != "Semua" and a.get("format", "") != format_filter:
                continue
            if tahun_filter != "Semua" and tahun_filter not in a.get("aired", ""):
                continue
            if musim_filter != "Semua" and musim_filter not in a.get("season", ""):
                continue
            hasil.append(a)
        return hasil

    filtered = filter_anime(st.session_state["anime_list"])
    st.markdown("## Populer di Fall 2025")
    if filtered:
        if st.session_state["is_mobile"]:
            # Layout Mobile - Card Style dengan spacing lebih baik
            for i, anime in enumerate(filtered):
                with st.container():
                    col_cover, col_info = st.columns([1, 2])
                    with col_cover:
                        st.image(anime.get("cover", "https://via.placeholder.com/300x400?text=No+Image"), use_container_width=True)
                    with col_info:
                        st.markdown(f"### {anime.get('title')}")
                        st.caption(f"**{anime.get('format')}** | ⭐ {anime.get('rating')}")
                        if anime.get("genres"):
                            st.caption("🎭 " + ", ".join(anime.get("genres", [])[:3]))
                        
                        col_btn1, col_btn2 = st.columns([3, 1])
                        with col_btn1:
                            if st.button("📖 Lihat Detail", key=f"detail_{i}", use_container_width=True):
                                st.query_params = {"anime": anime.get("mal_url")}
                        with col_btn2:
                            if st.button("🗑️", key=f"hapus_{i}", use_container_width=True):
                                st.session_state["anime_list"].pop(i)
                                simpan_ke_file(st.session_state["anime_list"])
                                st.query_params = {}
                    st.markdown("---")
        else:
            # Layout Desktop - Grid 5 kolom
            cols = st.columns(5)
            for i, anime in enumerate(filtered):
                with cols[i % 5]:
                    st.image(anime.get("cover", "https://via.placeholder.com/300x400?text=No+Image"), use_container_width=True)
                    judul = anime.get("title") or "Judul Tidak Ditemukan"
                    if st.button(judul, key=f"detail_{i}", use_container_width=True):
                        st.query_params = {"anime": anime.get("mal_url")}
                    st.caption(f"{anime.get('format','')} | ⭐ {anime.get('rating','N/A')}")
                    if anime.get("genres"):
                        st.caption(", ".join(anime.get("genres", [])[:3]))
                    if st.button("🗑️", key=f"hapus_{i}", use_container_width=True):
                        st.session_state["anime_list"].pop(i)
                        simpan_ke_file(st.session_state["anime_list"])
                        st.query_params = {}
    else:
        st.info("Belum ada anime yang ditambahkan.")

# Halaman Detail Anime
anime = None
if selected_url:
    anime = next((a for a in st.session_state["anime_list"] if a.get("mal_url") == selected_url), None)

if anime:
    col_judul, col_btn = st.columns([5, 1])
    with col_judul:
        st.markdown(f"## {anime.get('title','Unknown')}")
    with col_btn:
        if st.button("➕ Proyek Baru"):
            st.session_state["tambah_proyek"] = selected_url

    # Responsive layout untuk detail anime
    if st.session_state.get("is_mobile"):
        # Mobile Layout - Stack vertically
        st.image(anime.get("cover", "https://via.placeholder.com/300x400?text=No+Image"), use_container_width=True)
        st.markdown("### 📋 Informasi")
        st.write(f"**Format:** {anime.get('format','')}")
        st.write(f"**Episode:** {anime.get('episodes','?')}")
        st.write(f"**Status:** {anime.get('status','?')}")
        st.write(f"**Tayang:** {anime.get('aired','?')}")
        st.write(f"**Musim:** {anime.get('season','')}")
        st.write(f"**Studio:** {anime.get('studio','?')}")
        st.write(f"**Sumber:** {anime.get('source','?')}")
        st.write(f"**Rating:** {anime.get('rating','')}")
        st.write(f"**Genres:** {', '.join(anime.get('genres',[]))}")
        if anime.get("themes"):
            st.write(f"**Themes:** {', '.join(anime.get('themes',[]))}")
        if anime.get("demographic"):
            st.write(f"**Demographic:** {', '.join(anime.get('demographic',[]))}")
        st.markdown(f"[🔗 Lihat di MAL]({anime.get('mal_url','')})")
        refresh_data(anime, selected_url)
    else:
        # Desktop Layout - Side by side
        cols = st.columns([1, 2])
        with cols[0]:
            st.image(anime.get("cover", "https://via.placeholder.com/300x400?text=No+Image"), width=300)
        with cols[1]:
            st.write(f"**Format:** {anime.get('format','')}")
            st.write(f"**Episode:** {anime.get('episodes','?')}")
            st.write(f"**Status:** {anime.get('status','?')}")
            st.write(f"**Tayang:** {anime.get('aired','?')}")
            st.write(f"**Musim:** {anime.get('season','')}")
            st.write(f"**Studio:** {anime.get('studio','?')}")
            st.write(f"**Sumber:** {anime.get('source','?')}")
            st.write(f"**Rating:** {anime.get('rating','')}")
            st.write(f"**Genres:** {', '.join(anime.get('genres',[]))}")
            if anime.get("themes"):
                st.write(f"**Themes:** {', '.join(anime.get('themes',[]))}")
            if anime.get("demographic"):
                st.write(f"**Demographic:** {', '.join(anime.get('demographic',[]))}")
            st.write(f"[Lihat di MAL]({anime.get('mal_url','')})")
            refresh_data(anime, selected_url)

    st.markdown("### Sinopsis")
    edit_sinopsis(anime, selected_url)

    st.markdown("### Proyek Garapan")
    proyek_list = anime.get("proyek", [])
    if proyek_list:
        if st.session_state.get("is_mobile"):
            # Mobile Layout - Card style untuk proyek
            for idx, p in enumerate(proyek_list):
                with st.container():
                    st.markdown(f"**{p['penggarap']}**")
                    if p.get("catatan"):
                        st.caption(f"📝 {p['catatan']}")
                    
                    col_status, col_format = st.columns([1, 1])
                    with col_status:
                        warna = {
                            "Berjalan": "#4CAF50",
                            "Mangkrak": "#F44336",
                            "Tentatif": "#9E9E9E",
                            "Selesai": "#2196F3"
                        }.get(p["status"], "#CCCCCC")
                        st.markdown(
                            f"<span style='background-color:{warna};color:white;padding:4px 8px;border-radius:4px;font-size:12px;'>{p['status']}</span>",
                            unsafe_allow_html=True
                        )
                    with col_format:
                        st.markdown(
                            f"<a href='{p['link']}' target='_blank' style='background-color:#eee;padding:4px 8px;border-radius:4px;text-decoration:none;color:#333;font-size:12px;'>{p['format']}</a>",
                            unsafe_allow_html=True
                        )
                    
                    col_edit, col_hapus = st.columns([1, 1])
                    with col_edit:
                        if st.button("✏️ Edit", key=f"edit_proyek_{idx}", use_container_width=True):
                            st.session_state["edit_proyek"] = (selected_url, idx)
                    with col_hapus:
                        if st.button("🗑️ Hapus", key=f"hapus_proyek_{idx}", use_container_width=True):
                            anime["proyek"].pop(idx)
                            simpan_ke_file(st.session_state["anime_list"])
                            st.success("Proyek dihapus.")
                            st.query_params = {"anime": selected_url}
                    st.markdown("---")
        else:
            # Desktop Layout - Table style
            for idx, p in enumerate(proyek_list):
                col1, col2, col3 = st.columns([5, 3, 2])
                with col1:
                    penggarap_text = f"**{p['penggarap']}**"
                    if p.get("catatan"):
                        penggarap_text += f" &nbsp; <span style='color:#ccc;font-size:0.9em;'>📝 {p['catatan']}</span>"
                    st.markdown(penggarap_text, unsafe_allow_html=True)
                with col2:
                    warna = {
                        "Berjalan": "#4CAF50",
                        "Mangkrak": "#F44336",
                        "Tentatif": "#9E9E9E",
                        "Selesai": "#2196F3"
                    }.get(p["status"], "#CCCCCC")
                    st.markdown(
                        f"<span style='background-color:{warna};color:white;padding:4px 8px;border-radius:4px;'>{p['status']}</span> &nbsp; "
                        f"<a href='{p['link']}' target='_blank' style='background-color:#eee;padding:4px 8px;border-radius:4px;text-decoration:none;'>{p['format']}</a>",
                        unsafe_allow_html=True
                    )
                with col3:
                    col_edit, col_hapus = st.columns([1, 1], gap="small")
                    with col_edit:
                        if st.button("✏️", key=f"edit_proyek_{idx}", use_container_width=True):
                            st.session_state["edit_proyek"] = (selected_url, idx)
                    with col_hapus:
                        if st.button("🗑️", key=f"hapus_proyek_{idx}", use_container_width=True):
                            anime["proyek"].pop(idx)
                            simpan_ke_file(st.session_state["anime_list"])
                            st.success("Proyek dihapus.")
                            st.query_params = {"anime": selected_url}
    else:
        st.info("Belum ada proyek garapan untuk anime ini.")

    if st.session_state.get("tambah_proyek") == selected_url:
        tambah_proyek_form()

    if st.session_state.get("edit_proyek") and st.session_state["edit_proyek"][0] == selected_url:
        edit_proyek_form()
