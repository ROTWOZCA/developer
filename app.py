import os
import subprocess
import shutil
from flask import Flask, request, render_template_string, send_file

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smol Developer - AI Coding Agent</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: #fff;
            min-height: 100vh;
        }
        header {
            padding: 20px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        .logo { font-size: 24px; font-weight: bold; color: #a78bfa; }
        .premium-badge {
            background: linear-gradient(90deg, #f59e0b, #fbbf24);
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
            color: #000;
        }
        .container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 60px 20px;
        }
        h1 {
            font-size: 48px;
            margin-bottom: 20px;
            background: linear-gradient(90deg, #a78bfa, #f472b6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
        }
        p.subtitle {
            color: #9ca3af;
            margin-bottom: 40px;
            text-align: center;
            font-size: 18px;
        }
        .card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 40px;
            width: 100%;
            max-width: 700px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        }
        textarea {
            width: 100%;
            height: 150px;
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 15px;
            color: #fff;
            font-size: 16px;
            resize: none;
            outline: none;
        }
        textarea:focus { border-color: #a78bfa; }
        .btn {
            margin-top: 20px;
            width: 100%;
            padding: 15px;
            background: linear-gradient(90deg, #a78bfa, #f472b6);
            border: none;
            border-radius: 12px;
            color: #fff;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
        }
        .btn:hover { transform: translateY(-2px); }
        .premium-section {
            margin-top: 30px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            max-width: 700px;
            width: 100%;
        }
        .premium-card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }
        .premium-card h3 { color: #fbbf24; margin-bottom: 10px; }
        .premium-card p { color: #9ca3af; font-size: 14px; }
        .result-box {
            margin-top: 30px;
            padding: 20px;
            background: rgba(0, 0, 0, 0.4);
            border-radius: 12px;
            border-left: 4px solid #a78bfa;
            white-space: pre-wrap;
            font-family: monospace;
            font-size: 14px;
            max-height: 400px;
            overflow-y: auto;
        }
    </style>
</head>
<body>
    <header>
        <div class="logo">⚡ Smol Developer</div>
        <div class="premium-badge">✨ PREMIUM</div>
    </header>

    <div class="container">
        <h1>AI Coding Agent</h1>
        <p class="subtitle">Describe your app, and I'll build it for you.</p>

        <div class="card">
            <form action="/generate" method="post">
                <textarea name="prompt" placeholder="e.g., a simple JavaScript/HTML/CSS calculator app..."></textarea>
                <button type="submit" class="btn">🚀 Generate Code</button>
            </form>
        </div>

        <div class="premium-section">
            <div class="premium-card">
                <h3>⚡ Fast</h3>
                <p>Powered by Groq</p>
            </div>
            <div class="premium-card">
                <h3>🧠 Smart</h3>
                <p>AI-Powered</p>
            </div>
            <div class="premium-card">
                <h3>📦 ZIP</h3>
                <p>Download Code</p>
            </div>
        </div>

        {% if result %}
        <div class="result-box">
            <h3>✅ Generated:</h3>
            <pre>{{ result }}</pre>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/generate', methods=['POST'])
def generate():
    prompt = request.form.get('prompt')
    if not prompt:
        return "Prompt is required", 400
    
    project_path = "/tmp/generated_project"
    os.makedirs(project_path, exist_ok=True)
    
    try:
        result = subprocess.run(
            ["python", "main.py", "--prompt", prompt, "--generate_folder_path", project_path],
            capture_output=True, text=True, timeout=300
        )
        
        # إنشاء ملف ZIP
        shutil.make_archive("/tmp/output", 'zip', project_path)
        
        # إرسال الملف للتحميل
        return send_file(
            "/tmp/output.zip",
            as_attachment=True,
            download_name="generated_code.zip",
            mimetype="application/zip"
        )
    except Exception as e:
        return render_template_string(HTML, result=f"Error: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
