from flask import Blueprint, render_template
import psutil
import platform

server_bp = Blueprint('server', __name__)

@server_bp.route('/')
def dashboard():
    # Gather basic server info
    system_info = {
        "OS": platform.system(),
        "OS Release": platform.release(),
        "CPU Usage": f"{psutil.cpu_percent(interval=1)}%",
        "RAM Usage": f"{psutil.virtual_memory().percent}%"
    }
    return render_template('dashboard.html', system_info=system_info)
