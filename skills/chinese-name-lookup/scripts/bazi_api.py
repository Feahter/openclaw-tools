#!/usr/bin/env python3
"""
八字精算 API 调用封装（带 fallback 机制）
API: https://api.yuanfenju.com/index.php/v1/Bazi/jingsuan
"""

import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

DEFAULT_API_KEY = "YOUR_API_KEY_HERE"  # 用户需要自行配置
API_URL = "https://api.yuanfenju.com/index.php/v1/Bazi/jingsuan"

# Fallback 喜用神配置（API 不可用时使用）
FALLBACK_XIYONGSHEN = {
    "default": ["金", "水"],  # 最常见的喜用神组合
    "male": ["金", "水"],
    "female": ["木", "火"],
}


def call_bazi_api(
    name: str,
    sex: int,  # 1=男, 0=女
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int = 0,
    province: str = "北京市",
    city: str = "北京",
    api_key: str = DEFAULT_API_KEY,
    use_true_sun: int = 1,
) -> Dict[str, Any]:
    """
    调用八字精算 API 获取命盘信息
    
    API 调用失败时返回 fallback 数据，并在返回结果中标记 is_fallback=True
    """
    # 如果是默认 key，尝试调用一次然后直接 fallback
    if api_key == "YOUR_API_KEY_HERE" or api_key == DEFAULT_API_KEY:
        return _fallback_response(sex, reason="API_KEY_NOT_CONFIGURED")
    
    params = {
        "api_key": api_key,
        "name": name,
        "sex": str(sex),
        "type": "1",
        "year": str(year),
        "month": str(month),
        "day": str(day),
        "hours": str(hour),
        "minute": str(minute),
        "zhen": str(use_true_sun),
        "province": province,
        "city": city,
    }
    
    query_string = "&".join([
        f"{k}={urllib.parse.quote(str(v))}" 
        for k, v in params.items()
    ])
    url = f"{API_URL}?{query_string}"
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            
        if data.get("errcode") != 0:
            # API 返回错误，fallback
            return _fallback_response(sex, reason=f"API_ERROR: {data.get('errmsg', 'Unknown')}")
            
        return data
        
    except urllib.error.URLError as e:
        return _fallback_response(sex, reason=f"NETWORK_ERROR: {str(e)}")
    except json.JSONDecodeError as e:
        return _fallback_response(sex, reason=f"JSON_ERROR: {str(e)}")
    except Exception as e:
        return _fallback_response(sex, reason=f"UNKNOWN_ERROR: {str(e)}")


def _fallback_response(sex: int, reason: str = "") -> Dict[str, Any]:
    """
    生成 fallback 响应
    当 API 不可用时，使用默认喜用神
    """
    gender_key = "male" if sex == 1 else "female"
    fallback_xiyong = FALLBACK_XIYONGSHEN.get(gender_key, FALLBACK_XIYONGSHEN["default"])
    
    return {
        "is_fallback": True,
        "fallback_reason": reason,
        "data": {
            "base_info": {
                "sex": "乾造" if sex == 1 else "坤造",
                "name": "",
                "gongli": "",
                "nongli": "",
                "wuxing_wangdu": "（API 未配置，无法分析）",
                "xiyongshen": {
                    "qiangruo": "（API 未配置，无法分析）",
                    "xiyongshen": "、".join(fallback_xiyong),
                    "jishen": "（API 未配置，无法分析）",
                    "xiyongshen_desc": f"【注意】八字喜用神为估算值（{fallback_xiyong}），仅供参考。建议配置真实 API_KEY 获取准确喜用神。",
                    "jin_score": 50,
                    "mu_score": 50,
                    "shui_score": 50,
                    "huo_score": 50,
                    "tu_score": 50,
                }
            },
            "sizhu_info": {
                "year": {"tg": "?", "dz": "?", "wx": "?"},
                "month": {"tg": "?", "dz": "?", "wx": "?"},
                "day": {"tg": "?", "dz": "?", "wx": "?"},
                "hour": {"tg": "?", "dz": "?", "wx": "?"},
            }
        }
    }


def parse_bazi_response(api_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    解析八字 API 返回数据，提取关键信息
    """
    is_fallback = api_data.get("is_fallback", False)
    
    base = api_data.get("data", {}).get("base_info", {})
    xiyong = base.get("xiyongshen", {})
    sizhu = api_data.get("data", {}).get("sizhu_info", {})
    
    # 解析喜用神
    if isinstance(xiyong, dict):
        xiyong_str = xiyong.get("xiyongshen", "")
        jishen = xiyong.get("jishen", "")
        qiangruo = xiyong.get("qiangruo", "")
        desc = xiyong.get("xiyongshen_desc", "")
        scores = {
            "金": xiyong.get("jin_score", 0),
            "木": xiyong.get("mu_score", 0),
            "水": xiyong.get("shui_score", 0),
            "火": xiyong.get("huo_score", 0),
            "土": xiyong.get("tu_score", 0),
        }
    else:
        xiyong_str = str(xiyong) if xiyong else "金、水"
        jishen = ""
        qiangruo = ""
        desc = ""
        scores = {}
    
    # 解析四柱
    sizhu_info = {}
    for key in ["year", "month", "day", "hour"]:
        if key in sizhu:
            sizhu_info[key] = {
                "tg": sizhu[key].get("tg", ""),
                "dz": sizhu[key].get("dz", ""),
                "wx": sizhu[key].get("wx", ""),
            }
    
    # 构建出生时间描述
    year_tg = sizhu_info.get("year", {}).get("tg", "")
    year_dz = sizhu_info.get("year", {}).get("dz", "")
    month_tg = sizhu_info.get("month", {}).get("tg", "")
    month_dz = sizhu_info.get("month", {}).get("dz", "")
    day_tg = sizhu_info.get("day", {}).get("tg", "")
    day_dz = sizhu_info.get("day", {}).get("dz", "")
    hour_tg = sizhu_info.get("hour", {}).get("tg", "")
    hour_dz = sizhu_info.get("hour", {}).get("dz", "")
    
    birth_chart = f"{year_tg}{year_dz}年 {month_tg}{month_dz}月 {day_tg}{day_dz}日 {hour_tg}{hour_dz}时"
    
    return {
        "is_fallback": is_fallback,
        "birth_chart": birth_chart,
        "sex": base.get("sex", ""),
        "wuxing_wangdu": base.get("wuxing_wangdu", ""),
        "xiyongshen": xiyong_str,
        "jishen": jishen,
        "qiangruo": qiangruo,
        "xiyongshen_desc": desc,
        "wuxing_scores": scores,
        "sizhu": sizhu_info,
    }


def main():
    """测试 API 调用"""
    print("=== 测试 API 调用（含 fallback） ===\n")
    
    # 测试1: 默认 key (应触发 fallback)
    print("测试1: 使用默认 KEY (应触发 fallback)")
    result1 = call_bazi_api("张三", 1, 2024, 5, 1, 10)
    print(f"  is_fallback: {result1.get('is_fallback')}")
    print(f"  fallback_reason: {result1.get('fallback_reason')}")
    print()
    
    # 测试2: 解析
    print("测试2: 解析 fallback 响应")
    parsed = parse_bazi_response(result1)
    print(f"  喜用神: {parsed['xiyongshen']}")
    print(f"  描述: {parsed['xiyongshen_desc']}")


if __name__ == "__main__":
    import urllib.parse
    main()
