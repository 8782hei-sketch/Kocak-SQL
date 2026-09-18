from flask import Blueprint, request, jsonify, session
from app.database import get_db_connection, list_databases, create_database, delete_database, DEFAULT_DB
from app.modules.db_manager import parse_kocak_query
import time

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/query', methods=['POST'])
def execute_api_query():
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"status": "error", "message": "Field 'query' tidak ditemukan dalam JSON body"}), 400
        
    original_query = data['query']
    db_name = data.get('database', session.get('current_db', DEFAULT_DB))
    statements = parse_kocak_query(original_query)
    
    conn = get_db_connection(db_name)
    result_data = None
    execution_time = 0
    
    start_time = time.time()
    
    try:
        if len(statements) == 1:
            sql_query = statements[0]
            if sql_query.strip().upper().startswith("SELECT") or sql_query.strip().upper().startswith("PRAGMA"):
                cursor = conn.execute(sql_query)
                rows = cursor.fetchall()
                result_data = [dict(row) for row in rows]
                message = "Berhasil mengambil data"
            else:
                conn.execute(sql_query)
                conn.commit()
                affected = conn.total_changes
                message = f"Berhasil mengeksekusi perintah. {affected} baris terpengaruh"
        elif len(statements) > 1:
            script_to_run = "\n".join(statements)
            conn.executescript(script_to_run)
            conn.commit()
            message = f"Berhasil mengeksekusi batch perintah ({len(statements)} perintah)."
        else:
            message = "Perintah kosong."
            
        execution_time = time.time() - start_time
        return jsonify({
            "status": "success", 
            "message": message, 
            "data": result_data,
            "execution_time_ms": round(execution_time * 1000, 2)
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        conn.close()


@api_bp.route('/databases', methods=['GET'])
def list_databases_api():
    """List all available databases"""
    databases = list_databases()
    return jsonify({
        "status": "success",
        "databases": databases,
        "count": len(databases)
    })


@api_bp.route('/database/create', methods=['POST'])
def create_database_api():
    """Create a new database"""
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"status": "error", "message": "Field 'name' required"}), 400
    
    db_name = data['name']
    success, msg = create_database(db_name)
    
    if success:
        return jsonify({"status": "success", "message": msg, "database": db_name})
    else:
        return jsonify({"status": "error", "message": msg}), 400


@api_bp.route('/database/<db_name>', methods=['DELETE'])
def delete_database_api(db_name):
    """Delete a database"""
    success, msg = delete_database(db_name)
    
    if success:
        return jsonify({"status": "success", "message": msg, "database": db_name})
    else:
        return jsonify({"status": "error", "message": msg}), 400


@api_bp.route('/database/<db_name>/tables', methods=['GET'])
def list_tables_api(db_name):
    """List all tables in a database"""
    conn = get_db_connection(db_name)
    try:
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        table_names = [t['name'] for t in tables]
        return jsonify({
            "status": "success",
            "database": db_name,
            "tables": table_names,
            "count": len(table_names)
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        conn.close()


@api_bp.route('/database/<db_name>/table/<table_name>', methods=['GET'])
def get_table_data_api(db_name, table_name):
    """Get table data with optional filtering and pagination"""
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    where = request.args.get('where', None)
    
    conn = get_db_connection(db_name)
    try:
        if where:
            query = f"SELECT * FROM {table_name} WHERE {where} LIMIT ? OFFSET ?"
            count_query = f"SELECT COUNT(*) FROM {table_name} WHERE {where}"
        else:
            query = f"SELECT * FROM {table_name} LIMIT ? OFFSET ?"
            count_query = f"SELECT COUNT(*) FROM {table_name}"
        
        rows = conn.execute(query, (limit, offset)).fetchall()
        columns = [description[0] for description in conn.execute(f"SELECT * FROM {table_name} LIMIT 1;").description]
        total = conn.execute(count_query).fetchone()[0]
        
        data = [dict(row) for row in rows]
        return jsonify({
            "status": "success",
            "database": db_name,
            "table": table_name,
            "columns": columns,
            "data": data,
            "total": total,
            "limit": limit,
            "offset": offset
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        conn.close()


@api_bp.route('/database/<db_name>/table/<table_name>/schema', methods=['GET'])
def get_table_schema_api(db_name, table_name):
    """Get table schema"""
    conn = get_db_connection(db_name)
    try:
        schema = conn.execute(f"PRAGMA table_info({table_name});").fetchall()
        columns = [{
            "cid": r[0],
            "name": r[1],
            "type": r[2],
            "notnull": bool(r[3]),
            "default": r[4],
            "pk": bool(r[5])
        } for r in schema]
        
        # Get indexes
        indexes = conn.execute(f"PRAGMA index_list({table_name});").fetchall()
        index_list = []
        for idx in indexes:
            index_cols = conn.execute(f"PRAGMA index_info({idx[1]});").fetchall()
            index_list.append({
                "name": idx[1],
                "unique": bool(idx[2]),
                "columns": [c[2] for c in index_cols]
            })
        
        return jsonify({
            "status": "success",
            "database": db_name,
            "table": table_name,
            "columns": columns,
            "indexes": index_list
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        conn.close()


@api_bp.route('/database/<db_name>/execute', methods=['POST'])
def execute_sql_api(db_name):
    """Execute raw SQL on a specific database"""
    data = request.get_json()
    if not data or 'sql' not in data:
        return jsonify({"status": "error", "message": "Field 'sql' required"}), 400
    
    sql = data['sql']
    conn = get_db_connection(db_name)
    
    try:
        if sql.strip().upper().startswith("SELECT") or sql.strip().upper().startswith("PRAGMA"):
            cursor = conn.execute(sql)
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description] if cursor.description else []
            result_data = [dict(row) for row in rows]
            return jsonify({
                "status": "success",
                "data": result_data,
                "columns": columns
            })
        else:
            conn.execute(sql)
            conn.commit()
            affected = conn.total_changes
            return jsonify({
                "status": "success",
                "message": f"{affected} rows affected",
                "affected_rows": affected
            })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        conn.close()


@api_bp.route('/export/<db_name>', methods=['GET'])
def export_database_api(db_name):
    """Export database as SQL dump"""
    import os
    from app.database import get_db_path
    
    db_path = get_db_path(db_name)
    if not os.path.exists(db_path):
        return jsonify({"status": "error", "message": "Database not found"}), 404
    
    try:
        conn = get_db_connection(db_name)
        dump = conn.iterdump()
        sql_dump = "\n".join(dump)
        conn.close()
        
        return sql_dump, 200, {
            'Content-Type': 'application/sql',
            'Content-Disposition': f'attachment; filename={db_name.replace(".db", "")}_dump.sql'
        }
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
