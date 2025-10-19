import streamlit as st
import json
from datetime import datetime
import os
from packaging import version

DATA_FILE = "data_penggarap.json"

# Kompatibilitas rerun antar versi Streamlit
if version.parse(st.__version__) >= version.parse("1.30.0"):
    rerun = st.rerun
else:
    from streamlit.runtime.scriptrunner import RerunException
    from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx
    def rerun():
        ctx = get_script_run_ctx()
        raise RerunException(ctx)

def cocok_musim(musim_sekarang, musim_anime):
    musim_map = {
        "dingin": ["winter", "musim dingin"],
        "semi": ["spring", "musim semi"],
        "panas": ["summer", "musim panas"],
        "gugur": ["fall", "autumn", "musim gugur"]
    }
    musim_anime = musim_anime.lower()
    return any(m in musim_anime for m in musim_map.get(musim_sekarang, []))

def ambil_logo_platform(data):
    ikon_map = {
        "youtube": "📺",
        "discord": "💬",
        "twitter": "🐦",
        "instagram": "📸",
        "facebook": "📘",
        "tiktok": "🎵",
        "situs": "🌐"
    }
    hasil = []
    for kunci, ikon in ikon_map.items():
        tautan = data.get(kunci, "").strip()
        if tautan:
            if "redirect?" in tautan and "q=" in tautan:
                try:
                    import urllib.parse
                    tautan = urllib.parse.unquote(tautan.split("q=")[-1])
                except:
                    pass
            hasil.append(f"<a href='{tautan}' target='_blank'>{ikon}</a>")
    return " ".join(hasil) if hasil else "-"

def simpan_penggarap(nama, status, situs, medsos):
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    data[nama] = {
        "status": status,
        "situs": situs,
        **medsos
    }

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def hapus_penggarap(nama):
    if not os.path.exists(DATA_FILE):
        return
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
    if nama in data:
        del data[nama]
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)

def form_penggarap(nama_awal="", data_lama=None, mode="tambah"):
    st.markdown(f"### {'✏️ Edit' if mode == 'edit' else '➕ Tambah'} Penggarap")
    nama = st.text_input("Nama Penggarap", value=nama_awal)
    status = st.selectbox("Status", ["Aktif", "Nonaktif"], index=0 if data_lama and data_lama.get("status") == "Aktif" else 1)
    situs = st.text_input("Situs Web", value=data_lama.get("situs", "") if data_lama else "")
    col1, col2, col3 = st.columns(3)
    with col1:
        twitter = st.text_input("Twitter", value=data_lama.get("twitter", "") if data_lama else "")
        facebook = st.text_input("Facebook", value=data_lama.get("facebook", "") if data_lama else "")
    with col2:
        instagram = st.text_input("Instagram", value=data_lama.get("instagram", "") if data_lama else "")
        discord = st.text_input("Discord", value=data_lama.get("discord", "") if data_lama else "")
    with col3:
        tiktok = st.text_input("TikTok", value=data_lama.get("tiktok", "") if data_lama else "")
        youtube = st.text_input("YouTube", value=data_lama.get("youtube", "") if data_lama else "")

    col_simpan, col_batal = st.columns([1, 1])
    with col_simpan:
        if st.button("✅ Simpan", key=f"simpan_{mode}"):
            medsos = {
                "twitter": twitter, "facebook": facebook, "instagram": instagram,
                "discord": discord, "tiktok": tiktok, "youtube": youtube
            }
            simpan_penggarap(nama, status, situs, medsos)
            st.success(f"Penggarap '{nama}' berhasil disimpan.")
            if mode == "edit":
                st.session_state.edit_mode = False
                st.session_state.edit_nama = ""
            elif mode == "tambah":
                st.session_state.tambah_mode = False
            rerun()
    with col_batal:
        if mode == "edit":
            if st.button("❌ Batal", key="batal_edit"):
                st.session_state.edit_mode = False
                st.session_state.edit_nama = ""
                rerun()
        elif mode == "tambah":
            if st.button("❌ Batal", key="batal_tambah"):
                st.session_state.tambah_mode = False
                rerun()

def tampilkan_penggarap_resmi_page(anime_list):
    st.set_page_config(page_title="Penggarap Anime Resmi Indonesia", layout="wide")

    st.markdown("""
    <style>
    a { text-decoration: none; margin-right: 6px; }
    table td, table th { padding: 6px 12px; border: 1px solid #ccc; text-align: left; vertical-align: top; }
    table { width: 100%; border-collapse: collapse; }
    </style>
    """, unsafe_allow_html=True)

    bulan = datetime.now().month
    musim_sekarang = (
        "dingin" if bulan in [12, 1, 2] else
        "semi" if bulan in [3, 4, 5] else
        "panas" if bulan in [6, 7, 8] else
        "gugur"
    )

    st.markdown("## 📋 Penggarap Anime Resmi Indonesia")

    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False
        st.session_state.edit_nama = ""
    if "tambah_mode" not in st.session_state:
        st.session_state.tambah_mode = False

    if st.session_state.edit_mode and st.session_state.edit_nama:
        try:
            data_lama = json.load(open(DATA_FILE)).get(st.session_state.edit_nama, {})
        except:
            data_lama = {}
        form_penggarap(nama_awal=st.session_state.edit_nama, data_lama=data_lama, mode="edit")
    else:
        if not st.session_state.tambah_mode:
            if st.button("➕ Tambah Penggarap", key="tombol_tambah_penggarap"):
                st.session_state.tambah_mode = True
                rerun()
        if st.session_state.tambah_mode:
            form_penggarap(mode="tambah")
    # Bangun daftar penggarap
    daftar = {}
    if anime_list:
        for anime in anime_list:
            musim_anime = anime.get("season", "").lower()
            for p in anime.get("proyek", []):
                nama = p.get("penggarap")
                if not nama or "fansub" in nama.lower():
                    continue
                if nama not in daftar:
                    daftar[nama] = {
                        "total": 0,
                        "jumlah_berjalan": 0
                    }
                daftar[nama]["total"] += 1
                if p.get("status", "").lower() == "berjalan" and cocok_musim(musim_sekarang, musim_anime):
                    daftar[nama]["jumlah_berjalan"] += 1

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data_json = json.load(f)
        for nama, data in data_json.items():
            if nama not in daftar:
                daftar[nama] = {
                    "total": 0,
                    "jumlah_berjalan": 0
                }

    if not daftar:
        st.warning("Belum ada penggarap aktif untuk musim ini.")
        return

    st.markdown("### 📊 Daftar Penggarap")

    # Render tabel sebagai HTML agar scroll horizontal aktif di mobile
    html = """
    <div style='overflow-x:auto'>
    <table>
    <thead>
    <tr>
        <th>Nama Penggarap</th>
        <th>Total Garapan</th>
        <th>Proyek Saat Ini</th>
        <th>Status</th>
        <th>Tautan Platform</th>
    </tr>
    </thead>
    <tbody>
    """
    for nama, info in sorted(daftar.items()):
        data_platform = data_json.get(nama, {})
        status = data_platform.get("status", "Aktif")
        platform = ambil_logo_platform(data_platform)
        html += f"""
        <tr>
            <td><b>{nama}</b></td>
            <td>{info['total']}</td>
            <td>{info['jumlah_berjalan']}</td>
            <td>{status}</td>
            <td>{platform}</td>
        </tr>
        """
    html += "</tbody></table></div>"
    st.markdown(html, unsafe_allow_html=True)

    # Tombol edit/hapus modular di bawah tabel
    st.markdown("### 🔧 Aksi Penggarap")
    for nama, info in sorted(daftar.items()):
        key_suffix = f"{nama}_{info['total']}_{info['jumlah_berjalan']}".replace(" ", "_").replace("-", "_")
        col_edit, col_hapus = st.columns([1, 1])
        with col_edit:
            if st.button(f"✏️ Edit {nama}", key=f"edit_{key_suffix}"):
                st.session_state.edit_mode = True
                st.session_state.edit_nama = nama
                rerun()
        with col_hapus:
            if st.button(f"🗑️ Hapus {nama}", key=f"hapus_{key_suffix}"):
                hapus_penggarap(nama)
                st.success(f"Penggarap '{nama}' dihapus.")
                rerun()
