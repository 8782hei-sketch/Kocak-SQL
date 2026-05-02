from flask import Blueprint, request, jsonify
from app.database import get_db_connection
from app.modules.db_manager import parse_kocak_query

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/query', methods=['POST'])
def execute_api_query():
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"status": "error", "message": "Field 'query' tidak ditemukan dalam JSON body"}), 400
        
    original_query = data['query']
    statements = parse_kocak_query(original_query)
    
    conn = get_db_connection()
    result_data = None
    
    try:
        if len(statements) == 1:
            sql_query = statements[0]
            if sql_query.strip().upper().startswith("SELECT") or sql_query.strip().upper().startswith("PRAGMA"):
                cursor = conn.execute(sql_query)
                rows = cursor.fetchall()
                # convert sqlite3.Row to dict
                result_data = [dict(row) for row in rows]
                message = "Berhasil mengambil data"
            else:
                conn.execute(sql_query)
                conn.commit()
                message = "Berhasil mengeksekusi perintah"
        elif len(statements) > 1:
            script_to_run = "\n".join(statements)
            conn.executescript(script_to_run)
            message = f"Berhasil mengeksekusi batch perintah ({len(statements)} perintah)."
        else:
            message = "Perintah kosong."
            
        return jsonify({"status": "success", "message": message, "data": result_data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        conn.close()
