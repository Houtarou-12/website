from flask import Flask, render_template, request, redirect, url_for, jsonify
from modules import catalog, jadwal

app = Flask(__name__)

# Filter Jinja untuk konversi label musim ke Bahasa Indonesia + emoji
def musim_id_to_label(musim_str):
    if not musim_str or musim_str == "-":
        return "Musim Tidak Diketahui"
    musim_map = {
        "Spring": "Musim Semi 🌸",
        "Summer": "Musim Panas ☀️",
        "Fall": "Musim Gugur 🍂",
        "Winter": "Musim Dingin ❄️"
    }
    try:
        musim, tahun = musim_str.split()
        label = musim_map.get(musim, musim)
        return f"{label} {tahun}"
    except:
        return musim_str

app.jinja_env.filters["musim_id_to_label"] = musim_id_to_label

@app.route("/", methods=["GET", "POST"])
def halaman_katalog():
    message = ""
    if request.method == "POST":
        mal_url = request.form.get("mal_url")
        try:
            result, status = catalog.add_anime(mal_url)
            if status == "duplicate":
                message = "⚠️ Anime sudah ada di database!"
            else:
                message = "✅ Anime berhasil ditambahkan!"
        except Exception as e:
            message = f"❌ Gagal: {e}"

    # 🔍 Load data tanpa scraping ulang
    data = catalog.load_data()
    for i, anime in enumerate(data):
        anime["id"] = i

    # Ambil parameter GET untuk filter/pencarian
    judul = request.args.get("judul", "").lower()
    genre = request.args.get("genre", "")
    theme = request.args.get("theme", "")
    demografi = request.args.get("demografi", "")
    musim = request.args.get("musim", "")
    tahun = request.args.get("tahun", "")

    hasil = data
    if judul:
        hasil = [a for a in hasil if judul in a["title"].lower()]
    if genre:
        hasil = [a for a in hasil if genre in a.get("genres", [])]
    if theme:
        hasil = [a for a in hasil if theme in a.get("themes", [])]
    if demografi:
        hasil = [a for a in hasil if demografi in a.get("demographics", [])]
    if musim:
        hasil = [a for a in hasil if a.get("musim") == musim or a.get("season_label") == musim]
    if tahun:
        hasil = [a for a in hasil if str(a.get("year")) == tahun]

    musim_aktif = catalog.get_musim_terbaru(data)
    anime_musiman = [a for a in data if a.get("musim") == musim_aktif]

    if len(anime_musiman) < 5:
        while len(anime_musiman) < 5:
            anime_musiman.append({
                "title": "Belum ada data",
                "poster": "/static/img/no-poster.png",
                "score": "-",
                "genres": [],
                "themes": [],
                "demographics": [],
                "id": -1
            })

    musim_label = musim_aktif if musim_aktif else "Musim Terbaru"

    return render_template(
        "katalog.html",
        anime_list=hasil,
        anime_musiman=anime_musiman,
        musim_label=musim_label,
        message=message,
        judul=judul,
        genre=genre,
        theme=theme,
        demografi=demografi,
        musim=musim,
        tahun=tahun
    )
@app.route("/detail/<int:index>")
def halaman_detail_anime(index):
    data = catalog.get_anime_data()
    if not data:
        return "Belum ada anime di database.", 404
    if index < 0 or index >= len(data):
        return "Anime tidak ditemukan", 404

    anime = data[index]
    projects = []
    for entry in catalog.load_projects():
        if entry["anime_title"].lower() == anime["title"].lower():
            projects = entry["projects"]
            break

    daftar_penggarap = sorted([
        "Muse Indonesia",
        "Ani-One Asia",
        "Ani-One Indonesia",
        "Tropics Anime Asia",
        "iQIYI",
        "Netflix",
        "Bstation",
        "Crunchyroll",
        "Catchplay+",
        "Laftel"
    ])

    return render_template(
        "detail_anime.html",
        anime=anime,
        projects=projects,
        index=index,
        daftar_penggarap=daftar_penggarap
    )

# 🔄 Route untuk memperbarui data scraping manual
@app.route("/detail/<int:index>/update", methods=["POST"])
def perbarui_detail_anime(index):
    data = catalog.get_anime_data()
    if not data or index < 0 or index >= len(data):
        return "Anime tidak ditemukan", 404

    anime = data[index]
    try:
        fresh = catalog.scrape_anime_details(anime["url"])
        fresh["id"] = index
        data[index] = fresh
        catalog.save_data(data)
        message = "✅ Data berhasil diperbarui!"
    except Exception as e:
        message = f"❌ Gagal memperbarui: {e}"

    return redirect(url_for("halaman_detail_anime", index=index))

@app.route("/proyek", methods=["GET"])
def halaman_proyek():
    projects = catalog.load_projects()
    proyek_list = []
    for entry in projects:
        for p in entry["projects"]:
            proyek_list.append({
                "judul": entry["anime_title"],
                "status": p.get("status", "-"),
                "tahun": "-"
            })
    return render_template("proyek.html", proyek_list=proyek_list)

@app.route("/tambah-proyek", methods=["POST"])
def simpan_proyek():
    anime_title = request.form.get("anime_title")
    proyek_dict = {
        "penggarap": request.form.get("penggarap"),
        "status": request.form.get("status"),
        "takarir": request.form.get("takarir"),
        "unggahan": request.form.get("unggahan"),
        "catatan": request.form.get("catatan")
    }
    try:
        catalog.add_project(anime_title, proyek_dict)
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))

@app.route("/detail/<int:index>/proyek/<int:id_proyek>/hapus", methods=["POST"])
def hapus_proyek(index, id_proyek):
    data = catalog.get_anime_data()
    if index < 0 or index >= len(data):
        return "Anime tidak ditemukan", 404
    anime_title = data[index]["title"]
    success = catalog.delete_project(anime_title, id_proyek)
    if success:
        return redirect(url_for("halaman_detail_anime", index=index))
    return "Gagal menghapus proyek", 400

@app.route("/jadwal")
def halaman_jadwal():
    data = jadwal.load_jadwal()
    return render_template("jadwal.html", jadwal_data=data)

@app.route("/tambah-jadwal", methods=["POST"])
def tambah_jadwal():
    link = request.form.get("link")
    hari = request.form.get("hari")
    jam_h = request.form.get("jam_h")
    jam_m = request.form.get("jam_m")
    catatan = request.form.get("catatan")

    try:
        id_str = link.strip().split("/detail/")[1]
        anime_id = int(id_str)
        semua_anime = catalog.get_anime_data()
        judul = semua_anime[anime_id]["title"]
    except Exception:
        return "Link detail tidak valid atau anime tidak ditemukan", 400

    jam = f"{jam_h}:{jam_m}" if jam_h and jam_m else "-"
    entry = {
        "title": judul,
        "link": link,
        "hari": hari,
        "jam": jam,
        "catatan": catatan
    }
    jadwal.add_entry(hari, entry)
    return redirect(url_for("halaman_jadwal"))

@app.route("/edit-jadwal", methods=["POST"])
def edit_jadwal():
    link = request.form.get("link")
    hari_baru = request.form.get("hari")
    jam_h = request.form.get("jam_h")
    jam_m = request.form.get("jam_m")
    catatan_baru = request.form.get("catatan")

    try:
        id_str = link.strip().split("/detail/")[1]
        anime_id = int(id_str)
        semua_anime = catalog.get_anime_data()
        judul = semua_anime[anime_id]["title"]
    except Exception:
        return "Link detail tidak valid atau anime tidak ditemukan", 400

    jam_baru = f"{jam_h}:{jam_m}" if jam_h and jam_m else "-"
    jadwal.update_entry(judul, link, hari_baru, jam_baru, catatan_baru)
    return redirect(url_for("halaman_jadwal"))

@app.route("/hapus-jadwal", methods=["POST"])
def hapus_jadwal():
    title = request.form.get("hapus_title")
    link = request.form.get("hapus_link")
    if not title or not link:
        return "Data tidak lengkap", 400

    jadwal.delete_entry(title, link)
    return redirect(url_for("halaman_jadwal"))

if __name__ == "__main__":
    app.run(debug=True)
