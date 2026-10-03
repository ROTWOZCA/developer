import os
import subprocess
import shutil
from flask import Flask, request, jsonify, render_template_string

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
            display: flex;
            flex-direction: column;
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
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 40px 20px;
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
            transition: border 0.3s;
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
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(167, 139, 250, 0.4);
        }
        .result {
            margin-top: 30px;
            padding: 20px;
            background: rgba(0, 0, 0, 0.4);
            border-radius: 12px;
            border-left: 4px solid #a78bfa;
            white-space: pre-wrap;
            font-family: monospace;
            font-size: 14px;
            max-height: 300px;
            overflow-y: auto;
        }
        .premium-section {
            margin-top: 30px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
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
        
        shutil.make_archive("/tmp/output", 'zip', project_path)
        
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial; background: #0f0c29; color: #fff; padding: 40px; }}
                .box {{ background: rgba(255,255,255,0.05); padding: 30px; border-radius: 20px; max-width: 800px; margin: auto; }}
                h2 {{ color: #a78bfa; }}
                pre {{ background: rgba(0,0,0,0.3); padding: 15px; border-radius: 10px; overflow-x: auto; }}
                a {{ color: #f472b6; text-decoration: none; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="box">
                <h2>✅ Success!</h2>
                <p>Your project has been generated.</p>
                <h3>Output:</h3>
                <pre>{result.stdout}</pre>
                <p><strong>Note:</strong> ZIP saved at /tmp/output.zip</p>
                <a href="/">← Go Back</a>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        return f"""
        <html>
        <head><style>body {{ font-family: Arial; background: #0f0c29; color: #fff; padding: 40px; }}</style></head>
        <body>
            <div style="max-width: 800px; margin: auto; background: rgba(255,255,255,0.05); padding: 30px; border-radius: 20px;">
                <h2 style="color: #ef4444;">❌ Error:</h2>
                <pre>{str(e)}</pre>
                <a href="/" style="color: #f472b6;">← Go Back</a>
            </div>
        </body>
        </html>
        """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
