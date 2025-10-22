from http.server import BaseHTTPRequestHandler
import os
from pathlib import Path

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # 获取静态文件路径
            static_dir = Path(__file__).resolve().parent.parent / "static"
            index_path = static_dir / "index.html"
            
            if not index_path.exists():
                self.send_error_response("Index file not found", 404)
                return
            
            # 读取并返回index.html
            with open(index_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            
            self.wfile.write(content.encode('utf-8'))
            
        except Exception as e:
            self.send_error_response(f"Server error: {str(e)}")
    
    def send_error_response(self, message: str, status_code: int = 500):
        """发送错误响应"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error {status_code}</title>
            <meta charset="utf-8">
        </head>
        <body>
            <h1>Error {status_code}</h1>
            <p>{message}</p>
        </body>
        </html>
        """
        self.wfile.write(error_html.encode('utf-8'))