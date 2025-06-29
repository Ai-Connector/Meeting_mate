import redis
import json
from typing import Dict, Any, Optional, List, Set
import time
import asyncio
import os
from functools import wraps

class CacheManager:
    """会議データに特化したキャッシュ管理クラス"""
    
    def __init__(self, redis_host=None, redis_port=None, redis_db=0):
        """Redisクライアントの初期化"""
        # 環境変数から設定を読み取る
        redis_host = redis_host or os.environ.get('REDIS_HOST', 'localhost')
        redis_port = redis_port or int(os.environ.get('REDIS_PORT', 6379))
        
        # Redisクライアントの初期化（接続エラーに対応）
        try:
            self.redis = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
            self.redis.ping()  # 接続テスト
            self.redis_available = True
            print(f"Redis cache initialized: {redis_host}:{redis_port}")
        except redis.ConnectionError:
            self.redis_available = False
            print(f"Redis connection failed: {redis_host}:{redis_port}")
            print("Running with cache disabled")
        
        # キャッシュのデフォルトTTL（秒）
        self.default_ttl = {
            'meeting': 60,        # 会議データは1分
            'section': 30,        # セクションは30秒
            'item': 15,           # 項目は15秒
            'task': 60,           # タスクは1分
            'template': 3600,     # テンプレートは1時間
            'user': 300           # ユーザー情報は5分
        }
        
        # 依存関係の追跡用ハッシュマップ
        # 例: {'meeting:m1': ['section:s1', 'section:s2', 'task:t1']}
        self.dependency_prefix = 'deps:'
    
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """キャッシュからデータを取得"""
        if not hasattr(self, 'redis_available') or not self.redis_available:
            return None
            
        try:
            data = self.redis.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            print(f"Cache get error: {e}")
        return None
    
    async def set(self, key: str, data: Dict[str, Any], ttl: Optional[int] = None, 
                  entity_type: Optional[str] = None) -> None:
        """データをキャッシュに保存"""
        if not hasattr(self, 'redis_available') or not self.redis_available:
            return
            
        try:
            if entity_type and ttl is None:
                ttl = self.default_ttl.get(entity_type, 60)
                
            self.redis.setex(key, ttl, json.dumps(data))
        except Exception as e:
            print(f"Cache set error: {e}")
    
    async def delete(self, key: str) -> None:
        """キャッシュからデータを削除"""
        if not hasattr(self, 'redis_available') or not self.redis_available:
            return
            
        try:
            self.redis.delete(key)
            
            # 依存関係も削除
            self.redis.delete(f"{self.dependency_prefix}{key}")
        except Exception as e:
            print(f"Cache delete error: {e}")
    
    async def add_dependency(self, parent_key: str, child_key: str) -> None:
        """親キーと子キーの依存関係を追加"""
        if not hasattr(self, 'redis_available') or not self.redis_available:
            return
            
        try:
            self.redis.sadd(f"{self.dependency_prefix}{parent_key}", child_key)
        except Exception as e:
            print(f"Cache add_dependency error: {e}")
    
    async def invalidate_with_dependencies(self, key: str) -> None:
        """キーとその依存関係を無効化"""
        if not hasattr(self, 'redis_available') or not self.redis_available:
            return
            
        try:
            # まず依存関係を取得
            deps_key = f"{self.dependency_prefix}{key}"
            dependencies = self.redis.smembers(deps_key)
            
            # 依存関係を再帰的に無効化
            for dep in dependencies:
                dep_str = dep.decode('utf-8')
                await self.invalidate_with_dependencies(dep_str)
            
            # 最後に自身を無効化
            await self.delete(key)
        except Exception as e:
            print(f"Cache invalidate_with_dependencies error: {e}")
    
    async def get_meeting_with_related(self, meeting_id: str) -> Dict[str, Any]:
        """会議データと関連するセクション、項目を取得（キャッシュ優先）"""
        meeting_key = f"meeting:{meeting_id}"
        
        # 会議データをキャッシュから取得
        meeting = await self.get(meeting_key)
        
        # キャッシュになければ、ここでFirestoreから取得する処理を実装
        # （この例では省略）
        
        # セクションデータを取得
        sections_key = f"sections:{meeting_id}"
        sections = await self.get(sections_key)
        
        # セクションごとに項目を取得
        if sections:
            for section in sections:
                section_id = section['id']
                items_key = f"items:{section_id}"
                items = await self.get(items_key)
                if items:
                    section['items'] = items
        
        # 会議データにセクションを追加
        if meeting and sections:
            meeting['sections'] = sections
            
        return meeting
    
    async def update_meeting(self, meeting_id: str, data: Dict[str, Any]) -> None:
        """会議データを更新し、関連キャッシュを無効化"""
        meeting_key = f"meeting:{meeting_id}"
        
        # 会議データを更新（Firestoreへの更新は別途実装）
        await self.set(meeting_key, data, entity_type='meeting')
        
        # 関連するキャッシュを無効化
        await self.invalidate_with_dependencies(meeting_key)
    
    async def update_section(self, meeting_id: str, section_id: str, data: Dict[str, Any]) -> None:
        """セクションデータを更新し、関連キャッシュを無効化"""
        section_key = f"section:{section_id}"
        
        # セクションデータを更新
        await self.set(section_key, data, entity_type='section')
        
        # セクションリストのキャッシュを無効化
        await self.delete(f"sections:{meeting_id}")
        
        # 会議データの依存関係を更新
        meeting_key = f"meeting:{meeting_id}"
        await self.add_dependency(meeting_key, section_key)
    
    async def update_item(self, section_id: str, item_id: str, data: Dict[str, Any], meeting_id: str) -> None:
        """項目データを更新し、関連キャッシュを無効化"""
        item_key = f"item:{item_id}"
        
        # 項目データを更新
        await self.set(item_key, data, entity_type='item')
        
        # 項目リストのキャッシュを無効化
        await self.delete(f"items:{section_id}")
        
        # セクションの依存関係を更新
        section_key = f"section:{section_id}"
        await self.add_dependency(section_key, item_key)
        
        # 会議データの依存関係も更新
        meeting_key = f"meeting:{meeting_id}"
        await self.add_dependency(meeting_key, section_key)
    
    # キャッシュデコレータ
    def cached(self, entity_type: str, key_prefix: str, key_func=None):
        """関数の結果をキャッシュするデコレータ"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # キー生成関数がなければ、最初の引数をキーとして使用
                if key_func:
                    cache_key = f"{key_prefix}:{key_func(*args, **kwargs)}"
                else:
                    cache_key = f"{key_prefix}:{args[0]}" if args else key_prefix
                
                # キャッシュを確認
                cached_data = await self.get(cache_key)
                if cached_data:
                    return cached_data
                
                # 関数を実行
                result = await func(*args, **kwargs)
                
                # 結果をキャッシュ
                if result:
                    await self.set(cache_key, result, entity_type=entity_type)
                
                return result
            return wrapper
        return decorator

# シングルトンインスタンス
cache_manager = CacheManager()