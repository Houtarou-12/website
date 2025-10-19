import streamlit as st
from utils import simpan_ke_file

def tambah_proyek_form():
    st.markdown("## Tambah Proyek Garapan")
    penggarap_list = [
        "Muse Indonesia", "Crunchyroll", "Netflix", "Bstation",
        "Disney+", "Ani-One Asia", "Ani-One Indonesia", "Tropics Anime Asia"
    ]
    with st.form("form_tambah_proyek"):
        penggarap = st.selectbox("Nama Penggarap", options=penggarap_list)
        status = st.selectbox("Status Proyek", options=["Tentatif", "Berjalan", "Mangkrak", "Selesai"])
        format_unggahan = st.selectbox("Format Unggahan", options=["Softsub", "Hardsub"])
        link = st.text_input("Tautan Unggahan (URL)")
        catatan = st.text_area("Catatan (opsional)")
        simpan = st.form_submit_button("Simpan")
        batal = st.form_submit_button("Batal")

    if simpan:
        anime_url = st.query_params.get("anime", None)
        if not anime_url:
            st.warning("Proyek hanya bisa ditambahkan dari halaman detail anime.")
            return
        for i, a in enumerate(st.session_state["anime_list"]):
            if a.get("mal_url") == anime_url:
                st.session_state["anime_list"][i].setdefault("proyek", []).append({
                    "penggarap": penggarap,
                    "status": status,
                    "format": format_unggahan,
                    "link": link,
                    "catatan": catatan
                })
                break
        simpan_ke_file(st.session_state["anime_list"])
        st.success("Proyek berhasil ditambahkan.")
        st.session_state["tambah_proyek"] = None
        st.query_params = {"anime": anime_url}

    if batal:
        st.session_state["tambah_proyek"] = None

def edit_proyek_form():
    anime_url, idx = st.session_state.get("edit_proyek", (None, None))
    if not anime_url:
        return
    anime = next((a for a in st.session_state["anime_list"] if a.get("mal_url") == anime_url), None)
    if not anime or idx >= len(anime.get("proyek", [])):
        st.error("Proyek tidak ditemukan.")
        return

    proyek = anime["proyek"][idx]
    penggarap_list = [
        "Muse Indonesia", "Crunchyroll", "Netflix", "Bstation",
        "Disney+", "Ani-One Asia", "Ani-One Indonesia", "Tropics Anime Asia"
    ]

    st.markdown("## Edit Proyek Garapan")
    with st.form(f"form_edit_proyek_{idx}"):
        penggarap = st.selectbox("Nama Penggarap", options=penggarap_list, index=penggarap_list.index(proyek["penggarap"]) if proyek["penggarap"] in penggarap_list else 0)
        status = st.selectbox("Status Proyek", options=["Tentatif", "Berjalan", "Mangkrak", "Selesai"], index=["Tentatif", "Berjalan", "Mangkrak", "Selesai"].index(proyek["status"]))
        format_unggahan = st.selectbox("Format Unggahan", options=["Softsub", "Hardsub"], index=["Softsub", "Hardsub"].index(proyek["format"]))
        link = st.text_input("Tautan Unggahan (URL)", value=proyek["link"])
        catatan = st.text_area("Catatan (opsional)", value=proyek.get("catatan", ""))
        simpan = st.form_submit_button("Simpan")
        batal = st.form_submit_button("Batal")

    if simpan:
        proyek.update({
            "penggarap": penggarap,
            "status": status,
            "format": format_unggahan,
            "link": link,
            "catatan": catatan
        })
        simpan_ke_file(st.session_state["anime_list"])
        st.success("Proyek berhasil diperbarui.")
        st.session_state["edit_proyek"] = None
        st.query_params = {"anime": anime_url}

    if batal:
        st.session_state["edit_proyek"] = None
        st.query_params = {"anime": anime_url}
