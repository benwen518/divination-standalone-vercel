#!/usr/bin/env python3
"""
独立的AI算卦服务
专注于易经占卜和AI解读功能
"""

from __future__ import annotations

import os
import json as _json
import random
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib import request as _urlreq

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# ===================== 应用配置 =====================

app = FastAPI(
    title="AI算卦服务",
    description="基于易经的AI智能占卜解读服务",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================== 路径配置 =====================

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
DATA_DIR = BASE_DIR / "data"

# ===================== 易经基础数据 =====================

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
    0b111:0,  # 乾
    0b110:1,  # 兑
    0b101:2,  # 离
    0b100:3,  # 震
    0b011:4,  # 巽
    0b010:5,  # 坎
    0b001:6,  # 艮
    0b000:7,  # 坤
}

TRIGRAM_IDX_TO_NAME = ["乾","兑","离","震","巽","坎","艮","坤"]

# ===================== 数据缓存 =====================

_ICHING_CACHE: Optional[Dict[str, Any]] = None

def _load_iching_db() -> Dict[str, Any]:
    """加载易经数据库"""
    global _ICHING_CACHE
    if _ICHING_CACHE is not None:
        return _ICHING_CACHE
    
    json_path = DATA_DIR / "iching_basic.json"
    if not json_path.exists():
        # 如果数据文件不存在，返回空字典
        _ICHING_CACHE = {}
        return _ICHING_CACHE
    
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            _ICHING_CACHE = _json.load(f)
    except Exception as e:
        print(f"警告：无法加载易经数据库 {json_path}: {e}")
        _ICHING_CACHE = {}
    
    return _ICHING_CACHE

# ===================== 工具函数 =====================

def _hexagram_index_from_lines(lines: list[int]) -> tuple[int, str, str]:
    """根据爻线计算卦象索引和上下卦名"""
    if len(lines) != 6:
        return 0, "", ""
    
    # 计算上下卦的三位二进制
    lower_bits = (lines[2] << 2) | (lines[1] << 1) | lines[0]
    upper_bits = (lines[5] << 2) | (lines[4] << 1) | lines[3]
    
    lower_idx = TRIGRAM_BITS_TO_IDX.get(lower_bits, 0)
    upper_idx = TRIGRAM_BITS_TO_IDX.get(upper_bits, 0)
    
    lower_name = TRIGRAM_IDX_TO_NAME[lower_idx]
    upper_name = TRIGRAM_IDX_TO_NAME[upper_idx]
    
    # 查找卦象序号
    hexagram_idx = WEN_MATRIX[upper_idx][lower_idx]
    
    return hexagram_idx, upper_name, lower_name

# ===================== 数据模型 =====================

class DivineRequest(BaseModel):
    seed: Optional[str] = None
    topic: Optional[str] = None

class AIRequest(BaseModel):
    question: str
    model: str = "Qwen/QwQ-32B"
    hexagram: Dict[str, Any]

class InterpretRequest(BaseModel):
    hexagram: Dict[str, Any]
    question: str
    model: Optional[str] = None
    lang: Optional[str] = "zh"

class LineRequest(BaseModel):
    code: int
    line: int  # 0..5，自下而上
    llm: Optional[bool] = False
    question: Optional[str] = ""
    model: Optional[str] = None

# ===================== API端点 =====================

@app.get("/")
def index() -> HTMLResponse:
    """首页"""
    html_content = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI算卦服务</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .header { text-align: center; margin-bottom: 30px; }
            .api-list { background: #f5f5f5; padding: 20px; border-radius: 8px; }
            .api-item { margin: 10px 0; }
            .method { color: #007bff; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔮 AI算卦服务</h1>
            <p>基于易经的AI智能占卜解读服务</p>
        </div>
        
        <div class="api-list">
            <h2>API接口</h2>
            <div class="api-item">
                <span class="method">POST</span> /api/divine/coin - 铜钱占卜生成卦象
            </div>
            <div class="api-item">
                <span class="method">POST</span> /api/ai - AI解读卦象
            </div>
            <div class="api-item">
                <span class="method">GET</span> /api/divine/hex/{code} - 获取卦象详细信息
            </div>
            <div class="api-item">
                <span class="method">POST</span> /api/divine/interpret - 传统卦象解读
            </div>
            <div class="api-item">
                <span class="method">POST</span> /api/divine/line - 爻辞解读
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 30px;">
            <a href="/static/index.html" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                进入算卦界面
            </a>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/api/divine/coin")
def api_divine_coin(req: DivineRequest) -> Dict[str, Any]:
    """铜钱占卜生成卦象"""
    rnd = random.Random(req.seed) if req.seed else random.SystemRandom()
    lines: list[int] = []
    moving: list[bool] = []
    
    for _ in range(6):
        # 三枚铜钱：正=3 反=2；总和 6老阴 7少阳 8少阴 9老阳
        s = sum(rnd.choice([2, 3]) for _ in range(3))
        if s == 6:
            lines.append(0)
            moving.append(True)
        elif s == 7:
            lines.append(1)
            moving.append(False)
        elif s == 8:
            lines.append(0)
            moving.append(False)
        else:  # 9
            lines.append(1)
            moving.append(True)

    # 变卦
    changed = [(1 - v) if moving[i] else v for i, v in enumerate(lines)]
    idx, upper, lower = _hexagram_index_from_lines(lines)
    idx2, up2, lo2 = _hexagram_index_from_lines(changed)
    name = HEXAGRAM_NAMES[idx - 1] if 1 <= idx <= 64 else ""
    name2 = HEXAGRAM_NAMES[idx2 - 1] if 1 <= idx2 <= 64 else ""

    return {
        "method": "coin",
        "question": req.topic or "",
        "primary": {
            "code": idx,
            "name": name,
            "upper": upper,
            "lower": lower,
            "lines": lines,
            "moving": moving,
        },
        "changed": {
            "code": idx2,
            "name": name2,
            "upper": up2,
            "lower": lo2,
            "lines": changed,
        },
        "meta": {
            "sixBeasts": ["青龙","朱雀","勾陈","腾蛇","白虎","玄武"],
        },
    }

@app.post("/api/ai")
def api_ai(req: AIRequest) -> Dict[str, Any]:
    """AI解读卦象"""
    key = os.getenv("SILICONFLOW_API_KEY") or os.getenv("SILICONFLOW_TOKEN") or os.getenv("SILICONFLOW_KEY")
    if not key:
        raise HTTPException(status_code=400, detail="缺少环境变量 SILICONFLOW_API_KEY")

    base = "https://api.siliconflow.cn/v1/chat/completions"
    sys_prompt = (
        "你是一位严谨且通俗易懂的《周易》分析助手。"
        "结合用户问题与卦象（卦名、卦辞、象辞、爻辞、变爻），"
        "给出结构化的中文解读：\n"
        "- 结论（一句话）\n- 形势分析\n- 建议（行动要点）\n- 注意事项\n"
        "要求：真实、简洁、避免迷信表达，避免绝对化断语。"
    )
    
    # 组装 messages
    hx = req.hexagram or {}
    raw_lines = hx.get('lines') or []
    try:
        lines_text = "\n".join([str(x) for x in raw_lines])
    except Exception:
        lines_text = ""
    
    raw_change_list = hx.get('changeList') or []
    try:
        change_list_text = ", ".join([str(x) for x in raw_change_list]) or '无'
    except Exception:
        change_list_text = '无'

    user_content = (
        f"问题：{req.question}\n"
        f"卦象：{hx.get('name','')}（序号 {hx.get('sequence','')}，{hx.get('fullName','')}）\n"
        f"变爻：{change_list_text}\n"
        f"卦辞：{hx.get('judgement','')}\n"
        f"象曰：{hx.get('image','')}\n"
        f"爻辞：{lines_text}"
    )
    
    payload = {
        "model": req.model,
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_content},
        ],
        "temperature": 0.7,
    }

    data = _json.dumps(payload).encode("utf-8")
    req_obj = _urlreq.Request(
        base,
        data=data,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    
    try:
        with _urlreq.urlopen(req_obj, timeout=60) as resp:
            resp_text = resp.read().decode("utf-8")
            resp_data = _json.loads(resp_text)
    except Exception as e:
        error_msg = str(e)
        if "timed out" in error_msg.lower() or "timeout" in error_msg.lower():
            raise HTTPException(status_code=504, detail="AI 服务响应超时，请稍后重试")
        else:
            raise HTTPException(status_code=502, detail=f"AI 服务请求失败: {error_msg}")

    content = None
    try:
        content = resp_data.get("choices", [{}])[0].get("message", {}).get("content")
    except Exception:
        content = None

    return {"content": content or "（无返回内容）", "raw": resp_data}

@app.get("/api/divine/hex/{code}")
def api_divine_hex(code: int) -> Dict[str, Any]:
    """获取卦象详细信息"""
    DB = _load_iching_db()
    rec = DB.get(str(code))
    if not rec:
        raise HTTPException(status_code=404, detail="hexagram not found")
    return rec

@app.post("/api/divine/interpret")
def api_divine_interpret(req: InterpretRequest) -> Dict[str, Any]:
    """传统卦象解读"""
    h = req.hexagram
    p = h.get("primary", {})
    c = h.get("changed", {})
    name = p.get("name", "")
    name2 = c.get("name", "")
    moving = p.get("moving", [])
    moving_cnt = int(sum(1 for x in moving if x))
    q = (req.question or "").strip() or "综合运势"

    # 载入离线基础库
    DB = _load_iching_db()

    def find_record(hexa_name: str):
        for k,v in DB.items():
            if v.get("name") == hexa_name:
                return v
        return None

    rec = find_record(name) or {}
    rec2 = find_record(name2) or {}

    # 组合解释
    summary = (rec.get("judgement") or f"{name}：利于正道与循序渐进。")
    summary = f"卦名：{name}。针对「{q}」，{summary} 动爻{moving_cnt}。若推进受阻，可参考变卦「{name2}」。"
    details = []
    if rec.get("image"):
        details.append("象传：" + rec["image"])
    if moving_cnt:
        idxs = [i for i,b in enumerate(moving) if b]
        for i in idxs[:2]:
            line_text = (rec.get("lines") or [])
            if 0 <= i < len(line_text):
                details.append(f"动爻·{line_text[i]}")
    if rec2.get("judgement"):
        details.append("变卦启示：" + rec2["judgement"]) 

    advice = "结合卦意与现实资源，小步快跑、持续验证；与关键人保持顺畅沟通。"
    return {"summary": summary, "details": details, "advice": advice}

@app.post("/api/divine/line")
def api_divine_line(req: LineRequest) -> Dict[str, Any]:
    """爻辞解读"""
    DB = _load_iching_db()
    rec = DB.get(str(req.code))
    if not rec:
        raise HTTPException(status_code=404, detail="hexagram not found")
    
    lines = rec.get("lines") or []
    text = None
    modern = None
    if 0 <= req.line < len(lines):
        item = lines[req.line]
        if isinstance(item, str):
            text = item
        elif isinstance(item, dict):
            text = item.get("text")
            modern = item.get("modern")
    
    payload = {"text": text or "", "modern": modern}
    
    # LLM 补充
    if req.llm:
        payload["ai"] = f"【AI释义·示例】围绕问题\"{req.question or ''}\"，此爻强调顺势而行，先安其位，再图进取。"
    
    return payload

# ===================== 静态文件服务 =====================

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)