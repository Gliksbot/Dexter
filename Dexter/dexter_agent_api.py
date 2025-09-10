"""
Dexter Agent API - Maxed Out (Full Local Skill/Agent Functionality)

Exposes endpoints to securely list, read, write, and execute files and skills.
"""

from flask import Flask, request, jsonify
import os
import json
import subprocess
from pathlib import Path
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# ====== BASIC SECURITY (Change this key!) =====
API_KEY = "dexter-local-agent-key-2025"
SKILLS_DIR = Path("skills")
SKILLS_DIR.mkdir(exist_ok=True)

def authenticate():
    auth = request.headers.get('Authorization', '')
    return auth == f"Bearer {API_KEY}"

# ====== ENDPOINTS ======

@app.route('/agent/health', methods=['GET'])
def health():
    return jsonify({"status": "online", "message": "Dexter Agent API running"})

@app.route('/agent/list_files', methods=['POST'])
def list_files():
    if not authenticate():
        return jsonify({"error": "Unauthorized"}), 401
    try:
        files = []
        for item in Path('.').iterdir():
            if item.is_file() and item.suffix in ['.py', '.json', '.txt', '.md']:
                files.append({"name": item.name, "type": "file", "size": item.stat().st_size})
            elif item.is_dir():
                files.append({"name": item.name, "type": "directory", "size": 0})
        return jsonify({"files": files, "status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/agent/read_file', methods=['POST'])
def read_file():
    if not authenticate():
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json or {}
    file_path = data.get('file_path', '')
    try:
        if not Path(file_path).exists():
            return jsonify({"error": "File not found"}), 404
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({"content": content, "status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/agent/write_file', methods=['POST'])
def write_file():
    if not authenticate():
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json or {}
    file_path = data.get("file_path")
    content = data.get("content", "")
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return jsonify({"status": "success", "file_path": file_path})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/agent/read_config', methods=['POST'])
def read_config():
    if not authenticate():
        return jsonify({"error": "Unauthorized"}), 401
    try:
        with open('dexter_simple_config.json', 'r') as f:
            config = json.load(f)
        return jsonify({"config": config, "status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/agent/list_skills', methods=['POST'])
def list_skills():
    """List all available skills (Python files in skills/)."""
    if not authenticate():
        return jsonify({"error": "Unauthorized"}), 401
    try:
        files = [
            {"name": f.name, "size": f.stat().st_size}
            for f in SKILLS_DIR.glob("*.py") if f.is_file()
        ]
        return jsonify({"skills": files, "status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/agent/execute_skill', methods=['POST'])
def execute_skill():
    """Run a skill file and return its output. Args can be passed as strings, but code should handle them."""
    if not authenticate():
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json or {}
    skill_name = data.get("skill_name")
    args = data.get("args", [])
    skill_path = SKILLS_DIR / f"{skill_name}.py"
    if not skill_path.exists():
        return jsonify({"error": "Skill not found"}), 404
    try:
        result = subprocess.run(
            ["python", str(skill_path)] + args,
            capture_output=True,
            text=True,
            timeout=15
        )
        return jsonify({
            "output": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode,
            "status": "success" if result.returncode == 0 else "error"
        })
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Skill execution timed out"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ====== END ======
if __name__ == '__main__':
    print("🚀 Starting Dexter Agent API (maxed out) on port 5001...")
    app.run(host='0.0.0.0', port=5001, debug=False)
