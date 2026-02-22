# -*- coding: utf-8 -*-
"""
Edge TTS 音色实现
微软 Edge 免费 TTS 引擎
"""

import asyncio
import edge_tts
from .base_voice import BaseVoice, VoiceConfig


class EdgeVoice(BaseVoice):
    """
    Edge TTS 音色
    基于微软 Edge 浏览器的免费 TTS 服务
    """
    
    engine_id = "edge"
    engine_name = "Edge TTS"
    
    # 预定义音色列表
    PRESET_VOICES = {
        "yunxi": VoiceConfig(
            voice_id="zh-CN-YunxiNeural",
            voice_name="云希 (抖音热门)",
            voice_emoji="🎙️",
            description="年轻男声，活泼自然，适合大多数内容",
            gender="male",
            style="natural",
            supports_ssml=True
        ),
        "xiaoxiao": VoiceConfig(
            voice_id="zh-CN-XiaoxiaoNeural",
            voice_name="晓晓 (温柔女声)",
            voice_emoji="🎙️",
            description="温柔女声，亲切自然，适合治愈系内容",
            gender="female",
            style="gentle",
            supports_ssml=True
        ),
        "yunye": VoiceConfig(
            voice_id="zh-CN-YunyeNeural",
            voice_name="云野 (磁性男声)",
            voice_emoji="🎙️",
            description="成熟男声，磁性低沉，适合知识类内容",
            gender="male",
            style="mature",
            supports_ssml=True
        ),
        "xiaoyi": VoiceConfig(
            voice_id="zh-CN-XiaoyiNeural",
            voice_name="晓伊 (活泼女声)",
            voice_emoji="🎙️",
            description="活泼女声，轻快明亮，适合娱乐内容",
            gender="female",
            style="lively",
            supports_ssml=True
        ),
    }
    
    def __init__(self, voice_key: str = "yunxi"):
        """
        初始化 Edge TTS 音色
        
        Args:
            voice_key: 音色键名（yunxi/xiaoxiao/yunye/xiaoyi）
        """
        config = self.PRESET_VOICES.get(voice_key, self.PRESET_VOICES["yunxi"])
        super().__init__(config)
        self.voice_key = voice_key
    
    def is_available(self) -> bool:
        """Edge TTS 总是可用（无需API密钥）"""
        return True
    
    async def synthesize(self, text: str, output_path: str, **kwargs) -> bool:
        """
        使用 Edge TTS 合成语音
        
        Args:
            text: 要合成的文本（支持 SSML）
            output_path: 输出文件路径
            **kwargs:
                rate: 语速（如 "+10%", "-5%"）
                volume: 音量
                proxy: 代理地址
        
        Returns:
            是否成功
        """
        rate = kwargs.get('rate', '+10%')
        proxy = kwargs.get('proxy', None)
        
        # 预处理文本
        text = self.preprocess_text(text)
        
        # 重试逻辑
        for attempt in range(3):
            try:
                # 创建 Communicate 对象
                communicate = edge_tts.Communicate(
                    text, 
                    self.config.voice_id, 
                    rate=rate,
                    proxy=proxy
                )
                await communicate.save(output_path)
                
                # 验证输出
                if self.validate_output(output_path):
                    return True
                else:
                    print(f"❌ 音频文件生成失败或为空: {output_path}")
                    return False
                    
            except Exception as e:
                print(f"TTS 尝试 {attempt+1}/3 失败: {e}")
                await asyncio.sleep(2)
        
        print(f"❌ 音频生成失败（3次重试后）: {output_path}")
        return False
    
    @classmethod
    def get_preset_voice(cls, voice_key: str) -> "EdgeVoice":
        """获取预设音色实例"""
        return cls(voice_key)
    
    @classmethod
    def list_preset_voices(cls) -> dict:
        """列出所有预设音色"""
        return {
            key: f"{config.voice_emoji} {config.voice_name}"
            for key, config in cls.PRESET_VOICES.items()
        }
