"""
OpenRouter 生图中转服务（部署到 Railway）

claude.ai artifact → 这个服务 → OpenRouter gpt-image-2

API Key 从环境变量 OPENROUTER_API_KEY 读取（在 Railway 后台设置，不要写死在代码里）
"""

import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# 允许所有来源跨域（claude.ai artifact 需要）
CORS(app, resources={r"/*": {"origins": "*"}})

OPENROUTER_URL = "https://openrouter.ai/api/v1/images/generations"
MODEL = "openai/gpt-image-2"


@app.route("/")
def health():
    return jsonify({"status": "ok", "service": "openrouter-image-proxy"})


@app.route("/generate", methods=["POST", "OPTIONS"])
def generate():
    # 预检请求直接放行
    if request.method == "OPTIONS":
        return ("", 204)

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return jsonify({"error": "OPENROUTER_API_KEY not set on server"}), 500

    data = request.get_json(force=True) or {}
    prompt = data.get("prompt")
    if not prompt:
        return jsonify({"error": "Missing 'prompt' in request body"}), 400

    size = data.get("size", "1024x1024")
    n = data.get("n", 1)

    try:
        resp = requests.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL,
                "prompt": prompt,
                "n": n,
                "size": size,
            },
            timeout=120,
        )
        result = resp.json()

        if not resp.ok:
            return jsonify({"error": result.get("error", result)}), resp.status_code

        # 统一返回结构，前端处理 url 或 b64_json
        return jsonify(result), 200

    except requests.exceptions.Timeout:
        return jsonify({"error": "OpenRouter request timed out"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
