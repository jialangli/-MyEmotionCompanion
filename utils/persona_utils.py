import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def load_persona_config():
    """加载人格配置文件"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "persona_config.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        logging.debug(f"成功加载人格配置: {config}")
        return config
    except FileNotFoundError:
        logging.error("人格配置文件未找到，返回默认配置。")
        return {
            "personas": {
                "warm_partner": {
                    "name": "暖心伴侣（女友）",
                    "prompt": "你是用户的专属暖心女友，性格温柔黏人...",
                    "emoji": "💕"
                }
            },
            "default_persona": "warm_partner"
        }

def get_persona_prompt(persona_id):
    """根据人格标识获取对应的system_prompt"""
    config = load_persona_config()
    persona = config["personas"].get(persona_id, config["personas"][config["default_persona"]])
    logging.debug(f"获取人格 {persona_id} 的 system_prompt: {persona['prompt']}")
    return persona["prompt"]

def get_all_personas():
    """获取所有人格列表（供前端展示）"""
    config = load_persona_config()
    personas = []
    for persona_id, info in config["personas"].items():
        personas.append({
            "id": persona_id,
            "name": info["name"],
            "emoji": info["emoji"]
        })
    logging.debug(f"获取所有人格列表: {personas}")
    return personas