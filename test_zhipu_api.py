"""
快速测试智谱 API 是否正常
"""
import requests
import json

# 从 secrets.toml 读取 Key
ZHIPU_KEY = "9c7b05f88af8490989a35d414afec67f.WARkS7yF58ZeYuAB"

url = "https://open.bigmodel.cn/api/paas/v4/images/generations"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {ZHIPU_KEY}"
}

payload = {
    "model": "cogview-3-plus",
    "prompt": "A beautiful sunset over the ocean, cinematic lighting, 4k quality",
    "size": "1024x1920"  # 修复：改为16的整数倍
}

print("🧪 正在测试智谱 CogView-3-Plus API...")
print(f"📡 URL: {url}")
print(f"🔑 Key: {ZHIPU_KEY[:20]}...{ZHIPU_KEY[-10:]}")
print(f"📝 Prompt: {payload['prompt']}")
print()

try:
    response = requests.post(url, json=payload, headers=headers, timeout=60)
    print(f"📊 HTTP状态码: {response.status_code}")
    print()
    
    result = response.json()
    print("📄 完整响应:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print()
    
    if 'data' in result:
        print("✅ API调用成功！")
        print(f"🖼️ 图片URL: {result['data'][0]['url']}")
    else:
        print("❌ API返回错误")
        if 'error' in result:
            print(f"错误信息: {result['error']}")
            
except Exception as e:
    print(f"❌ 请求异常: {e}")
