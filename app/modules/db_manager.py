from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session
from app.database import get_db_connection, list_databases, create_database, delete_database, DEFAULT_DB, get_db_path
import re
import sqlite3

db_bp = Blueprint('db_manager', __name__, url_prefix='/db')

def parse_kocak_query(query):
    """Parse Kocak-SQL custom syntax to standard SQL"""
    lines = query.strip().split('\n')
    translated_lines = []
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('--'):
            continue
            
        line_lower = line.lower()
        
        # TCL Commands
        if line_lower == 'mulai_transaksi' or line_lower == 'begin':
            translated_lines.append("BEGIN TRANSACTION;")
            continue
        elif line_lower == 'simpan_transaksi' or line_lower == 'commit':
            translated_lines.append("COMMIT;")
            continue
        elif line_lower == 'batal_transaksi' or line_lower == 'rollback':
            translated_lines.append("ROLLBACK;")
            continue
        
        # Database Management
        match = re.match(r'^buat_database:\s*(\w+)$', line, re.IGNORECASE)
        if match:
            db_name = match.group(1)
            translated_lines.append(f"-- CREATE DATABASE {db_name} (handled by application)")
            continue
        
        match = re.match(r'^hapus_database:\s*(\w+)$', line, re.IGNORECASE)
        if match:
            db_name = match.group(1)
            translated_lines.append(f"-- DROP DATABASE {db_name} (handled by application)")
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

        # DDL - CREATE TABLE
        match = re.match(r'^buat_tabel:\s*(\w+)\s*\[(.*)\]$', line, re.IGNORECASE)
        if match:
            table = match.group(1)
            cols_raw = match.group(2).split(',')
            cols_def = []
            for col in cols_raw:
                col = col.strip()
                col_parts = col.split(':')
                col_name = col_parts[0].strip()
                col_type = col_parts[1].strip().upper() if len(col_parts) > 1 else 'TEXT'
                
                type_mapping = {
                    'INT': 'INTEGER', 'INTEGER': 'INTEGER', 'ID': 'INTEGER PRIMARY KEY AUTOINCREMENT',
                    'TEXT': 'TEXT', 'STRING': 'TEXT', 'VARCHAR': 'TEXT',
                    'FLOAT': 'REAL', 'DOUBLE': 'REAL', 'DECIMAL': 'REAL',
                    'BOOL': 'INTEGER', 'BOOLEAN': 'INTEGER',
                    'DATE': 'TEXT', 'DATETIME': 'TEXT', 'TIMESTAMP': 'TEXT',
                    'JSON': 'TEXT'
                }
                sql_type = type_mapping.get(col_type, col_type)
                if col_name.lower() == 'id' and 'PRIMARY' not in sql_type:
                    sql_type = 'INTEGER PRIMARY KEY AUTOINCREMENT'
                cols_def.append(f"{col_name} {sql_type}")
            cols_str = ", ".join(cols_def)
            translated_lines.append(f"CREATE TABLE {table} ({cols_str});")
            continue
        
        # DDL - ALTER TABLE ADD COLUMN
        match = re.match(r'^tambah_kolom:\s*(\w+)\s+(\w+)\s+(\w+)$', line, re.IGNORECASE)
        if match:
            table = match.group(1)
            col_name = match.group(2)
            col_type = match.group(3).upper()
            translated_lines.append(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type};")
            continue
        
        # DDL - DROP TABLE
        match = re.match(r'^hapus_tabel:\s*(\w+)$', line, re.IGNORECASE)
        if match:
            table = match.group(1)
            translated_lines.append(f"DROP TABLE {table};")
            continue
        
        # DDL - TRUNCATE
        match = re.match(r'^kosongkan_tabel:\s*(\w+)$', line, re.IGNORECASE)
        if match:
            table = match.group(1)
            translated_lines.append(f"DELETE FROM {table};")
            continue
        
        # DML - INSERT
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
                    v = v.strip()
                    if not (v.startswith("'") and v.endswith("'")) and not v.isdigit():
                        v = f"'{v}'"
                    vals.append(v)
            cols_str = ", ".join(cols)
            vals_str = ", ".join(vals)
            translated_lines.append(f"INSERT INTO {table} ({cols_str}) VALUES ({vals_str});")
            continue
        
        # DML - SELECT
        match = re.match(r'^lihat_data:\s*(\w+)(?:\s*\[(.*)\])?$', line, re.IGNORECASE)
        if match:
            table = match.group(1)
            conditions = match.group(2)
            if conditions:
                translated_lines.append(f"SELECT * FROM {table} WHERE {conditions};")
            else:
                translated_lines.append(f"SELECT * FROM {table};")
            continue
        
        # DML - SELECT with specific columns
        match = re.match(r'^ambil:\s*(\w+)\s*\[(.*)\](?:\s*\[(.*)\])?$', line, re.IGNORECASE)
        if match:
            table = match.group(1)
            columns = match.group(2).strip()
            conditions = match.group(3).strip() if match.group(3) else None
            if conditions:
                translated_lines.append(f"SELECT {columns} FROM {table} WHERE {conditions};")
            else:
                translated_lines.append(f"SELECT {columns} FROM {table};")
            continue
        
        # DML - UPDATE
        match = re.match(r'^ubah_data:\s*(\w+)\s*\[(.*?)\]\s*\[(.*)\]$', line, re.IGNORECASE)
        if match:
            table = match.group(1)
            cond = match.group(2).strip()
            updates_raw = match.group(3).split(',')
            updates = []
            for pair in updates_raw:
                if '=' in pair:
                    k, v = pair.split('=', 1)
                    k = k.strip()
                    v = v.strip()
                    if not (v.startswith("'") and v.endswith("'")) and not v.isdigit():
                        v = f"'{v}'"
                    updates.append(f"{k}={v}")
            updates_str = ", ".join(updates)
            translated_lines.append(f"UPDATE {table} SET {updates_str} WHERE {cond};")
            continue
        
        # DML - DELETE
        match = re.match(r'^hapus_data:\s*(\w+)\s*\[(.*)\]$', line, re.IGNORECASE)
        if match:
            table = match.group(1)
            cond = match.group(2).strip()
            translated_lines.append(f"DELETE FROM {table} WHERE {cond};")
            continue
        
        # INDEX - CREATE
        match = re.match(r'^buat_index:\s*(\w+)\s+pada\s+(\w+)$', line, re.IGNORECASE)
        if match:
            index_name = match.group(1)
            table_col = match.group(2)
            parts = table_col.split('.')
            if len(parts) == 2:
                table, col = parts
                translated_lines.append(f"CREATE INDEX {index_name} ON {table}({col});")
            continue
        
        # INDEX - DROP
        match = re.match(r'^hapus_index:\s*(\w+)$', line, re.IGNORECASE)
        if match:
            index_name = match.group(1)
            translated_lines.append(f"DROP INDEX {index_name};")
            continue
        
        # VIEW - CREATE
        match = re.match(r'^buat_view:\s*(\w+)\s+sebagai\s+(.*)$', line, re.IGNORECASE)
        if match:
            view_name = match.group(1)
            select_query = match.group(2).strip()
            translated_lines.append(f"CREATE VIEW {view_name} AS {select_query};")
            continue
        
        # VIEW - DROP
        match = re.match(r'^hapus_view:\s*(\w+)$', line, re.IGNORECASE)
        if match:
            view_name = match.group(1)
            translated_lines.append(f"DROP VIEW {view_name};")
            continue
        
        # Native SQL passthrough
        if any(line.upper().startswith(kw) for kw in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER', 'TRUNCATE', 'BEGIN', 'COMMIT', 'ROLLBACK', 'PRAGMA']):
            translated_lines.append(line)
            continue
        
        # Fallback - try as native SQL
        translated_lines.append(line)

    return translated_lines


@db_bp.route('/')
def index():
    conn = get_db_connection()
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    conn.close()
    databases = list_databases()
    current_db = session.get('current_db', DEFAULT_DB)
    return render_template('db_view.html', tables=tables, current_table=None, rows=None, 
                         databases=databases, current_db=current_db)


@db_bp.route('/switch_db/<db_name>')
def switch_database(db_name):
    session['current_db'] = db_name
    return redirect(url_for('db_manager.index'))


@db_bp.route('/create_db', methods=['POST'])
def create_new_db():
    db_name = request.form.get('db_name')
    if db_name:
        success, msg = create_database(db_name)
        if success:
            session['current_db'] = db_name
    return redirect(url_for('db_manager.index'))


@db_bp.route('/delete_db/<db_name>', methods=['POST'])
def delete_db(db_name):
    success, msg = delete_database(db_name)
    return redirect(url_for('db_manager.index'))


@db_bp.route('/table/<table_name>')
def view_table(table_name):
    current_db = session.get('current_db', DEFAULT_DB)
    conn = get_db_connection(current_db)
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    
    try:
        rows = conn.execute(f"SELECT * FROM {table_name} LIMIT 100;").fetchall()
        columns = [description[0] for description in conn.execute(f"SELECT * FROM {table_name} LIMIT 1;").description]
        
        # Get table info
        table_info = conn.execute(f"PRAGMA table_info({table_name});").fetchall()
        
        # Get row count
        count = conn.execute(f"SELECT COUNT(*) as cnt FROM {table_name};").fetchone()[0]
    except Exception as e:
        rows = []
        columns = []
        table_info = []
        count = 0
        
    conn.close()
    databases = list_databases()
    return render_template('db_view.html', tables=tables, current_table=table_name, rows=rows, 
                         columns=columns, table_info=table_info, row_count=count,
                         databases=databases, current_db=current_db)


@db_bp.route('/execute', methods=['POST'])
def execute_query():
    original_query = request.form.get('query')
    current_db = session.get('current_db', DEFAULT_DB)
    statements = parse_kocak_query(original_query)
    
    conn = get_db_connection(current_db)
    result = None
    message = ""
    execution_time = 0
    
    import time
    start_time = time.time()
    
    try:
        if len(statements) == 1:
            sql_query = statements[0]
            if sql_query.strip().upper().startswith("SELECT") or sql_query.strip().upper().startswith("PRAGMA"):
                cursor = conn.execute(sql_query)
                rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description] if cursor.description else []
                result = {"columns": columns, "rows": rows}
                message = f"Query berhasil: {len(rows)} baris ditemukan"
            else:
                conn.execute(sql_query)
                conn.commit()
                affected = conn.total_changes
                message = f"Berhasil dieksekusi. {affected} baris terpengaruh"
        elif len(statements) > 1:
            script_to_run = "\n".join(statements)
            conn.executescript(script_to_run)
            conn.commit()
            message = f"Berhasil mengeksekusi batch perintah ({len(statements)} perintah)."
        else:
            message = "Perintah kosong."
            
    except Exception as e:
        result = None
        message = f"Error: {str(e)}"
    finally:
        execution_time = time.time() - start_time
        conn.close()
        
    # Re-fetch tables
    conn = get_db_connection(current_db)
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    conn.close()
    
    databases = list_databases()
        
    return render_template('db_view.html', tables=tables, current_table=None, rows=None, 
                         query_result=result, message=message, query=original_query,
                         execution_time=execution_time, databases=databases, current_db=current_db)


@db_bp.route('/api/table/<table_name>/schema')
def get_table_schema(table_name):
    """API endpoint to get table schema"""
    current_db = session.get('current_db', DEFAULT_DB)
    conn = get_db_connection(current_db)
    try:
        schema = conn.execute(f"PRAGMA table_info({table_name});").fetchall()
        columns = [{"cid": r[0], "name": r[1], "type": r[2], "notnull": r[3], "default": r[4], "pk": r[5]} for r in schema]
        return jsonify({"status": "success", "table": table_name, "columns": columns})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        conn.close()


@db_bp.route('/api/table/<table_name>/data')
def get_table_data(table_name):
    """API endpoint to get table data with pagination"""
    current_db = session.get('current_db', DEFAULT_DB)
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    conn = get_db_connection(current_db)
    try:
        rows = conn.execute(f"SELECT * FROM {table_name} LIMIT ? OFFSET ?", (limit, offset)).fetchall()
        columns = [description[0] for description in conn.execute(f"SELECT * FROM {table_name} LIMIT 1;").description]
        total = conn.execute(f"SELECT COUNT(*) FROM {table_name};").fetchone()[0]
        
        data = [dict(row) for row in rows]
        return jsonify({"status": "success", "table": table_name, "columns": columns, "data": data, "total": total, "limit": limit, "offset": offset})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        conn.close()
