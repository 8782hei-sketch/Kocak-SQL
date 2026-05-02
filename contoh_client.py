import requests
import json
import time

# URL API dari server Kocak-SQL
URL = "http://127.0.0.1:5000/api/query"

def jalankan_query(perintah):
    """Fungsi pembantu untuk mengirim permintaan ke API Kocak-SQL"""
    payload = {"query": perintah}
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(URL, json=payload, headers=headers)
        data = response.json()
        
        if data.get('status') == 'success':
            print(f"✅ Sukses: {data['message']}")
            if data.get('data'):
                print("📊 Data yang Diterima:")
                print(json.dumps(data['data'], indent=2))
        else:
            print(f"❌ Gagal: {data.get('message', 'Unknown Error')}")
    except requests.exceptions.ConnectionError:
        print("❌ Kesalahan: Tidak dapat terhubung ke server. Pastikan Kocak-SQL (run.py) sudah berjalan.")
    except Exception as e:
        print(f"❌ Kesalahan: {e}")

if __name__ == "__main__":
    print("======================================")
    print("   DEMO CLIENT API KOCAK-SQL          ")
    print("======================================\n")
    
    print("1. Membuat tabel 'produk'...")
    jalankan_query("buat_tabel: produk [id, nama, harga, stok]")
    time.sleep(1)
    
    print("\n2. Mengirim beberapa data ke tabel 'produk' menggunakan TCL (Batch)...")
    jalankan_query("""
mulai_transaksi
tambah_data: produk [nama='Laptop Asus', harga=7500000, stok=10]
tambah_data: produk [nama='Mouse Logitech', harga=150000, stok=50]
tambah_data: produk [nama='Keyboard Mechanical', harga=450000, stok=20]
simpan_transaksi
    """)
    time.sleep(1)
    
    print("\n3. Memanggil/Melihat data dari tabel 'produk' (Read)...")
    jalankan_query("lihat_data: produk")
    time.sleep(1)
    
    print("\n4. Mengubah data stok 'Mouse Logitech' (Update)...")
    jalankan_query("ubah_data: produk [id=2] [stok=45]")
    time.sleep(1)
    
    print("\n5. Mengecek ulang data (Read)...")
    jalankan_query("lihat_data: produk")
    
    print("\n======================================")
    print("Demo selesai. Anda bisa melihat perubahan ini di WebUI Kocak-SQL.")
