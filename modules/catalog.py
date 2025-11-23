import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import re

DATA_FILE = "data/anime_db.json"
PROJECT_FILE = "data/project_garapan.json"

ID_MONTHS = {
    "January": "Januari", "February": "Februari", "March": "Maret",
    "April": "April", "May": "Mei", "June": "Juni", "July": "Juli",
    "August": "Agustus", "September": "September", "October": "Oktober",
    "November": "November", "December": "Desember",
    "Jan": "Januari", "Feb": "Februari", "Mar": "Maret", "Apr": "April",
    "May": "Mei", "Jun": "Juni", "Jul": "Juli", "Aug": "Agustus",
    "Sep": "September", "Oct": "Oktober", "Nov": "November", "Dec": "Desember",
}

SEASON_MAP_ID = {
    "Januari": "Winter", "Februari": "Winter", "Maret": "Winter",
    "April": "Spring", "Mei": "Spring", "Juni": "Spring",
    "Juli": "Summer", "Agustus": "Summer", "September": "Fall",
    "Oktober": "Fall", "November": "Fall", "Desember": "Fall",
}

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_projects():
    if os.path.exists(PROJECT_FILE):
        with open(PROJECT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_projects(data):
    with open(PROJECT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_project(anime_title, proyek_dict):
    data = load_projects()
    for entry in data:
        if entry["anime_title"].lower() == anime_title.lower():
            entry["projects"].append(proyek_dict)
            save_projects(data)
            return
    data.append({"anime_title": anime_title, "projects": [proyek_dict]})
    save_projects(data)

def update_project(anime_title, id_proyek, proyek_baru):
    data = load_projects()
    for entry in data:
        if entry["anime_title"].lower() == anime_title.lower():
            if 0 <= id_proyek < len(entry["projects"]):
                entry["projects"][id_proyek] = proyek_baru
                save_projects(data)
                return True
    return False

def delete_project(anime_title, id_proyek):
    data = load_projects()
    for entry in data:
        if entry["anime_title"].lower() == anime_title.lower():
            if 0 <= id_proyek < len(entry["projects"]):
                entry["projects"].pop(id_proyek)
                save_projects(data)
                return True
    return False

def extract_field(soup, label):
    for div in soup.select("div.spaceit_pad"):
        text = div.get_text(strip=True)
        if text.startswith(label):
            return text.replace(label, "").strip()
    return "-"
def parse_mal_date_to_id(text):
    """Konversi tanggal MAL ke format Indonesia (contoh: 3 Apr 2020 -> 3 April 2020)."""
    if not text or text == "-":
        return "-"
    raw = " ".join(text.split())
    parts = raw.split(" to ")

    def to_id_date(en_date):
        en_date = en_date.strip()
        try:
            dt = datetime.strptime(en_date, "%b %d, %Y")
            month_id = ID_MONTHS[dt.strftime("%b")]
            return f"{dt.day} {month_id} {dt.year}"
        except Exception:
            try:
                dt = datetime.strptime(en_date, "%B %d, %Y")
                month_id = ID_MONTHS[dt.strftime("%B")]
                return f"{dt.day} {month_id} {dt.year}"
            except Exception:
                return en_date

    if len(parts) == 2:
        start_id = to_id_date(parts[0])
        end_raw = parts[1].strip()
        end_id = to_id_date(end_raw) if end_raw != "?" else "?"
        return f"{start_id} s.d {end_id}"
    else:
        return to_id_date(raw)

def extract_musim_from_airing_id(airing_id):
    if not airing_id or airing_id == "-":
        return "-"
    try:
        start_part = airing_id.split(" s.d ")[0]
        parts = start_part.split()
        if len(parts) < 3:
            return "-"
        bulan = parts[1]
        tahun = parts[2]
        musim_eng = SEASON_MAP_ID.get(bulan, "-")
        if musim_eng == "-":
            return "-"
        return f"{musim_eng} {tahun}"
    except Exception:
        return "-"

def clean_text(text):
    if text is None:
        return "-"
    text = text.replace("Â", "").replace("â", "")
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.split("\n")]
    cleaned = "\n".join([ln for ln in lines if ln])
    return cleaned.strip()

def scrape_anime_details(url):
    res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if res.status_code != 200:
        raise Exception(f"Gagal fetch {url} (status {res.status_code})")

    soup = BeautifulSoup(res.text, "html.parser")

    title_tag = soup.find("h1")
    title = title_tag.get_text(strip=True) if title_tag else "-"

    poster_tag = soup.select_one("div.leftside img")
    poster_url = "-"
    if poster_tag:
        if poster_tag.has_attr("data-src"):
            poster_url = poster_tag["data-src"]
        elif poster_tag.has_attr("src"):
            poster_url = poster_tag["src"]
    if poster_url == "-" or not poster_url:
        poster_url = "/static/img/no-poster.png"

    anime_type = extract_field(soup, "Type:")
    source = extract_field(soup, "Source:")
    status = extract_field(soup, "Status:")
    episodes = extract_field(soup, "Episodes:")

    airing_raw = extract_field(soup, "Aired:")
    airing = parse_mal_date_to_id(airing_raw)

    studios, genres, themes, demographics = [], [], [], []
    for div in soup.select("div.spaceit_pad"):
        text = div.get_text(strip=True)
        if text.startswith("Studios:") or text.startswith("Studio:"):
            for a in div.find_all("a"):
                studios.append(a.get_text(strip=True))
        if text.startswith("Genres:") or text.startswith("Genre:"):
            for a in div.find_all("a"):
                genres.append(a.get_text(strip=True))
        if text.startswith("Themes:") or text.startswith("Theme:"):
            for a in div.find_all("a"):
                themes.append(a.get_text(strip=True))
        if text.startswith("Demographic:") or text.startswith("Demographics:"):
            for a in div.find_all("a"):
                demographics.append(a.get_text(strip=True))

    synopsis_tag = soup.select_one("p[itemprop='description']")
    synopsis_raw = synopsis_tag.get_text(separator="\n") if synopsis_tag else "-"
    synopsis_cleaned = clean_text(synopsis_raw)
    if synopsis_cleaned.count("\n") <= 1 and len(synopsis_cleaned) <= 100:
        synopsis = synopsis_cleaned.replace("\n", " ")
    else:
        synopsis = synopsis_cleaned

    score_tag = soup.select_one("span[itemprop='ratingValue']")
    score = score_tag.get_text(strip=True) if score_tag else "-"

    musim = extract_musim_from_airing_id(airing)
    year = "-"
    if musim != "-" and len(musim.split()) == 2:
        year = musim.split()[1]

    return {
        "title": title,
        "poster": poster_url,
        "type": anime_type,
        "source": source,
        "status": status,
        "episodes": episodes,
        "airing": airing,
        "studios": studios,
        "genres": genres,
        "themes": themes,
        "demographics": demographics,
        "synopsis": synopsis,
        "score": score,
        "url": url,
        "musim": musim,
        "year": year
    }

def get_anime_data(url=None):
    if url:
        return scrape_anime_details(url)
    else:
        return load_data()

def scrape_detail_mal(url):
    return scrape_anime_details(url)

def add_anime(url):
    data = load_data()
    anime = scrape_anime_details(url)
    for a in data:
        if a["title"].lower() == anime["title"].lower():
            a.update(anime)
            save_data(data)
            return anime, "duplicate"
    data.append(anime)
    save_data(data)
    return anime, "new"

def search_anime(keyword):
    data = load_data()
    results = []
    for anime in data:
        if keyword.lower() in anime["title"].lower():
            results.append(anime)
    return results

def list_all():
    return load_data()

def get_musim_terbaru(data):
    musim_set = set()
    for a in data:
        if "musim" in a and a["musim"] != "-":
            musim_set.add(a["musim"])
    if not musim_set:
        return "-"
    def musim_key(m):
        musim_order = {"Winter": 1, "Spring": 2, "Summer": 3, "Fall": 4}
        try:
            musim, tahun = m.split()
            return int(tahun) * 10 + musim_order.get(musim, 0)
        except:
            return 0
    return sorted(musim_set, key=musim_key, reverse=True)[0]
