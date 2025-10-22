from http.server import BaseHTTPRequestHandler
import json
import os
from urllib import request as _urlreq

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
                self.send_error_response("Invalid JSON format")
                return
            
            # 获取参数
            question = data.get('question', '')
            hexagram = data.get('hexagram', {})
            model = data.get('model', 'Qwen/QwQ-32B')
            
            if not question or not hexagram:
                self.send_error_response("Missing required parameters")
                return
            
            # 构建AI请求
            api_key = os.environ.get('SILICONFLOW_API_KEY')
            if not api_key:
                self.send_error_response("AI service not configured")
                return
            
            # 构建提示词
            hex_name = hexagram.get('name', '未知')
            hex_code = hexagram.get('code', 0)
            lines = hexagram.get('lines', [])
            
            prompt = f"""作为一位资深的易经大师，请为以下占卜结果提供详细解读：

问题：{question}
卦象：{hex_name}（第{hex_code}卦）
爻线：{lines}

请从以下几个方面进行解读：
1. 卦象含义和象征
2. 针对问题的具体指导
3. 当前形势分析
4. 行动建议
5. 注意事项

请用通俗易懂的语言，结合现代生活实际情况进行解读。"""

            # 调用AI服务
            try:
                ai_response = self.call_ai_service(api_key, model, prompt)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
                
                result = {
                    "question": question,
                    "hexagram": hex_name,
                    "interpretation": ai_response,
                    "model": model
                }
                
                response = json.dumps(result, ensure_ascii=False)
                self.wfile.write(response.encode('utf-8'))
                
            except Exception as e:
                self.send_error_response(f"AI service error: {str(e)}")
                
        except Exception as e:
            self.send_error_response(f"Server error: {str(e)}")
    
    def call_ai_service(self, api_key: str, model: str, prompt: str) -> str:
        """调用硅基流动AI服务"""
        url = "https://api.siliconflow.cn/v1/chat/completions"
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位精通易经的大师，能够为用户提供准确、有用的占卜解读。"
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.7
        }
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        req = _urlreq.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        with _urlreq.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result['choices'][0]['message']['content']
    
    def send_error_response(self, message: str):
        """发送错误响应"""
        self.send_response(500)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        error_response = json.dumps({"error": message}, ensure_ascii=False)
        self.wfile.write(error_response.encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()