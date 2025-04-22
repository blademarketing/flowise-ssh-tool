from flask import Flask, request, jsonify
import subprocess, os, logging
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

API_KEY = os.getenv("AGENT_API_KEY")
ALLOWED_IPS = os.getenv("ALLOWED_IPS", "").split(",")
LOG_FILE = os.getenv("LOG_FILE", "agent_shell.log")

logger = logging.getLogger("agent_logger")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(LOG_FILE)
formatter = logging.Formatter("%(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)
logger.addHandler(handler)


def log_denied(ip, reason, data=None):
    msg = f"{ip} | DENIED: {reason}"
    if data:
        msg += f" | DATA: {data}"
    logger.warning(msg)


def log_command(ip, cmd, stdout, stderr):
    msg = f"{ip} | CMD: {cmd} | OUT: {stdout.strip()} | ERR: {stderr.strip()}"
    logger.info(msg)


@app.before_request
def limit_ip():
    remote_ip = request.remote_addr
    if remote_ip not in ALLOWED_IPS:
        log_denied(remote_ip, "IP not allowed")
        return jsonify({"error": "Forbidden"}), 403


@app.route("/run", methods=["POST"])
def run_command():
    remote_ip = request.remote_addr

    if request.headers.get("Authorization") != f"Bearer {API_KEY}":
        log_denied(remote_ip, "Invalid API key", data=request.get_data(as_text=True))
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    cmd = data.get("command") if data else None  # 🛠️ Safe extraction

    if not cmd or not isinstance(cmd, str):
        log_denied(remote_ip, "Invalid command", data=str(data))
        return jsonify({"error": "Invalid command"}), 400

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        log_command(remote_ip, cmd, result.stdout, result.stderr)
        return jsonify({
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=33366)
