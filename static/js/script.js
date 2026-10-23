/* =====================================================================
   script.js - Sistem Informasi Manajemen Inventaris Barang
   Berisi seluruh interaktivitas halaman:
   1. Toggle sidebar (responsif)
   2. Penutupan otomatis notifikasi (flash message)
   3. Modal konfirmasi hapus barang
   4. Validasi formulir sisi klien (Bootstrap)
   5. Tombol cetak laporan
   6. Informasi stok pada formulir transaksi
   Semua kode berjalan setelah DOM siap agar tidak error di console.
   ===================================================================== */

document.addEventListener("DOMContentLoaded", function () {
    var body = document.body;

    /* ---------- 1. TOGGLE SIDEBAR ---------- */
    var tombolSidebar = document.getElementById("tombol-sidebar");
    var backdrop = document.getElementById("sidebar-backdrop");

    if (tombolSidebar) {
        tombolSidebar.addEventListener("click", function () {
            if (window.innerWidth < 992) {
                // Tampilan ponsel/tablet: sidebar muncul di atas konten
                body.classList.toggle("sidebar-open");
            } else {
                // Tampilan desktop: sidebar disembunyikan ke kiri
                body.classList.toggle("sidebar-collapsed");
            }
        });
    }

    if (backdrop) {
        backdrop.addEventListener("click", function () {
            body.classList.remove("sidebar-open");
        });
    }

    window.addEventListener("resize", function () {
        if (window.innerWidth >= 992) {
            body.classList.remove("sidebar-open");
        } else {
            body.classList.remove("sidebar-collapsed");
        }
    });

    /* ---------- 2. NOTIFIKASI HILANG OTOMATIS ---------- */
    var daftarAlert = document.querySelectorAll(".alert-dismissible");
    daftarAlert.forEach(function (elemenAlert) {
        setTimeout(function () {
            // Gunakan komponen Alert milik Bootstrap agar animasinya halus
            if (window.bootstrap && window.bootstrap.Alert) {
                var objekAlert = window.bootstrap.Alert.getOrCreateInstance(elemenAlert);
                objekAlert.close();
            }
        }, 5000);
    });

    /* ---------- 3. MODAL KONFIRMASI HAPUS ---------- */
    var modalHapus = document.getElementById("modal-hapus");
    if (modalHapus) {
        modalHapus.addEventListener("show.bs.modal", function (event) {
            var tombol = event.relatedTarget;
            if (!tombol) {
                return;
            }
            var namaBarang = tombol.getAttribute("data-nama") || "";
            var urlHapus = tombol.getAttribute("data-url") || "";
            var teksNama = document.getElementById("nama-barang-hapus");
            var formHapus = document.getElementById("form-hapus");
            if (teksNama) {
                teksNama.textContent = namaBarang;
            }
            if (formHapus) {
                formHapus.setAttribute("action", urlHapus);
            }
        });
    }

    /* ---------- 4. VALIDASI FORMULIR (SISI KLIEN) ---------- */
    // Formulir diberi class "form-validasi" dan atribut novalidate;
    // pesan error tampil sesuai gaya Bootstrap, validasi utama tetap di server.
    var daftarForm = document.querySelectorAll(".form-validasi");
    daftarForm.forEach(function (form) {
        form.addEventListener("submit", function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add("was-validated");
        });
    });

    /* ---------- 5. TOMBOL CETAK LAPORAN ---------- */
    var tombolCetak = document.getElementById("tombol-cetak");
    if (tombolCetak) {
        tombolCetak.addEventListener("click", function () {
            window.print();
        });
    }

    /* ---------- 6. INFO STOK PADA FORMULIR TRANSAKSI ---------- */
    var pilihBarang = document.getElementById("pilih-barang");
    var inputJumlah = document.getElementById("input-jumlah");
    var infoStok = document.getElementById("info-stok");
    var modeKeluar = body.getAttribute("data-halaman") === "barang_keluar";

    function perbaruiInfoStok() {
        if (!pilihBarang || !infoStok) {
            return;
        }
        var opsi = pilihBarang.options[pilihBarang.selectedIndex];
        if (!opsi || !opsi.value) {
            infoStok.textContent = "";
            if (inputJumlah) {
                inputJumlah.removeAttribute("max");
            }
            return;
        }
        var stok = parseInt(opsi.getAttribute("data-stok"), 10) || 0;
        if (modeKeluar && inputJumlah) {
            // Batasi jumlah keluar agar tidak melebihi stok (pengecekan utama di server)
            inputJumlah.setAttribute("max", String(stok));
            infoStok.textContent = "Stok tersedia: " + stok + " unit. Transaksi ditolak bila jumlah melebihi stok.";
            infoStok.classList.add("text-danger");
            infoStok.classList.remove("text-secondary");
        } else {
            if (inputJumlah) {
                inputJumlah.removeAttribute("max");
            }
            infoStok.textContent = "Stok saat ini: " + stok + " unit.";
            infoStok.classList.remove("text-danger");
            infoStok.classList.add("text-secondary");
        }
    }

    if (pilihBarang) {
        pilihBarang.addEventListener("change", perbaruiInfoStok);
        perbaruiInfoStok();
    }
});
