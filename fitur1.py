import streamlit as st

def sidebar_kiri():
    with st.sidebar:
        col_logo, col_judul = st.columns([1, 4])
        with col_logo:
            st.image("logo.png", width=50)
        with col_judul:
            st.markdown("""
            <div style="margin-top:-2px;">
                <span style="font-size:22px;font-weight:bold;line-height:1.1;">ANIME</span><br>
                <span style="font-size:16px;line-height:1.1;">INDONESIA</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        if st.button("🏠 Halaman Utama", key="btn_home"):
            st.query_params = {}

        with st.expander("👥 Penggarap", expanded=False):
            if st.button("📌 Resmi", key="btn_penggarap_resmi"):
                st.query_params = {"menu": "penggarap_resmi"}
            if st.button("🎌 Fansub", key="btn_penggarap_fansub"):
                st.query_params = {"menu": "penggarap_fansub"}

        with st.expander("🔗 Tautan", expanded=False):
            if st.button("➕ +Penggarap", key="btn_tautan_penggarap"):
                st.query_params = {"menu": "tautan_penggarap"}
            if st.button("💬 Discord", key="btn_tautan_discord"):
                st.query_params = {"menu": "tautan_discord"}
            if st.button("❤️ Donasi", key="btn_tautan_donasi"):
                st.query_params = {"menu": "tautan_donasi"}

        st.markdown("<div style='height:100vh;'></div>", unsafe_allow_html=True)

        if st.button("❓ Bantuan", key="btn_bantuan"):
            st.query_params = {"menu": "bantuan"}

        st.markdown("---")
        col_toggle, col_label = st.columns([1, 2])
        with col_toggle:
            mode_toggle = st.toggle("", value=st.session_state.get("is_mobile", False), key="toggle_mode")
            st.session_state["is_mobile"] = mode_toggle
        with col_label:
            st.markdown("📱" if st.session_state["is_mobile"] else "🖥️")


def tampilkan_menu_khusus():
    menu = st.query_params.get("menu", None)
    if menu == "penggarap_fansub":
        st.markdown("## 🎌 Fansub")
        st.info("Daftar grup fansub yang menerjemahkan anime secara sukarela.")
    elif menu == "tautan_penggarap":
        st.markdown("## ➕ Tambah Penggarap")
        st.info("Form atau tautan untuk menambahkan penggarap baru.")
    elif menu == "tautan_discord":
        st.markdown("## 💬 Discord")
        st.markdown("[Gabung ke Discord kami](https://discord.gg/example)")
    elif menu == "tautan_donasi":
        st.markdown("## ❤️ Donasi")
        st.markdown("Dukung proyek ini melalui [Trakteer](https://trakteer.id) atau [Saweria](https://saweria.co)")
    elif menu == "bantuan":
        st.markdown("## ❓ Bantuan")
        st.info("Jika kamu mengalami kendala, hubungi admin atau cek dokumentasi.")
