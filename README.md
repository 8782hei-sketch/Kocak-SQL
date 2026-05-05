<div align="center">
  <img src="https://img.icons8.com/color/96/000000/database.png" alt="Kocak-SQL Logo">
  <h1>Kocak-SQL</h1>
  <p><b>Sistem Manajemen Database Modern Berbasis DSL dengan Arsitektur Client-Server</b></p>

  [![Python](https://img.shields.io/badge/Python-3.x-blue.svg?style=flat-square&logo=python)](https://www.python.org/)
  [![Flask](https://img.shields.io/badge/Framework-Flask-black.svg?style=flat-square&logo=flask)](https://flask.palletsprojects.com/)
  [![SQLite](https://img.shields.io/badge/Database-SQLite-003B57.svg?style=flat-square&logo=sqlite)](https://www.sqlite.org/)
  [![License](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)]()
</div>

---

## 📖 Pengantar

**Kocak-SQL** adalah aplikasi pengelola database (*Database Management System / DBMS*) ringan yang dirancang untuk mempermudah manajemen data. Dibangun dengan **Python, Flask, dan SQLite**, aplikasi ini menawarkan antarmuka WebUI bernuansa premium (*glassmorphism dark-mode*) serta fitur unggulan berupa bahasa kueri (*Domain-Specific Language*) tersendiri yang sangat mudah dipahami.

Selain antarmuka web, Kocak-SQL juga mengimplementasikan arsitektur **Client-Server** yang memungkinkan aplikasi eksternal (via REST API) untuk terhubung dan mengelola data secara dinamis.

---

## 🌟 Fitur Unggulan

- **🚀 Dashboard Real-time:** Memonitor kesehatan server (CPU & RAM) secara instan.
- **💎 Premium WebUI:** Antarmuka modern dengan *glassmorphism*, tipografi *Inter/Outfit*, dan animasi yang memanjakan mata.
- **🗣️ Kocak-SQL DSL:** Menulis *query* SQL kompleks dengan bahasa Indonesia sederhana tanpa perlu pusing memikirkan sintaks SQL asli.
- **🔄 Batch & TCL Support:** Eksekusi puluhan baris kueri sekaligus secara aman dengan dukungan Manajemen Transaksi.
- **🔌 REST API Endpoint:** Hubungkan bahasa pemrograman apapun dengan database ini melalui protokol HTTP JSON.

---

## 🛠️ Arsitektur Sistem

Kocak-SQL dibangun menggunakan pola **Modular Monolith**.

```text
Kocak-SQL/
├── app/
│   ├── __init__.py          # Flask App Factory & Blueprint registration
│   ├── database.py          # Inisialisasi SQLite & Connection Pooling
│   ├── modules/
│   │   ├── api.py           # Endpoint REST API (/api/query)
│   │   ├── db_manager.py    # Interpreter DSL & Pengelola Tabel
│   │   └── server_status.py # Integrasi psutil untuk Server Monitoring
│   ├── static/
│   │   └── style.css        # Desain visual premium (UI/UX)
│   └── templates/           # View layer (HTML Jinja2)
├── run.py                   # Server Entry Point
└── contoh_client.py         # Contoh penerapan integrasi API
```

---

## 💻 Panduan Penggunaan Sintaks (Kocak-SQL DSL)

Interpreter Kocak-SQL akan menerjemahkan perintah Anda secara otomatis ke SQLite. Jika perintah tidak valid di DSL, sistem akan mencoba menjalankannya sebagai SQL asli.

### 1. Data Definition & Manipulation
| Operasi | Sintaks Kocak-SQL | Contoh Eksekusi |
| :--- | :--- | :--- |
| **Buat Tabel** | `buat_tabel: <nama> [<kolom>]` | `buat_tabel: users [id, nama, umur]` |
| **Hapus Tabel** | `hapus_tabel: <nama>` | `hapus_tabel: users` |
| **Lihat Data** | `lihat_data: <nama>` | `lihat_data: users` |
| **Tambah Data** | `tambah_data: <nama> [<k>=<v>]` | `tambah_data: users [nama='Budi', umur=20]` |
| **Ubah Data** | `ubah_data: <nama> [<kondisi>] [<k>=<v>]` | `ubah_data: users [id=1] [umur=21]` |
| **Hapus Data** | `hapus_data: <nama> [<kondisi>]` | `hapus_data: users [id=1]` |

### 2. Transaction Control Language (TCL) & DCL
- **Mulai Transaksi:** `mulai_transaksi` (BEGIN)
- **Simpan Transaksi:** `simpan_transaksi` (COMMIT)
- **Batalkan Transaksi:** `batal_transaksi` (ROLLBACK)
- **Beri Akses (Simulasi):** `beri_akses: <user> [<role>]`
- **Cabut Akses (Simulasi):** `cabut_akses: <user>`

---

## 🔗 Integrasi API (Client-Server)

Kocak-SQL menyediakan endpoint REST API profesional:

- **URL:** `POST /api/query`
- **Headers:** `Content-Type: application/json`
- **Payload:**
  ```json
  {
    "query": "lihat_data: users"
  }
  ```
- **Response:** Terstruktur rapi dengan kode status HTTP yang sesuai (Bisa dilihat detailnya dengan menjalankan file uji coba `contoh_client.py`).

---

## ⚙️ Cara Instalasi & Menjalankan

**Prasyarat:** Python 3.8+

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Jalankan Server Database:**
   ```bash
   python run.py
   ```
3. Buka Dashboard melalui Browser di: `http://127.0.0.1:5000`
4. *(Opsional)* Uji koneksi API dengan membuka terminal baru dan jalankan:
   ```bash
   python contoh_client.py
   ```

---
<div align="center">
  <i>Dibuat dengan ❤️ untuk kemudahan pengelolaan database.</i>
</div>
