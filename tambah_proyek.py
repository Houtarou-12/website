import streamlit as st
import json
import os

DATA_FILE = "data_penggarap.json"

def ambil_nama_penggarap():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
    return sorted(data.keys())

def tampilkan_tambah_proyek_page():
    st.set_page_config(page_title="Tambah Proyek Garapan", layout="wide")
    st.markdown("## ➕ Tambah Proyek Garapan")

    nama_penggarap_list = ambil_nama_penggarap()
    if not nama_penggarap_list:
        st.warning("Belum ada penggarap terdaftar. Tambahkan dulu di halaman Penggarap.")
        return

    nama = st.selectbox("Nama Penggarap", nama_penggarap_list)
    judul = st.text_input("Judul Anime")
    musim = st.text_input("Musim & Tahun (contoh: Fall 2025)")
    status = st.selectbox("Status Proyek", ["Berjalan", "Selesai", "Mangkrak", "Tentatif"])
    format = st.selectbox("Format", ["Softsub", "Hardsub", "Dubbing", "Streaming"])
    link = st.text_input("Tautan Proyek")

    if st.button("Simpan Proyek"):
        st.success(f"Proyek '{judul}' berhasil ditambahkan untuk {nama}")
