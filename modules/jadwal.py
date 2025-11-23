import json
import os

JADWAL_FILE = "data_jadwal.json"

def load_jadwal():
    if not os.path.exists(JADWAL_FILE):
        return {
            "Senin": [],
            "Selasa": [],
            "Rabu": [],
            "Kamis": [],
            "Jumat": [],
            "Sabtu": [],
            "Minggu": [],
            "Tidak Diketahui": []
        }
    with open(JADWAL_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_jadwal(data):
    with open(JADWAL_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def add_entry(hari, entry):
    data = load_jadwal()
    if hari not in data:
        data["Tidak Diketahui"].append(entry)
    else:
        data[hari].append(entry)
    save_jadwal(data)

def delete_entry(title, link):
    data = load_jadwal()
    for hari, daftar in data.items():
        for i, entry in enumerate(daftar):
            if entry["title"] == title and entry["link"] == link:
                del data[hari][i]
                save_jadwal(data)
                return True
    return False
def update_entry(title, link, new_hari, new_jam, new_catatan):
    """
    Update jadwal tayang untuk anime tertentu.
    - Hapus entry lama berdasarkan title + link
    - Tambahkan entry baru ke hari yang dipilih
    """
    data = load_jadwal()
    found = False

    # Cari dan hapus entry lama
    for hari, daftar in data.items():
        for i, entry in enumerate(daftar):
            if entry["title"] == title and entry["link"] == link:
                del data[hari][i]
                found = True
                break
        if found:
            break

    # Jika ditemukan, tambahkan entry baru ke hari baru
    if found:
        new_entry = {
            "title": title,
            "link": link,
            "hari": new_hari,
            "jam": new_jam,
            "catatan": new_catatan
        }
        if new_hari not in data:
            data["Tidak Diketahui"].append(new_entry)
        else:
            data[new_hari].append(new_entry)
        save_jadwal(data)
        return True
    return False
