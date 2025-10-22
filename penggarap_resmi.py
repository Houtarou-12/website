import streamlit as st
import json
import os
from datetime import datetime
from packaging import version
from streamlit.components.v1 import html
from streamlit_javascript import st_javascript   # ✅ tambahan

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

# ✅ Deteksi perangkat dengan streamlit-javascript
def deteksi_perangkat():
    width = st_javascript("window.innerWidth")
    if width is not None:
        st.session_state["is_mobile"] = width < 768
    else:
        st.session_state["is_mobile"] = False

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
        tautan = (data.get(kunci) or "").strip()
        if tautan:
            hasil.append(f"<a href='{tautan}' target='_blank'>{ikon}</a>")
    return " ".join(hasil) if hasil else "-"

def simpan_penggarap(nama, status, situs, medsos):
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    data[nama] = {
        "status": status,
        "situs": situs,
        **medsos
    }

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def hapus_penggarap(nama):
    if not os.path.exists(DATA_FILE):
        return
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    if nama in data:
        del data[nama]
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

def form_penggarap(nama_awal="", data_lama=None, mode="tambah"):
    st.markdown(f"### {'✏️ Edit' if mode == 'edit' else '➕ Tambah'} Penggarap")
    nama = st.text_input("Nama Penggarap", value=nama_awal)
    status_options = ["Aktif", "Nonaktif"]
    status_default = 0 if data_lama and data_lama.get("status") == "Aktif" else 1
    status = st.selectbox("Status", status_options, index=status_default)
    situs = st.text_input("Situs Web", value=(data_lama.get("situs", "") if data_lama else ""))

    col1, col2, col3 = st.columns(3)
    with col1:
        twitter = st.text_input("Twitter", value=(data_lama.get("twitter", "") if data_lama else ""))
        facebook = st.text_input("Facebook", value=(data_lama.get("facebook", "") if data_lama else ""))
    with col2:
        instagram = st.text_input("Instagram", value=(data_lama.get("instagram", "") if data_lama else ""))
        discord = st.text_input("Discord", value=(data_lama.get("discord", "") if data_lama else ""))
    with col3:
        tiktok = st.text_input("TikTok", value=(data_lama.get("tiktok", "") if data_lama else ""))
        youtube = st.text_input("YouTube", value=(data_lama.get("youtube", "") if data_lama else ""))

    col_simpan, col_batal = st.columns([1, 1])
    with col_simpan:
        if st.button("✅ Simpan", key=f"simpan_{mode}"):
            medsos = {
                "twitter": twitter,
                "facebook": facebook,
                "instagram": instagram,
                "discord": discord,
                "tiktok": tiktok,
                "youtube": youtube
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

    # Deteksi perangkat otomatis
    deteksi_perangkat()

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
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                semua = json.load(f)
            data_lama = semua.get(st.session_state.edit_nama, {})
        except Exception:
            data_lama = {}
        form_penggarap(nama_awal=st.session_state.edit_nama, data_lama=data_lama, mode="edit")
        return
    elif st.session_state.tambah_mode:
        form_penggarap(mode="tambah")
        return
    else:
        if st.button("➕ Tambah Penggarap", key="tombol_tambah_penggarap"):
            st.session_state.tambah_mode = True
            rerun()

    # Bangun daftar agregat
    daftar = {}
    if anime_list:
        for anime in anime_list:
            musim_anime = (anime.get("season") or "").lower()
            for p in anime.get("proyek", []):
                nama = p.get("penggarap")
                if not nama or "fansub" in (nama or "").lower():
                    continue
                if nama not in daftar:
                    daftar[nama] = {"total": 0, "jumlah_berjalan": 0}
                daftar[nama]["total"] += 1
                if (p.get("status", "").lower() == "berjalan") and cocok_musim(musim_sekarang, musim_anime):
                    daftar[nama]["jumlah_berjalan"] += 1

    data_json = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data_json = json.load(f)
        for nama in data_json:
            if nama not in daftar:
                daftar[nama] = {"total": 0, "jumlah_berjalan": 0}

    if not daftar:
        st.warning("Belum ada penggarap aktif untuk musim ini.")
        return

    st.markdown("### 📊 Daftar Penggarap")

    # Layout Mobile: tabel HTML scroll horizontal + highlight warna
    if st.session_state.get("is_mobile"):
        table_html = """
        <div style="overflow-x:auto;">
          <table style="border-collapse:collapse; width:100%; min-width:800px;">
            <thead>
              <tr style="background:#f0f0f0; text-align:left; color:#000;">
                <th style="padding:8px; border:1px solid #ddd;">Nama Penggarap</th>
                <th style="padding:8px; border:1px solid #ddd;">Total Garapan</th>
                <th style="padding:8px; border:1px solid #ddd;">Proyek Saat Ini</th>
                <th style="padding:8px; border:1px solid #ddd;">Status</th>
                <th style="padding:8px; border:1px solid #ddd;">Platform</th>
                <th style="padding:8px; border:1px solid #ddd;">Aksi</th>
              </tr>
            </thead>
            <tbody>
        """
        for nama, info in sorted(daftar.items()):
            data_platform = data_json.get(nama, {})
            status = data_platform.get("status", "Aktif")
            platform = ambil_logo_platform(data_platform)

            # Tentukan warna baris & teks
            if status.lower() == "aktif":
                row_bg = "#e8f5e9"   # hijau muda
                text_color = "#1b5e20"
            else:
                row_bg = "#f5f5f5"   # abu muda
                text_color = "#424242"

            table_html += f"""
              <tr style="background:{row_bg}; color:{text_color};">
                <td style="padding:8px; border:1px solid #ddd;">{nama}</td>
                <td style="padding:8px; border:1px solid #ddd; text-align:center;">{info['total']}</td>
                <td style="padding:8px; border:1px solid #ddd; text-align:center;">{info['jumlah_berjalan']}</td>
                <td style="padding:8px; border:1px solid #ddd; font-weight:bold;">{status}</td>
                <td style="padding:8px; border:1px solid #ddd;">{platform}</td>
                <td style="padding:8px; border:1px solid #ddd;">✏️ 🗑️</td>
              </tr>
            """
        table_html += "</tbody></table></div>"
        html(table_html, height=400, scrolling=True)

    # Layout Desktop: tabel kolom Streamlit + warna status
    else:
        header = st.columns([2.5, 1.2, 1.5, 1.2, 2.5, 1.5])
        header[0].markdown("**Nama Penggarap**")
        header[1].markdown("**Total Garapan**")
        header[2].markdown("**Proyek Saat Ini**")
        header[3].markdown("**Status**")
        header[4].markdown("**Tautan Platform**")
        header[5].markdown("**Aksi**")

        for nama, info in sorted(daftar.items()):
            data_platform = data_json.get(nama, {})
            status = data_platform.get("status", "Aktif")
            platform = ambil_logo_platform(data_platform)
            key_suffix = f"{nama}_{info['total']}_{info['jumlah_berjalan']}".replace(" ", "_").replace("-", "_")

            # Warna status
            status_color = "green" if status == "Aktif" else "gray"

            row = st.columns([2.5, 1.2, 1.5, 1.2, 2.5, 1.5])
            row[0].markdown(f"**{nama}**")
            row[1].markdown(str(info["total"]))
            row[2].markdown(str(info["jumlah_berjalan"]))
            row[3].markdown(f"<span style='color:{status_color}; font-weight:bold;'>{status}</span>", unsafe_allow_html=True)
            row[4].markdown(platform, unsafe_allow_html=True)
            with row[5]:
                col_edit, col_hapus = st.columns([1, 1])
                with col_edit:
                    if st.button("✏️", key=f"edit_{key_suffix}"):
                        st.session_state.edit_mode = True
                        st.session_state.edit_nama = nama
                        rerun()
                with col_hapus:
                    if st.button("🗑️", key=f"hapus_{key_suffix}"):
                        hapus_penggarap(nama)
                        st.success(f"Penggarap '{nama}' dihapus.")
                        rerun()
