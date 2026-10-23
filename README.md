# Sistem Informasi Manajemen Inventaris Barang Berbasis Web

Proyek **Evaluasi Tengah Semester (ETS)** — aplikasi web untuk membantu petugas
mengelola data inventaris barang: mencatat master data barang, memantau jumlah
dan kondisi barang, mencatat transaksi barang masuk dan keluar, serta menyajikan
laporan inventaris yang siap dicetak.

## Tujuan Sistem

1. Mempermudah petugas mencatat dan mengelola data inventaris dalam satu sistem terpusat.
2. Memantau jumlah stok dan kondisi barang (Baik, Rusak Ringan, Rusak Berat) secara real-time.
3. Menghindari kesalahan pencatatan stok melalui validasi input dan perubahan stok otomatis.
4. Menyediakan laporan inventaris lengkap dengan ringkasan kondisi dan riwayat transaksi.
5. Membantu pengambilan keputusan, misalnya melalui informasi barang dengan stok rendah.

## Teknologi yang Digunakan

| Bagian            | Teknologi                                    |
| ----------------- | -------------------------------------------- |
| Backend           | Python 3 dengan framework Flask              |
| Template engine   | Jinja2 (bawaan Flask)                        |
| Frontend          | HTML5, CSS3, JavaScript (tanpa React/Vue/Node) |
| Framework antarmuka | Dashboard berbasis **Bootstrap 5** (aset lokal di folder `static`) |
| Ikon              | Bootstrap Icons (aset lokal)                 |
| Database          | SQLite (dibuat otomatis, tanpa instalasi)    |
| Editor            | Visual Studio Code                           |

## Fitur Utama

- **Dashboard**: ringkasan jumlah jenis/unit barang, ringkasan kondisi barang, total barang masuk/keluar, daftar barang stok rendah, dan tabel barang terbaru.
- **Manajemen Data Barang (CRUD)**: tambah, edit, hapus (dengan modal konfirmasi), cari berdasarkan nama/kode, serta filter kategori dan kondisi.
- **Transaksi**: barang masuk (stok bertambah otomatis) dan barang keluar (stok berkurang otomatis, transaksi ditolak bila stok tidak cukup), lengkap dengan riwayat.
- **Laporan**: ringkasan kondisi barang, daftar seluruh barang, riwayat masuk/keluar, filter (kategori, kondisi, jenis transaksi, rentang tanggal), dan tombol cetak via fitur cetak browser.
- **Profil dan Bantuan**: informasi sistem serta panduan langkah demi langkah.
- **Notifikasi flash message** untuk keberhasilan/kegagalan setiap aksi, validasi input di sisi server maupun klien, dan tampilan responsif (desktop, tablet, ponsel).

## Struktur Folder

```
inventaris-barang/
├── app.py                  # File utama: routing, CRUD, transaksi, validasi
├── requirements.txt        # Daftar dependensi Python
├── README.md               # Dokumentasi proyek
├── .gitignore
├── inventaris.db           # Database SQLite (dibuat OTOMATIS saat aplikasi dijalankan)
├── templates/
│   ├── base.html           # Template utama: sidebar, navbar, footer, flash message
│   ├── dashboard.html      # Halaman Dashboard
│   ├── data_barang.html    # Tabel data barang + pencarian/filter + modal hapus
│   ├── form_barang.html    # Formulir bersama untuk Tambah dan Edit barang
│   ├── transaksi.html      # Formulir + riwayat Barang Masuk/Keluar (template bersama)
│   ├── laporan.html        # Laporan inventaris + ringkasan kondisi + riwayat
│   └── halaman_info.html   # Halaman Profil dan Bantuan (konten menyesuaikan menu)
└── static/
    ├── css/
    │   └── style.css                # CSS kustom proyek (satu-satunya file di sini)
    ├── js/
    │   └── script.js                # JavaScript buatan sendiri (satu-satunya file di sini)
    ├── vendor/                      # Aset pihak ketiga (dipisahkan agar folder proyek rapi)
    │   ├── bootstrap/
    │   │   ├── css/bootstrap.min.css        # Bootstrap 5 (lokal, dapat dipakai offline)
    │   │   └── js/bootstrap.bundle.min.js   # JavaScript Bootstrap 5 (lokal)
    │   └── bootstrap-icons/
    │       ├── bootstrap-icons.min.css      # Bootstrap Icons (lokal)
    │       └── fonts/                       # Berkas ikon woff/woff2
    └── img/                         # Folder gambar (disediakan; ikon memakai Bootstrap Icons)
```

Catatan struktur:

- Semua halaman mewarisi `base.html` melalui **Template Inheritance** (`{% extends "base.html" %}`, `{% block title %}`, `{% block content %}`), sehingga sidebar dan navbar hanya ditulis satu kali.
- `transaksi.html` adalah satu template bersama untuk dua halaman transaksi (`/barang-masuk` dan `/barang-keluar`) dengan konten menyesuaikan mode — sesuai prinsip tidak membuat file HTML terpisah untuk konten yang bisa memakai template yang sama.
- Aset pihak ketiga dikelompokkan pada `static/vendor/` sehingga `static/css/` dan `static/js/` hanya berisi file buatan sendiri; semua aset diunduh lokal agar aplikasi tetap tampil benar **tanpa koneksi internet**.
- `inventaris.db` akan terbentuk sendiri berisi tabel `barang`, tabel `transaksi`, dan data contoh saat aplikasi pertama kali dijalankan. Hapus file tersebut jika ingin mengulang dari data awal.

## Instalasi dan Menjalankan Aplikasi

Panduan berikut ditujukan untuk Windows dan Visual Studio Code.

Pastikan **Python 3.10+** sudah terpasang (cek dengan `python --version`).

1. **Buka folder proyek** di Visual Studio Code (File → Open Folder → pilih folder `inventaris-barang`), lalu buka terminal VS Code (Terminal → New Terminal).

2. **Buat virtual environment** (hanya sekali di awal):

   ```
   python -m venv venv
   ```

3. **Aktifkan virtual environment** (Windows):

   ```
   venv\Scripts\activate
   ```

   Jika muncul peringatan policy PowerShell, jalankan sekali:
   `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` lalu ulangi aktivasi.

4. **Instal dependensi** (venv harus dalam keadaan aktif, ditandai `(venv)` di terminal):

   ```
   pip install -r requirements.txt
   ```

5. **Jalankan aplikasi**:

   ```
   python app.py
   ```

6. **Buka website** di browser pada alamat yang ditampilkan Flask:

   ```
   http://127.0.0.1:5000
   ```

7. Jika port 5000 sedang dipakai aplikasi lain, ubah baris terakhir `app.py` menjadi `app.run(host="127.0.0.1", port=5001, debug=True)` lalu akses `http://127.0.0.1:5001`.

## Cara Menggunakan Fitur Utama

1. **Dashboard** — halaman pembuka berisi ringkasan inventaris. Perhatikan panel "Barang Stok Rendah" untuk barang yang perlu segera di-restock.
2. **Menambah barang** — menu *Manajemen Data → Tambah Barang*, isi semua kolom bertanda `*`, klik **Simpan**. Kode barang tidak boleh kembar.
3. **Mengedit/menghapus barang** — dari halaman *Data Barang*, gunakan tombol pensil (edit) atau tombol tempat sampah (hapus, dengan konfirmasi modal).
4. **Mencari/memfilter** — di halaman *Data Barang*, isi kolom pencarian dan/atau pilih kategori/kondisi lalu klik **Terapkan**.
5. **Barang masuk/keluar** — menu *Transaksi → Barang Masuk / Barang Keluar*, pilih barang, isi jumlah, tanggal, keterangan, lalu simpan. Stok berubah otomatis; transaksi keluar ditolak bila melebihi stok.
6. **Laporan** — menu *Laporan → Laporan Inventaris*, gunakan filter bila perlu, lalu klik **Cetak Laporan** untuk mencetak atau menyimpan PDF melalui dialog cetak browser.
7. **Profil & Bantuan** — menu *Profil* berisi informasi sistem; menu *Bantuan* berisi panduan penggunaan lengkap.

## Struktur Database (SQLite)

Tabel **barang**: `id`, `kode_barang` (unik), `nama_barang`, `kategori`, `lokasi`, `jumlah_stok` (≥ 0), `kondisi` (Baik/Rusak Ringan/Rusak Berat), `tanggal_pencatatan`.

Tabel **transaksi**: `id`, `barang_id` (merujuk ke `barang.id`), `jenis` (masuk/keluar), `jumlah` (> 0), `tanggal`, `keterangan`.

Seluruh query memakai **parameter binding** (`?`) sehingga aman dari SQL Injection, dan input divalidasi di sisi server (kolom wajib, stok tidak negatif, jumlah transaksi > 0, stok cukup untuk barang keluar).

## Checklist Pengujian

Gunakan checklist berikut untuk memverifikasi aplikasi sebelum dikumpulkan.

### A. Persiapan

- [ ] Virtual environment dibuat dan diaktifkan tanpa error
- [ ] `pip install -r requirements.txt` selesai tanpa error
- [ ] `python app.py` berjalan dan alamat `http://127.0.0.1:5000` muncul di terminal
- [ ] File `inventaris.db` dibuat otomatis di folder proyek
- [ ] Data contoh tampil saat pertama kali dijalankan

### B. Navigasi dan Tampilan

- [ ] Semua menu sidebar dapat dibuka tanpa error: Dashboard, Data Barang, Tambah Barang, Barang Masuk, Barang Keluar, Laporan Inventaris, Ringkasan Kondisi, Profil, Bantuan
- [ ] Dropdown/submenu Manajemen Data, Transaksi, dan Laporan dapat dibuka dan ditutup
- [ ] Menu yang sedang dibuka ditandai warna aktif di sidebar
- [ ] Tombol hamburger menyembunyikan/menampilkan sidebar (desktop)
- [ ] Pada lebar layar ponsel sidebar menjadi off-canvas dengan latar gelap dan dapat ditutup lewat area gelap
- [ ] Tampilan rapi pada desktop, laptop, tablet, dan ponsel
- [ ] Tidak ada error di console browser (F12 → Console)
- [ ] Tidak ada broken link dan seluruh aset berhasil dimuat (F12 → Network, status 200)

### C. Manajemen Data Barang

- [ ] Menambah barang lengkap berhasil dan muncul notifikasi hijau
- [ ] Menambah barang dengan kolom kosong ditolak (notifikasi merah + pesan validasi)
- [ ] Menambah barang dengan jumlah stok negatif ditolak
- [ ] Menambah barang dengan kode yang sudah ada ditolak
- [ ] Edit data barang tersimpan dan muncul notifikasi hijau
- [ ] Menghapus barang selalu menampilkan modal konfirmasi terlebih dahulu
- [ ] Pencarian berdasarkan nama dan kode barang berfungsi
- [ ] Filter kategori dan filter kondisi berfungsi (sendiri-sendiri dan digabung)
- [ ] Tombol reset (X) mengosongkan pencarian dan filter

### D. Transaksi Barang Masuk/Keluar

- [ ] Barang masuk menambah stok pada halaman Data Barang sesuai jumlah
- [ ] Barang keluar mengurangi stok sesuai jumlah
- [ ] Barang keluar yang melebihi stok ditolak dengan notifikasi merah dan stok tidak berubah
- [ ] Informasi stok tampil saat memilih barang pada formulir transaksi
- [ ] Riwayat transaksi tampil di halaman transaksi dan di halaman Laporan

### E. Laporan

- [ ] Ringkasan kondisi barang sesuai dengan data yang ada
- [ ] Filter kategori dan kondisi menyaring tabel daftar barang
- [ ] Filter jenis transaksi dan rentang tanggal menyaring riwayat transaksi
- [ ] Tombol **Cetak Laporan** membuka dialog cetak browser
- [ ] Pratinjau cetak hanya berisi laporan (sidebar, navbar, dan tombol disembunyikan)

### F. Konsistensi Data

- [ ] Data tetap tersimpan setelah aplikasi dimatikan (Ctrl+C) dan dijalankan ulang
- [ ] Menghapus barang juga menghilangkan riwayat transaksinya dari laporan

### G. Keamanan Dasar

- [ ] Mengakses tautan hapus dengan metode GET langsung tidak menghapus data (route hanya menerima POST)
- [ ] Memasukkan teks pada kolom angka ditolak dengan pesan yang jelas
#