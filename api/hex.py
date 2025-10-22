from http.server import BaseHTTPRequestHandler
import json
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlparse, parse_qs

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

_ICHING_CACHE: Optional[Dict[str, Any]] = None

def _load_iching_db() -> Dict[str, Any]:
    """加载易经数据库"""
    global _ICHING_CACHE
    if _ICHING_CACHE is not None:
        return _ICHING_CACHE
    
    json_path = DATA_DIR / "iching_basic.json"
    if not json_path.exists():
        _ICHING_CACHE = {}
        return _ICHING_CACHE
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            _ICHING_CACHE = json.load(f)
    except Exception:
        _ICHING_CACHE = {}
    
    return _ICHING_CACHE

def find_record(name: str) -> Optional[Dict[str, Any]]:
    """根据卦名查找记录"""
    db = _load_iching_db()
    for record in db.get("hexagrams", []):
        if record.get("name") == name:
            return record
    return None

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # 解析URL路径
            parsed_url = urlparse(self.path)
            path_parts = parsed_url.path.strip('/').split('/')
            
            # 期望路径格式: /api/hex/{code}
            if len(path_parts) < 3 or path_parts[0] != 'api' or path_parts[1] != 'hex':
                self.send_error_response("Invalid path format", 404)
                return
            
            try:
                code = int(path_parts[2])
            except ValueError:
                self.send_error_response("Invalid hexagram code", 400)
                return
            
            if not (1 <= code <= 64):
                self.send_error_response("Hexagram code must be between 1 and 64", 400)
                return
            
            # 获取卦象名称
            hexagram_names = [
                "乾","坤","屯","蒙","需","讼","师","比","小畜","履","泰","否","同人","大有","谦","豫",
                "随","蛊","临","观","噬嗑","贲","剥","复","无妄","大畜","颐","大过","坎","离","咸","恒",
                "遁","大壮","晋","明夷","家人","睽","蹇","解","损","益","夬","姤","萃","升","困","井","革",
                "鼎","震","艮","渐","归妹","丰","旅","巽","兑","涣","节","中孚","小过","既济","未济"
            ]
            
            name = hexagram_names[code - 1]
            record = find_record(name)
            
            if not record:
                result = {
                    "code": code,
                    "name": name,
                    "judgement": f"{name}：利于正道与循序渐进。",
                    "image": "",
                    "lines": []
                }
            else:
                result = {
                    "code": code,
                    "name": name,
                    "judgement": record.get("judgement", f"{name}：利于正道与循序渐进。"),
                    "image": record.get("image", ""),
                    "lines": record.get("lines", [])
                }
            
            # 返回结果
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            response = json.dumps(result, ensure_ascii=False)
            self.wfile.write(response.encode('utf-8'))
            
        except Exception as e:
            self.send_error_response(f"Server error: {str(e)}")
    
    def send_error_response(self, message: str, status_code: int = 500):
        """发送错误响应"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        error_response = json.dumps({"error": message}, ensure_ascii=False)
        self.wfile.write(error_response.encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()