# Kocak-SQL

Kocak-SQL adalah sebuah aplikasi pengelola database sederhana berbasis Python dengan antarmuka WebUI yang premium dan mudah digunakan. Aplikasi ini dibangun dengan arsitektur **Modular Monolith** menggunakan Flask, yang memisahkan fitur-fitur menjadi modul yang terorganisir.

Kocak-SQL hadir dengan bahasa kueri (*query language*) yang disederhanakan, memungkinkan pengguna untuk mengelola database tanpa perlu mengetik SQL panjang.

## Fitur Utama

1. **Dashboard Server Status**: Memantau status server secara real-time termasuk penggunaan CPU, RAM, dan informasi sistem operasi.
2. **Database Manager Premium**: 
   - Antarmuka *dark mode* kekinian dengan *glassmorphism* dan animasi halus.
   - Console eksekusi khusus dengan bahasa perintah bahasa Indonesia (*Kocak-SQL DSL*).
   - Penampil tabel secara instan.

## Bahasa Perintah Kocak-SQL

Kocak-SQL menerjemahkan perintah sederhana bahasa Indonesia menjadi perintah SQL murni secara otomatis. Jika perintah tidak dikenali, ia akan secara otomatis mencoba menjalankan perintah tersebut sebagai kueri SQL biasa (fallback).
*Tip: Anda juga dapat mengetikkan beberapa perintah sekaligus dipisahkan dengan Enter (baris baru)!*

Berikut daftar perintah yang disederhanakan:

### 1. Membuat Tabel
Perintah sederhana untuk membuat tabel beserta kolomnya. Jika ada kolom bernama `id`, ia otomatis akan menjadi `INTEGER PRIMARY KEY AUTOINCREMENT`. Jika ada nama seperti `umur`, `stok`, `qty`, `harga`, akan diset `INTEGER`, selebihnya `TEXT`.

**Sintaks:** `buat_tabel: <nama_tabel> [<kolom1>, <kolom2>, ...]`
**Contoh:** 
```text
buat_tabel: users [id, nama, umur]
```
*(Menjadi: CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, nama TEXT, umur INTEGER);)*

### 2. Menambahkan Data
Memasukkan baris baru ke dalam tabel yang dipilih. Gunakan tanda kutip `''` untuk data teks.

**Sintaks:** `tambah_data: <nama_tabel> [<kolom1>=<nilai1>, <kolom2>=<nilai2>]`
**Contoh:** 
```text
tambah_data: users [nama='Budi Raharjo', umur=25]
```

### 3. Mengubah Data
Memperbarui data yang ada berdasarkan kondisi yang diberikan di dalam kurung siku pertama `[]`.

**Sintaks:** `ubah_data: <nama_tabel> [<kondisi_kolom>=<nilai>] [<kolom_diubah>=<nilai_baru>]`
**Contoh:** 
```text
ubah_data: users [id=1] [nama='Andi Perkasa', umur=26]
```

### 4. Menghapus Data
Menghapus baris dari tabel berdasarkan suatu kondisi tertentu.

**Sintaks:** `hapus_data: <nama_tabel> [<kondisi>]`
**Contoh:** 
```text
hapus_data: users [id=1]
```

### 5. Melihat Data
Ini adalah cara pintas untuk perintah `SELECT * FROM ...`.

**Sintaks:** `lihat_data: <nama_tabel>`
**Contoh:** 
```text
lihat_data: users
```

### 6. Menghapus Tabel
Menghapus (Drop) sebuah tabel beserta semua isinya secara permanen.

**Sintaks:** `hapus_tabel: <nama_tabel>`
**Contoh:** 
```text
hapus_tabel: users
```

### 7. DCL (Data Control Language) - Simulasi Manajemen Akses
Karena SQLite tidak memiliki sistem kontrol pengguna mandiri (`GRANT`/`REVOKE`), Kocak-SQL menyimulasikan DCL dengan memanipulasi tabel bawaan `users`.

**Memberi Akses (Role)**
**Sintaks:** `beri_akses: <username> [<role_baru>]`
**Contoh:** 
```text
beri_akses: admin [administrator_utama]
```

**Mencabut Akses (Kembali ke pengguna biasa)**
**Sintaks:** `cabut_akses: <username>`
**Contoh:** 
```text
cabut_akses: admin
```

### 8. TCL (Transaction Control Language)
Digunakan untuk mengeksekusi sekumpulan perintah secara aman (terutama jika Anda mengeksekusi beberapa baris perintah sekaligus di Console).

- **Memulai Transaksi:** `mulai_transaksi` (Membuka sesi transaksi sementara)
- **Menyimpan Transaksi:** `simpan_transaksi` (Menyimpan seluruh perubahan secara permanen)
- **Membatalkan Transaksi:** `batal_transaksi` (Membatalkan semua perintah sejak `mulai_transaksi`)

**Contoh Penggunaan Batch dengan TCL:**
```text
mulai_transaksi
tambah_data: users [nama='Ahmad', umur=24]
tambah_data: users [nama='Zaki', umur=28]
simpan_transaksi
```

## Arsitektur (Modular Monolith)

Aplikasi ini menggunakan struktur Modular Monolith:

```text
Kocak-SQL/
│
├── app/
│   ├── __init__.py          # Flask App Factory
│   ├── database.py          # Koneksi ke SQLite
│   ├── modules/
│   │   ├── db_manager.py    # Pengelola database & parser sintaks Kocak-SQL
│   │   └── server_status.py # Logika monitoring server
│   ├── static/
│   │   └── style.css        # Desain antarmuka (Dark mode premium CSS)
│   └── templates/
│       ├── base.html        
│       ├── dashboard.html   
│       └── db_view.html     
│
├── run.py                   # Entry point aplikasi
└── Readme.md                # Dokumentasi aplikasi
```

## Cara Menjalankan

1. Pastikan Python sudah terinstall di sistem Anda.
2. Install library yang dibutuhkan:
   ```bash
   pip install Flask psutil
   ```
3. Jalankan aplikasi:
   ```bash
   python run.py
   ```
4. Buka browser dan akses alamat: `http://127.0.0.1:5000`
