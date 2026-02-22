# -*- coding: utf-8 -*-
"""
剧本模块 - 面向对象架构
包含剧本版本、剧本管理器
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
import json
import sqlite3


@dataclass
class Scene:
    """分镜场景"""
    scene_number: int
    content: str
    image_prompt: str = ""
    image_path: str = ""
    audio_path: str = ""
    duration: float = 5.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'scene_number': self.scene_number,
            'content': self.content,
            'image_prompt': self.image_prompt,
            'image_path': self.image_path,
            'audio_path': self.audio_path,
            'duration': self.duration
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Scene':
        return cls(
            scene_number=data.get('scene_number', 0),
            content=data.get('content', ''),
            image_prompt=data.get('image_prompt', ''),
            image_path=data.get('image_path', ''),
            audio_path=data.get('audio_path', ''),
            duration=data.get('duration', 5.0)
        )


@dataclass
class ScriptVersion:
    """剧本版本"""
    user_id: str
    version_name: str
    topic: str = ""
    style_id: str = ""
    voice_id: str = ""
    scenes: List[Scene] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    id: Optional[int] = None
    is_locked: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'version_name': self.version_name,
            'topic': self.topic,
            'style_id': self.style_id,
            'voice_id': self.voice_id,
            'scenes': [s.to_dict() for s in self.scenes],
            'created_at': self.created_at,
            'is_locked': self.is_locked
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ScriptVersion':
        scenes = [Scene.from_dict(s) for s in data.get('scenes', [])]
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id', ''),
            version_name=data.get('version_name', ''),
            topic=data.get('topic', ''),
            style_id=data.get('style_id', ''),
            voice_id=data.get('voice_id', ''),
            scenes=scenes,
            created_at=data.get('created_at', datetime.now().isoformat()),
            is_locked=data.get('is_locked', False)
        )
    
    def get_total_duration(self) -> float:
        """获取总时长"""
        return sum(scene.duration for scene in self.scenes)
    
    def get_word_count(self) -> int:
        """获取总字数"""
        return sum(len(scene.content) for scene in self.scenes)


class ScriptManager:
    """
    剧本管理器
    负责剧本版本的CRUD操作
    """
    
    def __init__(self, db_connection: sqlite3.Connection = None, db_path: str = "app_data.db"):
        self._db_path = db_path
        self._connection = db_connection
        self._init_table()
    
    def _get_connection(self):
        """获取数据库连接"""
        if self._connection:
            return self._connection
        return sqlite3.connect(self._db_path)
    
    def _init_table(self):
        """初始化剧本版本表"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS script_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    version_name TEXT NOT NULL,
                    topic TEXT,
                    style_id TEXT,
                    voice_id TEXT,
                    scenes_data TEXT,  -- JSON格式存储
                    is_locked BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
    
    def save_version(self, version: ScriptVersion) -> ScriptVersion:
        """保存剧本版本"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if version.id:
                # 更新
                cursor.execute('''
                    UPDATE script_versions SET
                        version_name=?,
                        topic=?,
                        style_id=?,
                        voice_id=?,
                        scenes_data=?,
                        is_locked=?
                    WHERE id=?
                ''', (
                    version.version_name,
                    version.topic,
                    version.style_id,
                    version.voice_id,
                    json.dumps([s.to_dict() for s in version.scenes], ensure_ascii=False),
                    version.is_locked,
                    version.id
                ))
            else:
                # 插入
                cursor.execute('''
                    INSERT INTO script_versions
                    (user_id, version_name, topic, style_id, voice_id, scenes_data, is_locked)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    version.user_id,
                    version.version_name,
                    version.topic,
                    version.style_id,
                    version.voice_id,
                    json.dumps([s.to_dict() for s in version.scenes], ensure_ascii=False),
                    version.is_locked
                ))
                version.id = cursor.lastrowid
            
            conn.commit()
            return version
    
    def get_user_versions(self, user_id: str) -> List[ScriptVersion]:
        """获取用户的所有剧本版本"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, user_id, version_name, topic, style_id, voice_id, scenes_data, is_locked, created_at
                FROM script_versions
                WHERE user_id = ?
                ORDER BY created_at DESC
            ''', (user_id,))
            
            versions = []
            for row in cursor.fetchall():
                scenes_data = json.loads(row[6]) if row[6] else []
                version = ScriptVersion(
                    id=row[0],
                    user_id=row[1],
                    version_name=row[2],
                    topic=row[3] or '',
                    style_id=row[4] or '',
                    voice_id=row[5] or '',
                    scenes=[Scene.from_dict(s) for s in scenes_data],
                    created_at=row[8],
                    is_locked=bool(row[7])
                )
                versions.append(version)
            
            return versions
    
    def get_version(self, version_id: int) -> Optional[ScriptVersion]:
        """获取指定版本"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, user_id, version_name, topic, style_id, voice_id, scenes_data, is_locked, created_at
                FROM script_versions
                WHERE id = ?
            ''', (version_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            scenes_data = json.loads(row[6]) if row[6] else []
            return ScriptVersion(
                id=row[0],
                user_id=row[1],
                version_name=row[2],
                topic=row[3] or '',
                style_id=row[4] or '',
                voice_id=row[5] or '',
                scenes=[Scene.from_dict(s) for s in scenes_data],
                created_at=row[8],
                is_locked=bool(row[7])
            )
    
    def delete_version(self, version_id: int) -> bool:
        """删除剧本版本"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM script_versions WHERE id=?", (version_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def lock_version(self, version_id: int) -> bool:
        """锁定剧本版本"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE script_versions SET is_locked=1 WHERE id=?",
                (version_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
