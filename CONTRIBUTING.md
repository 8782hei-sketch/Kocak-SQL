# Kontribusi ke Kocak-SQL

Terima kasih telah tertarik untuk berkontribusi pada Kocak-SQL! Panduan ini akan membantu Anda memahami bagaimana cara berkontribusi dengan baik.

## 📋 Daftar Isi

- [Code of Conduct](#code-of-conduct)
- [Melaporkan Bug](#melaporkan-bug)
- [Mengusulkan Fitur Baru](#mengusulkan-fitur-baru)
- [Pull Request Process](#pull-request-process)
- [Standar Kode](#standar-kode)
- [Struktur File](#struktur-file)

---

## Code of Conduct

Proyek ini menerapkan Code of Conduct yang ketat. Harap hormati sesama kontributor dan pengguna dengan:
- Berkomunikasi dengan sopan dan profesional
- Menghormati perbedaan pendapat
- Fokus pada isu, bukan pada individu
- Tidak ada toleransi untuk harassment atau diskriminasi

---

## Melaporkan Bug

Jika Anda menemukan bug, harap buat **Issue** baru dengan format berikut:

### Template:
```
**Deskripsi Bug:**
[Jelaskan bug dengan singkat]

**Langkah Reproduksi:**
1. [Langkah pertama]
2. [Langkah kedua]
3. [Dst...]

**Hasil yang Diharapkan:**
[Apa yang seharusnya terjadi]

**Hasil Aktual:**
[Apa yang benar-benar terjadi]

**Screenshots/Logs:**
[Lampirkan screenshot atau error log jika ada]

**Environment:**
- OS: [Windows/Linux/Mac]
- Python Version: [3.8/3.9/3.10/3.11]
- Browser: [Chrome/Firefox/Safari]
```

---

## Mengusulkan Fitur Baru

Sebelum mulai membuat fitur, buat **Issue** terlebih dahulu dengan label `enhancement`:

### Template:
```
**Deskripsi Fitur:**
[Jelaskan fitur yang ingin ditambahkan]

**Mengapa Fitur Ini Diperlukan:**
[Jelaskan use case dan benefit]

**Implementasi yang Diusulkan:**
[Jelaskan bagaimana implementasi yang mungkin]

**Alternatif:**
[Apakah ada alternatif lain yang bisa dipertimbangkan?]
```

Tunggu feedback maintainer sebelum mulai mengerjakan fitur.

---

## Pull Request Process

### 1. Fork dan Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/Kocak-SQL.git
cd Kocak-SQL
git remote add upstream https://github.com/8782hei-sketch/Kocak-SQL.git
```

### 2. Buat Branch Fitur
```bash
git checkout -b feature/nama-fitur
# atau untuk bug fix:
git checkout -b fix/nama-bug
```

**Naming Convention:**
- Fitur baru: `feature/deskripsi-singkat`
- Bug fix: `fix/deskripsi-singkat`
- Documentation: `docs/deskripsi-singkat`
- Testing: `test/deskripsi-singkat`

### 3. Setup Development Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# atau
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 4. Buat Perubahan
- Pastikan kode mengikuti standar (lihat [Standar Kode](#standar-kode))
- Commit secara regular dengan pesan yang jelas
- Jangan commit file yang tidak perlu (gunakan `.gitignore`)

### 5. Commit dengan Pesan yang Jelas
```bash
git commit -m "feat: tambahkan fitur baru xyz"
git commit -m "fix: perbaiki bug di module abc"
git commit -m "docs: update dokumentasi readme"
```

**Format Commit:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type:**
- `feat` - Fitur baru
- `fix` - Bug fix
- `docs` - Dokumentasi
- `style` - Formatting, missing semicolons, etc
- `refactor` - Refactoring kode
- `test` - Adding tests
- `chore` - Build process, dependencies, etc

### 6. Push dan Buat Pull Request
```bash
git push origin feature/nama-fitur
```

Buat Pull Request di GitHub dengan:
- Deskripsi yang jelas tentang apa yang diubah
- Reference ke Issue jika ada (gunakan `Closes #123`)
- Checklist:
  - [ ] Kode mengikuti standar repository
  - [ ] Testing sudah dilakukan
  - [ ] Dokumentasi sudah diupdate
  - [ ] Tidak ada breaking changes (atau sudah dijelaskan)

### 7. Code Review
- Maintainer akan melakukan review
- Respond terhadap feedback dengan konstruktif
- Push perubahan baru ke branch yang sama (jangan buat PR baru)

### 8. Merge
Setelah approval dari maintainer, PR akan di-merge.

---

## Standar Kode

### Python Style Guide
Ikuti [PEP 8](https://www.python.org/dev/peps/pep-0008/) dengan pedoman:

**Naming Convention:**
```python
# Classes: PascalCase
class DatabaseManager:
    pass

# Functions & variables: snake_case
def execute_query():
    result = None
    return result

# Constants: UPPER_CASE
MAX_CONNECTIONS = 100
DEFAULT_TIMEOUT = 30
```

**Code Quality:**
- Max line length: 100 characters
- Gunakan type hints kapan memungkinkan
- Write descriptive docstrings untuk functions dan classes
- Hindari nested if-statements yang terlalu dalam

**Contoh Function dengan Docstring:**
```python
def parse_kocak_sql_command(command: str) -> dict:
    """
    Parse Kocak-SQL DSL command menjadi SQL query.
    
    Args:
        command (str): Perintah Kocak-SQL yang akan diparse
        
    Returns:
        dict: Hasil parsing dengan keys 'sql', 'type', 'success'
        
    Raises:
        ValueError: Jika command tidak valid
        
    Example:
        >>> result = parse_kocak_sql_command('lihat_data: users')
        >>> result['sql']
        'SELECT * FROM users'
    """
    # Implementation
    pass
```

### HTML/CSS Standards
- Gunakan semantic HTML5
- Ikuti BEM naming convention untuk CSS
- Mobile-first responsive design
- Inline comments untuk logic yang kompleks

### File Organization
```
module/
├── __init__.py
├── main_logic.py      # Core functionality
├── utils.py           # Helper functions
├── constants.py       # Magic strings/numbers
└── errors.py          # Custom exceptions
```

---

## Struktur File

Pastikan file baru/modified mengikuti struktur existing:

```
Kocak-SQL/
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── api.py
│   │   ├── db_manager.py
│   │   └── server_status.py
│   ├── static/
│   │   ├── style.css
│   │   └── [css files]
│   └── templates/
│       ├── base.html
│       ├── dashboard.html
│       └── db_view.html
├── tests/             # Baru: test files
│   ├── __init__.py
│   ├── test_db_manager.py
│   └── test_api.py
├── run.py
├── contoh_client.py
├── requirements.txt
├── .gitignore
├── LICENSE
├── README.md
└── CONTRIBUTING.md
```

---

## Testing

Sebelum submit PR:
1. Test fitur Anda secara manual
2. Pastikan tidak ada error di console
3. Test di berbagai browser (jika UI changes)
4. Buat unit test untuk logic yang kompleks

---

## Questions?

Jika ada pertanyaan, silakan:
1. Buka GitHub Issue
2. Gunakan Discussion jika sudah tersedia
3. Email ke maintainer jika perlu

---

**Terima kasih telah berkontribusi! ❤️**
