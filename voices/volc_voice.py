# -*- coding: utf-8 -*-
"""
火山引擎 TTS 音色实现
字节跳动豆包语音合成大模型
"""

import os
import sys
import subprocess
from typing import Optional
from .base_voice import BaseVoice, VoiceConfig


class VolcVoice(BaseVoice):
    """
    火山引擎 TTS 音色
    字节跳动豆包语音合成大模型（需要API密钥）
    """
    
    engine_id = "volc"
    engine_name = "火山引擎 TTS"
    
    # 预定义音色列表
    PRESET_VOICES = {
        "lingcheng": VoiceConfig(
            voice_id="zh_male_jingqiangkanye_emo_v2_mars_bigtts",
            voice_name="火山-温柔女声",
            voice_emoji="🔥",
            description="温柔婉转女声，情感细腻",
            gender="female",
            style="gentle",
            is_emotional=True
        ),
        "xinglin": VoiceConfig(
            voice_id="zh_male_junlangnanyou_emo_v2_mars_bigtts",
            voice_name="火山-成熟男声",
            voice_emoji="🔥",
            description="成熟稳重男声，权威感强",
            gender="male",
            style="mature",
            is_emotional=True
        ),
        "mingxuan": VoiceConfig(
            voice_id="zh_male_jingqiangkanye_emo_v2_mars_bigtts",
            voice_name="火山-暴躁老哥",
            voice_emoji="🔥",
            description="情绪充沛男声，适合吐槽类内容",
            gender="male",
            style="passionate",
            is_emotional=True
        ),
        "yanping": VoiceConfig(
            voice_id="zh_female_tianmeixiaomei_emo_moon_bigtts",
            voice_name="火山-甜美女声",
            voice_emoji="🔥",
            description="甜美可爱女声，适合萌系内容",
            gender="female",
            style="cute",
            is_emotional=True
        ),
        "yuanfeng": VoiceConfig(
            voice_id="zh_male_junlangnanyou_emo_v2_mars_bigtts",
            voice_name="火山-活力少年",
            voice_emoji="🔥",
            description="活力四射少年音，适合运动/游戏内容",
            gender="male",
            style="energetic",
            is_emotional=True
        ),
    }
    
    def __init__(self, voice_key: str = "xinglin"):
        """
        初始化火山引擎音色
        
        Args:
            voice_key: 音色键名
        """
        config = self.PRESET_VOICES.get(voice_key, self.PRESET_VOICES["xinglin"])
        super().__init__(config)
        self.voice_key = voice_key
        self._appid: Optional[str] = None
        self._access_token: Optional[str] = None
    
    def _load_credentials(self) -> bool:
        """加载 API 凭证"""
        try:
            # 尝试从 Streamlit secrets 加载
            import streamlit as st
            self._appid = st.secrets.get("VOLC_APPID", "")
            self._access_token = st.secrets.get("VOLC_ACCESS_TOKEN", "")
        except:
            # 尝试从环境变量加载
            self._appid = os.environ.get("VOLC_APPID", "")
            self._access_token = os.environ.get("VOLC_ACCESS_TOKEN", "")
        
        return bool(self._appid and self._access_token)
    
    def is_available(self) -> bool:
        """检查火山引擎是否可用（需要API密钥）"""
        return self._load_credentials()
    
    async def synthesize(self, text: str, output_path: str, **kwargs) -> bool:
        """
        使用火山引擎合成语音
        
        Args:
            text: 要合成的文本
            output_path: 输出文件路径
            **kwargs:
                timeout: 超时时间（默认60秒）
        
        Returns:
            是否成功
        """
        timeout = kwargs.get('timeout', 60)
        
        # 加载凭证
        if not self._load_credentials():
            print("❌ 火山引擎 API 凭证未配置")
            return False
        
        # 预处理文本
        text = self.preprocess_text(text)
        
        # 官方脚本路径
        script_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "examples", "volcengine", "bidirection.py"
        )
        
        if not os.path.exists(script_path):
            print(f"❌ 找不到火山引擎脚本: {script_path}")
            return False
        
        print(f"🚀 正在调用豆包语音合成: {self.config.voice_name}...")
        
        try:
            # 构建命令
            command = [
                sys.executable,
                script_path,
                "--appid", self._appid,
                "--access_token", self._access_token,
                "--voice_type", self.config.voice_id,
                "--text", text,
                "--encoding", "mp3",
                "--output", output_path
            ]
            
            # 执行脚本
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            # 验证输出
            if self.validate_output(output_path):
                print(f"✅ 豆包音频生成成功: {output_path}")
                return True
            else:
                print(f"❌ 输出文件未生成或为空: {output_path}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"❌ 火山引擎 TTS 超时（{timeout}秒）")
            return False
        except subprocess.CalledProcessError as e:
            print(f"❌ 火山引擎调用失败: {e.stderr}")
            return False
        except Exception as e:
            print(f"❌ 火山引擎异常: {e}")
            return False
    
    @classmethod
    def get_preset_voice(cls, voice_key: str) -> "VolcVoice":
        """获取预设音色实例"""
        return cls(voice_key)
    
    @classmethod
    def list_preset_voices(cls) -> dict:
        """列出所有预设音色"""
        return {
            key: f"{config.voice_emoji} {config.voice_name}"
            for key, config in cls.PRESET_VOICES.items()
        }
