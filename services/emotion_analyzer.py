# services/emotion_analyzer.py - 百度AI情感倾向分析工具
import requests
import json
import time
import os


class BaiduEmotionAnalyzer:
    """百度AI情感倾向分析工具类"""

    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key
        self.access_token = None
        self.token_expire_time = 0  # Token过期时间（时间戳）

    def _get_access_token(self):
        """获取Access Token（内部方法，外部无需调用）"""
        # 百度认证接口地址
        token_url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={self.api_key}&client_secret={self.secret_key}"
        try:
            response = requests.get(token_url, timeout=10)
            response.raise_for_status()  # 抛出HTTP请求异常
            result = response.json()
            if "access_token" in result:
                # 保存Token和过期时间（Token有效期30天，这里提前1天过期，避免失效）
                self.access_token = result["access_token"]
                self.token_expire_time = time.time() + (result["expires_in"] - 86400)
                return self.access_token
            else:
                raise Exception(f"获取Token失败：{result}")
        except Exception as e:
            raise Exception(f"获取Token异常：{str(e)}")

    def analyze_emotion(self, text):
        """
        调用百度AI情感倾向分析接口
        :param text: 用户的消息文本（字符串）
        :return: 情绪分析结果（字典），包含：
            - polarity：情感极性（0：负面，1：中性，2：正面）
            - emotion：情绪标签（如难过、开心、疲惫、焦虑等）
            - confidence：置信度（0-1，越高越准确）
        """
        # 1. 检查Token是否有效，无效则重新获取
        if not self.access_token or time.time() > self.token_expire_time:
            self._get_access_token()

        # 2. 情感分析接口地址
        emotion_url = f"https://aip.baidubce.com/rpc/2.0/nlp/v1/sentiment_classify?access_token={self.access_token}"
        # 3. 构造请求参数（百度接口要求JSON格式）
        data = {
            "text": text,
            "mode": "precise"  # precise模式：返回更细粒度的情绪标签（推荐）
        }
        headers = {
            "Content-Type": "application/json"
        }

        try:
            # 4. 发送请求
            response = requests.post(emotion_url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            result = response.json()

            # 5. 解析结果（处理接口返回的不同情况）
            if "items" in result and len(result["items"]) > 0:
                item = result["items"][0]
                # 提取核心结果
                emotion_result = {
                    "polarity": item.get("sentiment", 1),  # 0负面，1中性，2正面
                    "confidence": item.get("confidence", 0.5),  # 置信度
                    "emotion": item.get("emotion", "neutral")  # 情绪标签
                }
                # 英文情绪标签映射为中文
                emotion_map = {
                    "sad": "难过",
                    "happy": "开心",
                    "angry": "生气",
                    "tired": "疲惫",
                    "anxious": "焦虑",
                    "excited": "兴奋",
                    "scared": "害怕",
                    "hate": "厌恶",
                    "fear": "恐惧",
                    "surprise": "惊讶",
                    "neutral": "中性"
                }
                emotion_result["emotion"] = emotion_map.get(emotion_result["emotion"].lower(), "中性")
                return emotion_result
            else:
                # 无情绪结果时返回中性
                return {
                    "polarity": 1,
                    "confidence": 0.9,
                    "emotion": "中性"
                }
        except Exception as e:
            # 异常时返回中性，避免程序崩溃
            print(f"情感分析接口调用失败：{str(e)}")
            return {
                "polarity": 1,
                "confidence": 0.9,
                "emotion": "中性"
            }


# 快速测试（若直接运行此文件）
if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    try:
        import config
        BAIDU_API_KEY = config.BAIDU_API_KEY
        BAIDU_SECRET_KEY = config.BAIDU_SECRET_KEY
    except ImportError:
        print("无法导入 config 模块")
        sys.exit(1)

    if not BAIDU_API_KEY or not BAIDU_SECRET_KEY:
        print("请在 .env 中配置 BAIDU_API_KEY 和 BAIDU_SECRET_KEY")
    else:
        print("🚀 开始测试情感分析...")
        analyzer = BaiduEmotionAnalyzer(BAIDU_API_KEY, BAIDU_SECRET_KEY)
        test_texts = [
            "我今天被领导骂了，好委屈",
            "我中奖了，超开心",
            "加班到半夜，感觉整个人都空了",
            "今天天气不错"
        ]
        for text in test_texts:
            try:
                result = analyzer.analyze_emotion(text)
                print(f"\n文本：{text}")
                print(f"分析结果：{result}")
            except Exception as e:
                print(f"\n文本：{text}")
                print(f"分析失败：{e}")
