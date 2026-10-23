import sqlite3
from datetime import date, datetime

from flask import Flask, flash, redirect, render_template, request, url_for

# ---------------------------------------------------------------------
# 1. KONFIGURASI APLIKASI
# ---------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = "kunci-rahasia-ets-inventaris"  # Dibutuhkan untuk flash message

DATABASE = "inventaris.db"  # File database SQLite (dibuat otomatis saat dijalankan)
NAMA_SISTEM = "Sistem Informasi Manajemen Inventaris Barang"

# Pilihan kondisi barang (dipakai pada form, validasi, badge, dan laporan)
KONDISI_BARANG = ["Baik", "Rusak Ringan", "Rusak Berat"]

# Barang dengan stok <= nilai ini dianggap "stok rendah" pada dashboard
BATAS_STOK_RENDAH = 5

# Label rapi untuk pesan validasi form barang
LABEL_KOLOM = {
    "kode_barang": "Kode Barang",
    "nama_barang": "Nama Barang",
    "kategori": "Kategori",
    "lokasi": "Lokasi Penyimpanan",
}


# ---------------------------------------------------------------------
# 2. KONEKSI DAN INISIALISASI DATABASE
# ---------------------------------------------------------------------
def get_db():
    """Membuka koneksi ke database SQLite.

    row_factory diatur ke sqlite3.Row agar hasil query dapat diakses
    dengan nama kolom, misalnya barang["nama_barang"].
    """
    koneksi = sqlite3.connect(DATABASE)
    koneksi.row_factory = sqlite3.Row
    return koneksi


def init_db():
    """Membuat tabel dan mengisi data contoh jika database belum ada.

    Fungsi ini dipanggil otomatis setiap kali aplikasi dijalankan,
    sehingga file inventaris.db terbentuk sendiri tanpa perintah manual.
    """
    koneksi = get_db()
    kursor = koneksi.cursor()

    # Tabel barang: master data inventaris
    kursor.execute(
        """
        CREATE TABLE IF NOT EXISTS barang (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            kode_barang        TEXT    NOT NULL UNIQUE,
            nama_barang        TEXT    NOT NULL,
            kategori           TEXT    NOT NULL,
            lokasi             TEXT    NOT NULL,
            jumlah_stok        INTEGER NOT NULL DEFAULT 0,
            kondisi            TEXT    NOT NULL,
            tanggal_pencatatan TEXT    NOT NULL
        )
        """
    )

    # Tabel transaksi: riwayat barang masuk dan barang keluar
    kursor.execute(
        """
        CREATE TABLE IF NOT EXISTS transaksi (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            barang_id  INTEGER NOT NULL,
            jenis      TEXT    NOT NULL,
            jumlah     INTEGER NOT NULL,
            tanggal    TEXT    NOT NULL,
            keterangan TEXT,
            FOREIGN KEY (barang_id) REFERENCES barang (id)
        )
        """
    )

    # Isi data contoh hanya saat tabel barang masih kosong (pertama kali dijalankan)
    kursor.execute("SELECT COUNT(*) FROM barang")
    if kursor.fetchone()[0] == 0:
        data_barang_contoh = [
            ("INV-001", "Laptop Lenovo ThinkPad", "Elektronik",        "Ruang Laboratorium 1", 8,  "Baik",         "2025-01-10"),
            ("INV-002", "Printer Epson L3210",    "Elektronik",        "Ruang Administrasi",   3,  "Rusak Ringan", "2025-01-12"),
            ("INV-003", "Meja Kerja Kayu",        "Perabot Kantor",    "Ruang Kelas A",        20, "Baik",         "2025-01-15"),
            ("INV-004", "Kursi Putar Kantor",     "Perabot Kantor",    "Ruang Kelas B",        15, "Baik",         "2025-01-18"),
            ("INV-005", "Lemari Arsip Besi",      "Perabot Kantor",    "Ruang Arsip",          4,  "Baik",         "2025-01-20"),
            ("INV-006", "Proyektor Epson EB-X51", "Elektronik",        "Ruang Laboratorium 2", 2,  "Rusak Berat",  "2025-02-01"),
            ("INV-007", "Sapu Ijuk",              "Alat Kebersihan",   "Gudang Utama",         6,  "Baik",         "2025-02-05"),
            ("INV-008", "Kertas HVS A4 (pak)",    "Alat Tulis Kantor", "Gudang Utama",         25, "Baik",         "2025-02-08"),
        ]
        kursor.executemany(
            """
            INSERT INTO barang
                (kode_barang, nama_barang, kategori, lokasi, jumlah_stok, kondisi, tanggal_pencatatan)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            data_barang_contoh,
        )

        data_transaksi_contoh = [
            (1, "masuk",  10, "2025-01-15", "Stok awal dari vendor"),
            (3, "masuk",   5, "2025-02-01", "Pengadaan perabot kantor"),
            (8, "masuk",  40, "2025-02-10", "Pesanan kertas HVS bulanan"),
            (8, "keluar", 15, "2025-03-05", "Pemakaian rutin administrasi"),
            (1, "keluar",  2, "2025-03-12", "Dipinjam unit produksi"),
        ]
        kursor.executemany(
            """
            INSERT INTO transaksi (barang_id, jenis, jumlah, tanggal, keterangan)
            VALUES (?, ?, ?, ?, ?)
            """,
            data_transaksi_contoh,
        )

    koneksi.commit()
    koneksi.close()


# ---------------------------------------------------------------------
# 3. VARIABEL GLOBAL UNTUK SEMUA TEMPLATE
# ---------------------------------------------------------------------
@app.context_processor
def variabel_global_template():
    """Menyediakan variabel dan fungsi bantu yang bisa dipakai semua template."""

    def warna_badge_kondisi(kondisi):
        """Mengembalikan kelas warna Bootstrap sesuai kondisi barang."""
        peta_warna = {
            "Baik": "success",
            "Rusak Ringan": "warning",
            "Rusak Berat": "danger",
        }
        return peta_warna.get(kondisi, "secondary")

    return {
        "nama_sistem": NAMA_SISTEM,
        "KONDISI_BARANG": KONDISI_BARANG,
        "batas_stok_rendah": BATAS_STOK_RENDAH,
        "tahun_sekarang": date.today().year,
        "tanggal_hari_ini": date.today().strftime("%d-%m-%Y"),      # untuk ditampilkan
        "tanggal_iso_hari_ini": date.today().strftime("%Y-%m-%d"),  # untuk nilai default input date
        "badge_kondisi": warna_badge_kondisi,
    }


# ---------------------------------------------------------------------
# 4. FUNGSI BANTU (HELPER)
# ---------------------------------------------------------------------
def ambil_barang(barang_id):
    """Mengambil satu data barang berdasarkan ID. Mengembalikan None jika tidak ada."""
    koneksi = get_db()
    barang = koneksi.execute("SELECT * FROM barang WHERE id = ?", (barang_id,)).fetchone()
    koneksi.close()
    return barang


def validasi_form_barang(form):
    """Memvalidasi input formulir tambah/edit barang dari sisi server.

    Mengembalikan tuple (data, daftar_error).
    """
    daftar_error = []

    data = {
        "kode_barang": (form.get("kode_barang") or "").strip(),
        "nama_barang": (form.get("nama_barang") or "").strip(),
        "kategori": (form.get("kategori") or "").strip(),
        "lokasi": (form.get("lokasi") or "").strip(),
        "jumlah_stok": (form.get("jumlah_stok") or "").strip(),
        "kondisi": (form.get("kondisi") or "").strip(),
        "tanggal_pencatatan": (form.get("tanggal_pencatatan") or "").strip(),
    }

    # Jika tanggal kosong, otomatis memakai tanggal hari ini
    if not data["tanggal_pencatatan"]:
        data["tanggal_pencatatan"] = date.today().strftime("%Y-%m-%d")

    # a. Kolom teks wajib tidak boleh kosong
    for kolom, label in LABEL_KOLOM.items():
        if not data[kolom]:
            daftar_error.append(f"Kolom {label} wajib diisi.")

    # b. Jumlah stok harus angka bulat >= 0 (tidak boleh negatif)
    if not data["jumlah_stok"]:
        daftar_error.append("Kolom Jumlah Stok wajib diisi.")
    else:
        try:
            stok = int(data["jumlah_stok"])
            if stok < 0:
                daftar_error.append("Jumlah stok tidak boleh bernilai negatif.")
            else:
                data["jumlah_stok"] = stok
        except ValueError:
            daftar_error.append("Jumlah stok harus berupa angka bulat yang valid.")

    # c. Kondisi harus salah satu dari pilihan yang tersedia
    if data["kondisi"] and data["kondisi"] not in KONDISI_BARANG:
        daftar_error.append("Kondisi barang tidak valid.")

    # d. Format tanggal harus YYYY-MM-DD
    try:
        datetime.strptime(data["tanggal_pencatatan"], "%Y-%m-%d")
    except ValueError:
        daftar_error.append("Format tanggal pencatatan tidak valid.")

    return data, daftar_error


def validasi_form_transaksi(form):
    """Memvalidasi input formulir barang masuk/keluar.

    Mengembalikan tuple (barang_id, jumlah, tanggal, keterangan, daftar_error).
    """
    daftar_error = []

    barang_id = form.get("barang_id", type=int)
    jumlah = form.get("jumlah", type=int)
    tanggal = (form.get("tanggal") or "").strip()
    keterangan = (form.get("keterangan") or "").strip()

    # Jika tanggal kosong, otomatis memakai tanggal hari ini
    if not tanggal:
        tanggal = date.today().strftime("%Y-%m-%d")

    if barang_id is None:
        daftar_error.append("Silakan pilih barang terlebih dahulu.")

    if jumlah is None or jumlah <= 0:
        daftar_error.append("Jumlah barang harus berupa angka lebih besar dari 0.")

    try:
        datetime.strptime(tanggal, "%Y-%m-%d")
    except ValueError:
        daftar_error.append("Format tanggal transaksi tidak valid.")

    return barang_id, jumlah, tanggal, keterangan, daftar_error


# =====================================================================
# 5. ROUTE DASHBOARD
# =====================================================================
@app.route("/")
def dashboard():
    """Menampilkan ringkasan inventaris pada halaman utama (Dashboard)."""
    koneksi = get_db()

    total_jenis_barang = koneksi.execute("SELECT COUNT(*) FROM barang").fetchone()[0]
    total_unit_barang = koneksi.execute(
        "SELECT COALESCE(SUM(jumlah_stok), 0) FROM barang"
    ).fetchone()[0]

    # Ringkasan jumlah barang per kondisi (Baik / Rusak Ringan / Rusak Berat)
    ringkasan_kondisi = []
    for kondisi in KONDISI_BARANG:
        baris = koneksi.execute(
            "SELECT COUNT(*), COALESCE(SUM(jumlah_stok), 0) FROM barang WHERE kondisi = ?",
            (kondisi,),
        ).fetchone()
        persen = round(baris[0] * 100 / total_jenis_barang) if total_jenis_barang > 0 else 0
        ringkasan_kondisi.append(
            {"kondisi": kondisi, "jumlah_jenis": baris[0], "jumlah_unit": baris[1], "persen": persen}
        )

    total_barang_masuk = koneksi.execute(
        "SELECT COALESCE(SUM(jumlah), 0) FROM transaksi WHERE jenis = 'masuk'"
    ).fetchone()[0]
    total_barang_keluar = koneksi.execute(
        "SELECT COALESCE(SUM(jumlah), 0) FROM transaksi WHERE jenis = 'keluar'"
    ).fetchone()[0]

    barang_stok_rendah = koneksi.execute(
        """
        SELECT * FROM barang
        WHERE jumlah_stok <= ?
        ORDER BY jumlah_stok ASC, nama_barang ASC
        LIMIT 5
        """,
        (BATAS_STOK_RENDAH,),
    ).fetchall()

    barang_terbaru = koneksi.execute(
        "SELECT * FROM barang ORDER BY id DESC LIMIT 5"
    ).fetchall()

    koneksi.close()

    return render_template(
        "dashboard.html",
        total_jenis_barang=total_jenis_barang,
        total_unit_barang=total_unit_barang,
        ringkasan_kondisi=ringkasan_kondisi,
        total_barang_masuk=total_barang_masuk,
        total_barang_keluar=total_barang_keluar,
        barang_stok_rendah=barang_stok_rendah,
        barang_terbaru=barang_terbaru,
    )


# =====================================================================
# 6. ROUTE MANAJEMEN DATA BARANG (CRUD)
# =====================================================================
@app.route("/barang")
def data_barang():
    """Menampilkan tabel data barang dengan pencarian dan filter."""
    q = (request.args.get("q") or "").strip()
    kategori = (request.args.get("kategori") or "").strip()
    kondisi = (request.args.get("kondisi") or "").strip()

    sql = "SELECT * FROM barang WHERE 1=1"
    parameter = []

    # Pencarian berdasarkan nama atau kode barang
    if q:
        sql += " AND (nama_barang LIKE ? OR kode_barang LIKE ?)"
        parameter.extend(["%" + q + "%", "%" + q + "%"])
    # Filter berdasarkan kategori
    if kategori:
        sql += " AND kategori = ?"
        parameter.append(kategori)
    # Filter berdasarkan kondisi
    if kondisi:
        sql += " AND kondisi = ?"
        parameter.append(kondisi)

    sql += " ORDER BY id DESC"

    koneksi = get_db()
    daftar_barang = koneksi.execute(sql, parameter).fetchall()
    daftar_kategori = koneksi.execute(
        "SELECT DISTINCT kategori FROM barang ORDER BY kategori ASC"
    ).fetchall()
    koneksi.close()

    return render_template(
        "data_barang.html",
        daftar_barang=daftar_barang,
        daftar_kategori=daftar_kategori,
        q=q,
        kategori=kategori,
        kondisi=kondisi,
    )


@app.route("/barang/tambah", methods=["GET", "POST"])
def tambah_barang():
    """Menampilkan formulir (GET) dan memproses penambahan (POST) barang baru."""
    if request.method == "POST":
        data, daftar_error = validasi_form_barang(request.form)

        if not daftar_error:
            koneksi = get_db()
            sudah_ada = koneksi.execute(
                "SELECT id FROM barang WHERE kode_barang = ?", (data["kode_barang"],)
            ).fetchone()

            if sudah_ada:
                daftar_error.append(
                    f"Kode barang {data['kode_barang']} sudah digunakan, gunakan kode lain."
                )
                koneksi.close()
            else:
                koneksi.execute(
                    """
                    INSERT INTO barang
                        (kode_barang, nama_barang, kategori, lokasi,
                         jumlah_stok, kondisi, tanggal_pencatatan)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        data["kode_barang"],
                        data["nama_barang"],
                        data["kategori"],
                        data["lokasi"],
                        data["jumlah_stok"],
                        data["kondisi"],
                        data["tanggal_pencatatan"],
                    ),
                )
                koneksi.commit()
                koneksi.close()
                nama_baru = data["nama_barang"]
                flash(f'Barang "{nama_baru}" berhasil ditambahkan.', "success")
                return redirect(url_for("data_barang"))

        # Jika validasi gagal: tampilkan semua pesan error lalu buka formulir lagi
        for pesan_error in daftar_error:
            flash(pesan_error, "danger")
        return render_template("form_barang.html", mode="tambah", nilai=request.form)

    # GET: tampilkan formulir kosong dengan tanggal hari ini sebagai nilai awal
    nilai_awal = {"tanggal_pencatatan": date.today().strftime("%Y-%m-%d")}
    return render_template("form_barang.html", mode="tambah", nilai=nilai_awal)


@app.route("/barang/edit/<int:barang_id>", methods=["GET", "POST"])
def edit_barang(barang_id):
    """Menampilkan formulir (GET) dan memproses perubahan (POST) data barang."""
    barang = ambil_barang(barang_id)
    if barang is None:
        flash("Barang yang ingin diedit tidak ditemukan.", "danger")
        return redirect(url_for("data_barang"))

    if request.method == "POST":
        data, daftar_error = validasi_form_barang(request.form)

        if not daftar_error:
            koneksi = get_db()
            sudah_ada = koneksi.execute(
                "SELECT id FROM barang WHERE kode_barang = ? AND id != ?",
                (data["kode_barang"], barang_id),
            ).fetchone()

            if sudah_ada:
                daftar_error.append(
                    f"Kode barang {data['kode_barang']} sudah dipakai oleh barang lain."
                )
                koneksi.close()
            else:
                koneksi.execute(
                    """
                    UPDATE barang
                    SET kode_barang = ?, nama_barang = ?, kategori = ?, lokasi = ?,
                        jumlah_stok = ?, kondisi = ?, tanggal_pencatatan = ?
                    WHERE id = ?
                    """,
                    (
                        data["kode_barang"],
                        data["nama_barang"],
                        data["kategori"],
                        data["lokasi"],
                        data["jumlah_stok"],
                        data["kondisi"],
                        data["tanggal_pencatatan"],
                        barang_id,
                    ),
                )
                koneksi.commit()
                koneksi.close()
                nama_edit = data["nama_barang"]
                flash(f'Data barang "{nama_edit}" berhasil diperbarui.', "success")
                return redirect(url_for("data_barang"))

        for pesan_error in daftar_error:
            flash(pesan_error, "danger")
        return render_template(
            "form_barang.html", mode="edit", nilai=request.form, barang_id=barang_id
        )

    # GET: isi formulir dengan data barang yang sudah ada di database
    return render_template(
        "form_barang.html", mode="edit", nilai=barang, barang_id=barang_id
    )


@app.route("/barang/hapus/<int:barang_id>", methods=["POST"])
def hapus_barang(barang_id):
    """Menghapus data barang.

    Hanya menerima metode POST (penghapusan tidak boleh dilakukan
    melalui tautan GET demi keamanan data).
    """
    barang = ambil_barang(barang_id)
    if barang is None:
        flash("Barang yang ingin dihapus tidak ditemukan.", "danger")
        return redirect(url_for("data_barang"))

    koneksi = get_db()
    # Hapus juga riwayat transaksi barang tersebut agar data tetap konsisten
    koneksi.execute("DELETE FROM transaksi WHERE barang_id = ?", (barang_id,))
    koneksi.execute("DELETE FROM barang WHERE id = ?", (barang_id,))
    koneksi.commit()
    koneksi.close()

    nama_hapus = barang["nama_barang"]
    flash(f'Barang "{nama_hapus}" beserta riwayat transaksinya berhasil dihapus.', "success")
    return redirect(url_for("data_barang"))


# =====================================================================
# 7. ROUTE TRANSAKSI BARANG MASUK DAN BARANG KELUAR
# =====================================================================
@app.route("/barang-masuk", methods=["GET", "POST"])
def barang_masuk():
    """Mencatat transaksi barang masuk dan menambah stok secara otomatis."""
    koneksi = get_db()
    nilai = {}

    if request.method == "POST":
        barang_id, jumlah, tanggal, keterangan, daftar_error = validasi_form_transaksi(
            request.form
        )

        barang = None
        if not daftar_error:
            barang = koneksi.execute(
                "SELECT * FROM barang WHERE id = ?", (barang_id,)
            ).fetchone()
            if barang is None:
                daftar_error.append("Barang pilihan tidak ditemukan.")

        if not daftar_error:
            koneksi.execute(
                """
                INSERT INTO transaksi (barang_id, jenis, jumlah, tanggal, keterangan)
                VALUES (?, 'masuk', ?, ?, ?)
                """,
                (barang_id, jumlah, tanggal, keterangan),
            )
            koneksi.execute(
                "UPDATE barang SET jumlah_stok = jumlah_stok + ? WHERE id = ?",
                (jumlah, barang_id),
            )
            koneksi.commit()
            koneksi.close()
            nama_barang = barang["nama_barang"]
            flash(
                f'Transaksi masuk berhasil: stok "{nama_barang}" bertambah {jumlah} unit.',
                "success",
            )
            return redirect(url_for("barang_masuk"))

        for pesan_error in daftar_error:
            flash(pesan_error, "danger")
        nilai = request.form

    daftar_barang = koneksi.execute(
        "SELECT * FROM barang ORDER BY nama_barang ASC"
    ).fetchall()
    riwayat = koneksi.execute(
        """
        SELECT t.*, b.kode_barang, b.nama_barang
        FROM transaksi t
        JOIN barang b ON t.barang_id = b.id
        WHERE t.jenis = 'masuk'
        ORDER BY t.tanggal DESC, t.id DESC
        LIMIT 15
        """
    ).fetchall()
    koneksi.close()

    return render_template(
        "transaksi.html",
        mode="masuk",
        nilai=nilai,
        daftar_barang=daftar_barang,
        riwayat=riwayat,
    )


@app.route("/barang-keluar", methods=["GET", "POST"])
def barang_keluar():
    """Mencatat transaksi barang keluar dan mengurangi stok secara otomatis.

    Transaksi ditolak jika jumlah barang keluar melebihi stok tersedia.
    """
    koneksi = get_db()
    nilai = {}

    if request.method == "POST":
        barang_id, jumlah, tanggal, keterangan, daftar_error = validasi_form_transaksi(
            request.form
        )

        barang = None
        if not daftar_error:
            barang = koneksi.execute(
                "SELECT * FROM barang WHERE id = ?", (barang_id,)
            ).fetchone()
            if barang is None:
                daftar_error.append("Barang pilihan tidak ditemukan.")
            elif jumlah > barang["jumlah_stok"]:
                stok_tersedia = barang["jumlah_stok"]
                nama_barang = barang["nama_barang"]
                daftar_error.append(
                    f'Transaksi ditolak: jumlah keluar ({jumlah}) melebihi stok '
                    f'"{nama_barang}" yang tersedia ({stok_tersedia} unit).'
                )

        if not daftar_error:
            koneksi.execute(
                """
                INSERT INTO transaksi (barang_id, jenis, jumlah, tanggal, keterangan)
                VALUES (?, 'keluar', ?, ?, ?)
                """,
                (barang_id, jumlah, tanggal, keterangan),
            )
            koneksi.execute(
                "UPDATE barang SET jumlah_stok = jumlah_stok - ? WHERE id = ?",
                (jumlah, barang_id),
            )
            koneksi.commit()
            koneksi.close()
            nama_barang = barang["nama_barang"]
            flash(
                f'Transaksi keluar berhasil: stok "{nama_barang}" berkurang {jumlah} unit.',
                "success",
            )
            return redirect(url_for("barang_keluar"))

        for pesan_error in daftar_error:
            flash(pesan_error, "danger")
        nilai = request.form

    daftar_barang = koneksi.execute(
        "SELECT * FROM barang ORDER BY nama_barang ASC"
    ).fetchall()
    riwayat = koneksi.execute(
        """
        SELECT t.*, b.kode_barang, b.nama_barang
        FROM transaksi t
        JOIN barang b ON t.barang_id = b.id
        WHERE t.jenis = 'keluar'
        ORDER BY t.tanggal DESC, t.id DESC
        LIMIT 15
        """
    ).fetchall()
    koneksi.close()

    return render_template(
        "transaksi.html",
        mode="keluar",
        nilai=nilai,
        daftar_barang=daftar_barang,
        riwayat=riwayat,
    )


# =====================================================================
# 8. ROUTE LAPORAN INVENTARIS
# =====================================================================
@app.route("/laporan")
def laporan():
    """Menampilkan laporan inventaris: ringkasan kondisi, daftar barang,
    dan riwayat transaksi, lengkap dengan filter dan tombol cetak."""
    kategori = (request.args.get("kategori") or "").strip()
    kondisi = (request.args.get("kondisi") or "").strip()
    jenis_transaksi = (request.args.get("jenis") or "").strip()
    tanggal_dari = (request.args.get("tanggal_dari") or "").strip()
    tanggal_sampai = (request.args.get("tanggal_sampai") or "").strip()

    koneksi = get_db()

    # --- Query daftar barang (dengan filter kategori dan kondisi) ---
    sql_barang = "SELECT * FROM barang WHERE 1=1"
    parameter_barang = []
    if kategori:
        sql_barang += " AND kategori = ?"
        parameter_barang.append(kategori)
    if kondisi:
        sql_barang += " AND kondisi = ?"
        parameter_barang.append(kondisi)
    sql_barang += " ORDER BY nama_barang ASC"
    daftar_barang = koneksi.execute(sql_barang, parameter_barang).fetchall()

    # --- Ringkasan kondisi dihitung dari daftar barang yang sudah terfilter ---
    total_jenis_laporan = len(daftar_barang)
    total_unit_laporan = sum(b["jumlah_stok"] for b in daftar_barang)
    ringkasan_kondisi = []
    for kondisi_item in KONDISI_BARANG:
        jumlah_jenis = sum(1 for b in daftar_barang if b["kondisi"] == kondisi_item)
        jumlah_unit = sum(b["jumlah_stok"] for b in daftar_barang if b["kondisi"] == kondisi_item)
        persen = round(jumlah_jenis * 100 / total_jenis_laporan) if total_jenis_laporan > 0 else 0
        ringkasan_kondisi.append(
            {
                "kondisi": kondisi_item,
                "jumlah_jenis": jumlah_jenis,
                "jumlah_unit": jumlah_unit,
                "persen": persen,
            }
        )

    # --- Query riwayat transaksi (dengan filter jenis dan rentang tanggal) ---
    sql_transaksi = """
        SELECT t.*, b.kode_barang, b.nama_barang
        FROM transaksi t
        JOIN barang b ON t.barang_id = b.id
        WHERE 1=1
    """
    parameter_transaksi = []
    if jenis_transaksi in ("masuk", "keluar"):
        sql_transaksi += " AND t.jenis = ?"
        parameter_transaksi.append(jenis_transaksi)
    if tanggal_dari:
        sql_transaksi += " AND t.tanggal >= ?"
        parameter_transaksi.append(tanggal_dari)
    if tanggal_sampai:
        sql_transaksi += " AND t.tanggal <= ?"
        parameter_transaksi.append(tanggal_sampai)
    sql_transaksi += " ORDER BY t.tanggal DESC, t.id DESC LIMIT 100"
    riwayat_transaksi = koneksi.execute(sql_transaksi, parameter_transaksi).fetchall()

    daftar_kategori = koneksi.execute(
        "SELECT DISTINCT kategori FROM barang ORDER BY kategori ASC"
    ).fetchall()
    koneksi.close()

    return render_template(
        "laporan.html",
        daftar_barang=daftar_barang,
        ringkasan_kondisi=ringkasan_kondisi,
        total_jenis_laporan=total_jenis_laporan,
        total_unit_laporan=total_unit_laporan,
        riwayat_transaksi=riwayat_transaksi,
        daftar_kategori=daftar_kategori,
        kategori=kategori,
        kondisi=kondisi,
        jenis_transaksi=jenis_transaksi,
        tanggal_dari=tanggal_dari,
        tanggal_sampai=tanggal_sampai,
    )


# =====================================================================
# 9. ROUTE PROFIL DAN BANTUAN
# =====================================================================
@app.route("/profil")
def profil():
    """Menampilkan informasi tentang sistem (menggunakan halaman_info.html)."""
    return render_template("halaman_info.html", halaman="profil")


@app.route("/bantuan")
def bantuan():
    """Menampilkan panduan penggunaan sistem (menggunakan halaman_info.html)."""
    return render_template("halaman_info.html", halaman="bantuan")


# =====================================================================
# 10. MENJALANKAN APLIKASI
# =====================================================================
if __name__ == "__main__":
    init_db()  # Buat database, tabel, dan data contoh otomatis saat pertama dijalankan
    app.run(host="127.0.0.1", port=5000, debug=True)
