from http.server import BaseHTTPRequestHandler
import json
import random
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib import request as _urlreq

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# 易经基础数据
HEXAGRAM_NAMES = [
    "乾","坤","屯","蒙","需","讼","师","比","小畜","履","泰","否","同人","大有","谦","豫",
    "随","蛊","临","观","噬嗑","贲","剥","复","无妄","大畜","颐","大过","坎","离","咸","恒",
    "遁","大壮","晋","明夷","家人","睽","蹇","解","损","益","夬","姤","萃","升","困","井","革",
    "鼎","震","艮","渐","归妹","丰","旅","巽","兑","涣","节","中孚","小过","既济","未济"
]

WEN_MATRIX = [
    [1,43,14,34,9,5,26,11],
    [10,58,38,54,61,60,41,19],
    [13,49,30,55,37,63,22,36],
    [25,17,21,51,42,3,27,24],
    [44,28,50,32,57,48,18,46],
    [6,47,64,40,59,29,4,7],
    [33,31,56,62,53,39,52,15],
    [12,45,35,16,20,8,23,2],
]

TRIGRAM_BITS_TO_IDX = {
    0b111:0, 0b110:1, 0b101:2, 0b100:3,
    0b011:4, 0b010:5, 0b001:6, 0b000:7,
}

TRIGRAM_IDX_TO_NAME = ["乾","兑","离","震","巽","坎","艮","坤"]

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

def _hexagram_index_from_lines(lines: list[int]) -> tuple[int, str, str]:
    """从爻线计算卦象索引"""
    upper_bits = (lines[5] << 2) | (lines[4] << 1) | lines[3]
    lower_bits = (lines[2] << 2) | (lines[1] << 1) | lines[0]
    
    upper_idx = TRIGRAM_BITS_TO_IDX.get(upper_bits, 0)
    lower_idx = TRIGRAM_BITS_TO_IDX.get(lower_bits, 0)
    
    code = WEN_MATRIX[upper_idx][lower_idx]
    name = HEXAGRAM_NAMES[code - 1] if 1 <= code <= 64 else "未知"
    
    upper_name = TRIGRAM_IDX_TO_NAME[upper_idx]
    lower_name = TRIGRAM_IDX_TO_NAME[lower_idx]
    
    return code, name, f"{upper_name}{lower_name}"

def divine_coin(question: str = "") -> Dict[str, Any]:
    """铜钱占卜"""
    lines = []
    moving = []
    
    for _ in range(6):
        coins = [random.choice([0, 1]) for _ in range(3)]
        heads = sum(coins)
        
        if heads == 3:  # 三个正面
            lines.append(1)
            moving.append(True)
        elif heads == 0:  # 三个反面
            lines.append(0)
            moving.append(True)
        elif heads == 2:  # 两正一反
            lines.append(1)
            moving.append(False)
        else:  # 一正两反
            lines.append(0)
            moving.append(False)
    
    # 计算本卦
    code, name, trigrams = _hexagram_index_from_lines(lines)
    upper, lower = trigrams[:1], trigrams[1:]
    
    # 计算变卦
    changed_lines = [1-line if mov else line for line, mov in zip(lines, moving)]
    code2, name2, _ = _hexagram_index_from_lines(changed_lines)
    
    return {
        "method": "coin",
        "question": question,
        "primary": {
            "code": code,
            "name": name,
            "upper": upper,
            "lower": lower,
            "lines": lines,
            "moving": moving
        },
        "changed": {
            "code": code2,
            "name": name2,
            "lines": changed_lines
        }
    }

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # 解析JSON
            try:
                data = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError:
                data = {}
            
            # 获取问题
            question = data.get('question', '')
            
            # 执行占卜
            result = divine_coin(question)
            
            # 返回结果
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            response = json.dumps(result, ensure_ascii=False)
            self.wfile.write(response.encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = json.dumps({"error": str(e)}, ensure_ascii=False)
            self.wfile.write(error_response.encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()