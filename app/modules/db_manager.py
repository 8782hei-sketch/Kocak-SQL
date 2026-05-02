from flask import Blueprint, render_template, request, redirect, url_for
from app.database import get_db_connection
import re

db_bp = Blueprint('db_manager', __name__, url_prefix='/db')

def parse_kocak_query(query):
    lines = query.strip().split('\n')
    translated_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # TCL Commands
        if line.lower() == 'mulai_transaksi':
            translated_lines.append("BEGIN TRANSACTION;")
            continue
        elif line.lower() == 'simpan_transaksi':
            translated_lines.append("COMMIT;")
            continue
        elif line.lower() == 'batal_transaksi':
            translated_lines.append("ROLLBACK;")
            continue
            
        # DCL Commands (Simulasi ke tabel users)
        match = re.match(r'^beri_akses:\s*(\w+)\s*\[(.*)\]$', line, re.IGNORECASE)
        if match:
            username = match.group(1)
            role = match.group(2).strip()
            translated_lines.append(f"UPDATE users SET role='{role}' WHERE username='{username}';")
            continue
            
        match = re.match(r'^cabut_akses:\s*(\w+)$', line, re.IGNORECASE)
        if match:
            username = match.group(1)
            translated_lines.append(f"UPDATE users SET role='pengguna_biasa' WHERE username='{username}';")
            continue

        # CRUD & DDL Commands
        match = re.match(r'^buat_tabel:\s*(\w+)\s*\[(.*)\]$', line, re.IGNORECASE)
        if match:
            table = match.group(1)
            cols_raw = match.group(2).split(',')
            cols_def = []
            for col in cols_raw:
                col = col.strip()
                if col.lower() == 'id':
                    cols_def.append(f"{col} INTEGER PRIMARY KEY AUTOINCREMENT")
                elif any(x in col.lower() for x in ['age', 'umur', 'harga', 'stok', 'jumlah', 'qty']):
                    cols_def.append(f"{col} INTEGER")
                else:
                    cols_def.append(f"{col} TEXT")
            cols_str = ", ".join(cols_def)
            translated_lines.append(f"CREATE TABLE {table} ({cols_str});")
            continue
            
        match = re.match(r'^tambah_data:\s*(\w+)\s*\[(.*)\]$', line, re.IGNORECASE)
        if match:
            table = match.group(1)
            pairs_raw = match.group(2).split(',')
            cols = []
            vals = []
            for pair in pairs_raw:
                if '=' in pair:
                    k, v = pair.split('=', 1)
                    cols.append(k.strip())
                    vals.append(v.strip())
            cols_str = ", ".join(cols)
            vals_str = ", ".join(vals)
            translated_lines.append(f"INSERT INTO {table} ({cols_str}) VALUES ({vals_str});")
            continue
            
        match = re.match(r'^ubah_data:\s*(\w+)\s*\[(.*?)\]\s*\[(.*)\]$', line, re.IGNORECASE)
        if match:
            table = match.group(1)
            cond = match.group(2).strip()
            updates_raw = match.group(3).split(',')
            updates = []
            for pair in updates_raw:
                if '=' in pair:
                    k, v = pair.split('=', 1)
                    updates.append(f"{k.strip()}={v.strip()}")
            updates_str = ", ".join(updates)
            translated_lines.append(f"UPDATE {table} SET {updates_str} WHERE {cond};")
            continue
            
        match = re.match(r'^hapus_data:\s*(\w+)\s*\[(.*)\]$', line, re.IGNORECASE)
        if match:
            table = match.group(1)
            cond = match.group(2).strip()
            translated_lines.append(f"DELETE FROM {table} WHERE {cond};")
            continue
            
        match = re.match(r'^lihat_data:\s*(\w+)$', line, re.IGNORECASE)
        if match:
            table = match.group(1)
            translated_lines.append(f"SELECT * FROM {table};")
            continue
            
        match = re.match(r'^hapus_tabel:\s*(\w+)$', line, re.IGNORECASE)
        if match:
            table = match.group(1)
            translated_lines.append(f"DROP TABLE {table};")
            continue
            
        # Fallback
        translated_lines.append(line)

    return translated_lines

@db_bp.route('/')
def index():
    conn = get_db_connection()
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    conn.close()
    return render_template('db_view.html', tables=tables, current_table=None, rows=None)

@db_bp.route('/table/<table_name>')
def view_table(table_name):
    conn = get_db_connection()
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    
    try:
        rows = conn.execute(f"SELECT * FROM {table_name} LIMIT 100;").fetchall()
        columns = [description[0] for description in conn.execute(f"SELECT * FROM {table_name}").description]
    except Exception as e:
        rows = []
        columns = []
        
    conn.close()
    return render_template('db_view.html', tables=tables, current_table=table_name, rows=rows, columns=columns)

@db_bp.route('/execute', methods=['POST'])
def execute_query():
    original_query = request.form.get('query')
    statements = parse_kocak_query(original_query)
    
    conn = get_db_connection()
    result = None
    message = ""
    
    try:
        if len(statements) == 1:
            sql_query = statements[0]
            if sql_query.strip().upper().startswith("SELECT") or sql_query.strip().upper().startswith("PRAGMA"):
                cursor = conn.execute(sql_query)
                rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description] if cursor.description else []
                result = {"columns": columns, "rows": rows}
                message = f"Berhasil dieksekusi: {sql_query}"
            else:
                conn.execute(sql_query)
                conn.commit()
                message = f"Berhasil dieksekusi: {sql_query}"
        elif len(statements) > 1:
            script_to_run = "\n".join(statements)
            conn.executescript(script_to_run)
            message = f"Berhasil mengeksekusi batch perintah ({len(statements)} perintah)."
        else:
            message = "Perintah kosong."
            
    except Exception as e:
        result = None
        message = f"Error: {str(e)}"
    finally:
        conn.close()
        
    # Re-fetch tables to show in sidebar
    conn = get_db_connection()
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    conn.close()
        
    return render_template('db_view.html', tables=tables, current_table=None, rows=None, query_result=result, message=message, query=original_query)
