import streamlit as st
import requests
from bs4 import BeautifulSoup
from utils import simpan_ke_file

def ambil_data_mal(url: str) -> dict:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            raise Exception(f"Status code: {r.status_code}")
        soup = BeautifulSoup(r.text, "html.parser")

        if not soup.find("span", itemprop="description") and not soup.find("div", class_="spaceit_pad"):
            return {"error": "Halaman bukan detail anime. Cek URL atau redirect."}

        def ambil_judul(soup):
            h1_tag = soup.find("h1", class_="title-name h1_bold_none")
            if h1_tag and h1_tag.text.strip():
                return h1_tag.text.strip()
            tag = soup.find("span", itemprop="name")
            if tag and tag.text.strip():
                return tag.text.strip()
            h1 = soup.find("h1")
            if h1 and h1.text.strip():
                return h1.text.strip()
            meta_tag = soup.find("meta", property="og:title")
            if meta_tag and meta_tag.get("content"):
                judul = meta_tag["content"].replace(" - MyAnimeList.net", "").strip()
                if judul.lower() in ["top", "myanimelist", "home"]:
                    return None
                return judul
            meta_name = soup.find("meta", attrs={"name": "title"})
            if meta_name and meta_name.get("content"):
                judul = meta_name["content"].replace(" - MyAnimeList.net", "").strip()
                if judul.lower() in ["top", "myanimelist", "home"]:
                    return None
                return judul
            title_tag = soup.find("title")
            if title_tag:
                judul = title_tag.text.replace(" - MyAnimeList.net", "").strip()
                if judul.lower() in ["top", "myanimelist", "home"]:
                    return None
                return judul
            return None

        def ubah_format_tanggal(tanggal):
            bulan_map = {
                "Jan": "Januari", "Feb": "Februari", "Mar": "Maret", "Apr": "April",
                "May": "Mei", "Jun": "Juni", "Jul": "Juli", "Aug": "Agustus",
                "Sep": "September", "Oct": "Oktober", "Nov": "November", "Dec": "Desember"
            }
            parts = tanggal.split(" to ")
            def format_tgl(t):
                for eng, indo in bulan_map.items():
                    t = t.replace(eng, indo)
                return t.strip()
            if len(parts) == 2:
                return f"{format_tgl(parts[0])} s.d {format_tgl(parts[1])}"
            return format_tgl(tanggal)

        def ambil_info_panel(soup):
            info = {
                "format": "Unknown", "episodes": "?", "status": "?",
                "aired": "?", "season": "Unknown", "studio": "?",
                "source": "?", "genres": [], "themes": [], "demographic": []
            }
            blocks = soup.find_all("div", class_="spaceit_pad")
            for block in blocks:
                label = block.get_text(" ", strip=True).lower()
                links = [a.text.strip() for a in block.find_all("a")]
                raw_text = block.text.strip()
                if "type:" in label:
                    info["format"] = links[0] if links else raw_text.replace("Type:", "").strip()
                elif "episodes:" in label:
                    info["episodes"] = raw_text.replace("Episodes:", "").strip()
                elif "status:" in label:
                    info["status"] = raw_text.replace("Status:", "").strip()
                elif "aired:" in label:
                    info["aired"] = ubah_format_tanggal(raw_text.replace("Aired:", "").strip())
                elif "premiered:" in label:
                    info["season"] = links[0] if links else "Unknown"
                elif "studios:" in label:
                    info["studio"] = links[0] if links else "?"
                elif "source:" in label:
                    info["source"] = raw_text.replace("Source:", "").strip()
                elif "genres:" in label:
                    info["genres"] = links
                elif "theme:" in label or "themes:" in label:
                    info["themes"] = links
                elif "demographic:" in label or "demographics:" in label:
                    info["demographic"] = links
            return info

        title = ambil_judul(soup)
        if not title:
            return {"error": "Judul gagal diambil"}

        rating = soup.find("span", itemprop="ratingValue")
        rating = rating.text.strip() if rating else "N/A"

        img_tag = soup.find("img", class_="ac")
        cover = img_tag.get("data-src") or img_tag.get("src") if img_tag else "https://via.placeholder.com/300x400?text=No+Image"

        sinopsis_tag = soup.find("span", itemprop="description")
        sinopsis = sinopsis_tag.text.strip() if sinopsis_tag else "Sinopsis belum tersedia."

        info = ambil_info_panel(soup)

        return {
            "title": title,
            "format": info["format"],
            "episodes": info["episodes"],
            "status": info["status"],
            "aired": info["aired"],
            "season": info["season"],
            "studio": info["studio"],
            "source": info["source"],
            "rating": rating,
            "cover": cover,
            "mal_url": url,
            "sinopsis": sinopsis,
            "genres": info["genres"],
            "themes": info["themes"],
            "demographic": info["demographic"],
            "proyek": [],
            "sinopsis_manual": ""
        }
    except Exception as e:
        return {"error": str(e)}

def refresh_data(anime: dict, selected_url: str):
    if st.button("🔄 Perbarui Data"):
        data_baru = ambil_data_mal(anime.get("mal_url"))
        if "error" in data_baru:
            st.error(f"Gagal memperbarui: {data_baru['error']}")
        else:
            for i, a in enumerate(st.session_state["anime_list"]):
                if a.get("mal_url") == selected_url:
                    for k in ["format", "episodes", "status", "aired", "season", "studio", "source", "rating", "genres", "themes", "demographic"]:
                        st.session_state["anime_list"][i][k] = data_baru.get(k, a.get(k))
                    break
            simpan_ke_file(st.session_state["anime_list"])
            st.success("Data berhasil diperbarui.")
            st.query_params = {"anime": selected_url}
def edit_sinopsis(anime: dict, selected_url: str):
    sinopsis_tampil = anime.get("sinopsis_manual") or anime.get("sinopsis", "Sinopsis belum tersedia.")
    st.write(sinopsis_tampil)

    if st.button("✏️ Edit Sinopsis"):
        with st.form("form_edit_sinopsis"):
            sinopsis_baru = st.text_area("Ubah Sinopsis", value=sinopsis_tampil)
            col_simpan, col_batal = st.columns([1, 1])
            with col_simpan:
                simpan_sinopsis = st.form_submit_button("Simpan")
            with col_batal:
                batal_sinopsis = st.form_submit_button("Batal")

        if simpan_sinopsis:
            for i, a in enumerate(st.session_state["anime_list"]):
                if a.get("mal_url") == selected_url:
                    st.session_state["anime_list"][i]["sinopsis_manual"] = sinopsis_baru
                    break
            simpan_ke_file(st.session_state["anime_list"])
            st.success("Sinopsis berhasil diperbarui.")
            st.query_params = {"anime": selected_url}

        if batal_sinopsis:
            st.info("Perubahan sinopsis dibatalkan.")
            st.query_params = {"anime": selected_url}
