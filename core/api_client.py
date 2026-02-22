# -*- coding: utf-8 -*-
"""
API 客户端模块 - 面向对象的 API 调用封装
"""

import requests
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class APIResponse:
    """API 响应数据类"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    raw_response: Optional[Dict] = None


class APIClient(ABC):
    """
    API 客户端基类
    所有具体 API 客户端必须继承此类
    """
    
    def __init__(self, api_key: str, base_url: str):
        self._api_key = api_key
        self._base_url = base_url
        self._session = requests.Session()
    
    @abstractmethod
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        pass
    
    def _post(self, endpoint: str, payload: Dict, timeout: int = 60) -> APIResponse:
        """发送 POST 请求"""
        url = f"{self._base_url}/{endpoint}"
        try:
            response = self._session.post(
                url,
                json=payload,
                headers=self._get_headers(),
                timeout=timeout
            )
            response.raise_for_status()
            data = response.json()
            return APIResponse(success=True, data=data, raw_response=data)
        except requests.exceptions.RequestException as e:
            return APIResponse(success=False, error=str(e))
        except json.JSONDecodeError as e:
            return APIResponse(success=False, error=f"JSON解析错误: {e}")
    
    def _get(self, endpoint: str, params: Dict = None, timeout: int = 30) -> APIResponse:
        """发送 GET 请求"""
        url = f"{self._base_url}/{endpoint}"
        try:
            response = self._session.get(
                url,
                params=params,
                headers=self._get_headers(),
                timeout=timeout
            )
            response.raise_for_status()
            data = response.json()
            return APIResponse(success=True, data=data, raw_response=data)
        except requests.exceptions.RequestException as e:
            return APIResponse(success=False, error=str(e))


class DeepSeekClient(APIClient):
    """
    DeepSeek API 客户端
    用于剧本生成、文本优化
    """
    
    def __init__(self, api_key: str):
        super().__init__(api_key, "https://api.deepseek.com/v1")
    
    def _get_headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}"
        }
    
    def generate_script(self, topic: str, style_prompt: str, 
                        temperature: float = 0.7) -> APIResponse:
        """生成剧本"""
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": style_prompt},
                {"role": "user", "content": f"主题：{topic}"}
            ],
            "temperature": temperature,
            "response_format": {"type": "json_object"}
        }
        return self._post("chat/completions", payload)
    
    def refine_script(self, current_script: str, feedback: str) -> APIResponse:
        """优化剧本"""
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你是一位专业的剧本编辑，根据用户反馈优化剧本。"},
                {"role": "user", "content": f"当前剧本：{current_script}\n\n用户反馈：{feedback}"}
            ],
            "temperature": 0.7
        }
        return self._post("chat/completions", payload)
    
    def generate_visual_anchor(self, topic: str, style: str) -> APIResponse:
        """生成视觉锚点"""
        prompt = f"""基于主题"{topic}"和风格"{style}"，定义一个视觉锚点。

请输出JSON格式：
{{
  "anchor_description": "详细的主角特征描述（中文，50字以内）",
  "character_type": "person/product/scene",
  "key_features": ["特征1", "特征2", "特征3"],
  "english_description": "英文描述，用于image_prompt开头"
}}"""
        
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "response_format": {"type": "json_object"}
        }
        return self._post("chat/completions", payload)


class ZhipuClient(APIClient):
    """
    智谱 AI API 客户端
    用于图片/视频生成
    """
    
    def __init__(self, api_key: str):
        super().__init__(api_key, "https://open.bigmodel.cn/api/paas/v4")
    
    def _get_headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}"
        }
    
    def generate_image(self, prompt: str, size: str = "1024x1920") -> APIResponse:
        """生成图片（CogView-3-Plus）"""
        payload = {
            "model": "cogview-3-plus",
            "prompt": prompt,
            "size": size
        }
        return self._post("images/generations", payload, timeout=60)
    
    def generate_video(self, prompt: str) -> APIResponse:
        """生成视频（CogVideoX-3）"""
        payload = {
            "model": "cogvideox-3",
            "prompt": prompt
        }
        return self._post("videos/generations", payload, timeout=120)
    
    def batch_generate_images(self, prompts: List[str], 
                              size: str = "1024x1920") -> List[APIResponse]:
        """批量生成图片"""
        results = []
        for prompt in prompts:
            result = self.generate_image(prompt, size)
            results.append(result)
        return results


class TianapiClient(APIClient):
    """
    天行数据 API 客户端
    用于获取热点数据
    """
    
    def __init__(self, api_key: str):
        super().__init__(api_key, "https://apis.tianapi.com")
    
    def _get_headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/x-www-form-urlencoded"
        }
    
    def get_douyin_hot(self) -> APIResponse:
        """获取抖音热搜榜"""
        try:
            response = self._session.post(
                f"{self._base_url}/douyinhot/index",
                data={"key": self._api_key},
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("code") == 200:
                topics = [item["word"] for item in data["result"]["list"][:10]]
                return APIResponse(success=True, data=topics)
            else:
                return APIResponse(success=False, error=data.get("msg", "未知错误"))
        except Exception as e:
            return APIResponse(success=False, error=str(e))
    
    def get_weibo_hot(self) -> APIResponse:
        """获取微博热搜榜"""
        try:
            response = self._session.post(
                f"{self._base_url}/weibohot/index",
                data={"key": self._api_key},
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("code") == 200:
                topics = [item["word"] for item in data["result"]["list"][:10]]
                return APIResponse(success=True, data=topics)
            else:
                return APIResponse(success=False, error=data.get("msg", "未知错误"))
        except Exception as e:
            return APIResponse(success=False, error=str(e))


class PexelsClient:
    """
    Pexels API 客户端
    用于获取免费视频素材
    """
    
    def __init__(self, api_key: str):
        self._api_key = api_key
        self._base_url = "https://api.pexels.com"
        self._session = requests.Session()
    
    def search_videos(self, query: str, per_page: int = 5, 
                      orientation: str = "portrait") -> APIResponse:
        """搜索视频"""
        headers = {"Authorization": self._api_key}
        params = {
            "query": query,
            "per_page": per_page,
            "orientation": orientation
        }
        
        try:
            response = self._session.get(
                f"{self._base_url}/videos/search",
                headers=headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return APIResponse(success=True, data=data.get("videos", []))
        except Exception as e:
            return APIResponse(success=False, error=str(e))
