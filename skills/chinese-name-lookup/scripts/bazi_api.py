#!/usr/bin/env python3
"""
八字精算 API 调用封装
API: https://api.yuanfenju.com/index.php/v1/Bazi/jingsuan
"""

import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

# 默认 Demo Key (可用于测试)
DEFAULT_API_KEY = "FsF1CsVevk3N17w7oBkSydfSk"
API_URL = "https://api.yuanfenju.com/index.php/v1/Bazi/jingsuan"


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
    use_true_sun: int = 1,  # 1=考虑真太阳时
) -> Dict[str, Any]:
    """
    调用八字精算 API 获取命盘信息
    
    Args:
        name: 姓名
        sex: 性别 (1=男, 0=女)
        year: 出生年 (公历)
        month: 出生月
        day: 出生日
        hour: 出生时 (24小时制)
        minute: 出生分 (默认0)
        province: 省份
        city: 城市
        api_key: API密钥
        use_true_sun: 是否考虑真太阳时 (1=是, 0=否)
    
    Returns:
        API 返回的完整 JSON 数据
        
    Raises:
        Exception: API 调用失败时抛出
    """
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
    
    query_string = "&".join([f"{k}={urllib.parse.quote(str(v))}" 
                              for k, v in params.items()])
    url = f"{API_URL}?{query_string}"
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            
        if data.get("errcode") != 0:
            raise Exception(f"API Error: {data.get('errmsg', 'Unknown error')}")
            
        return data
        
    except urllib.error.URLError as e:
        raise Exception(f"Network Error: {str(e)}")
    except json.JSONDecodeError as e:
        raise Exception(f"JSON Parse Error: {str(e)}")


def parse_bazi_response(api_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    解析八字 API 返回数据，提取关键信息
    
    Returns:
        {
            "birth_chart": "甲辰年 戊辰月 壬辰日 己酉时",
            "sex": "乾造",  # 或 "坤造"
            "wuxing_wangdu": "水旺 木相 金休 土囚 火死",
            "xiyongshen": "金、水",
            "jishen": "木",
            "qiangruo": "八字偏弱",
            "xiyongshen_desc": "身弱，需补助...",
            "wuxing_scores": {
                "金": 75, "木": 16, "水": 118, "火": 36, "土": 139
            },
            "sizhu": {
                "year": {"tg": "甲", "dz": "辰"},
                "month": {"tg": "戊", "dz": "辰"},
                "day": {"tg": "壬", "dz": "辰"},
                "hour": {"tg": "己", "dz": "酉"},
            }
        }
    """
    base = api_data.get("data", {}).get("base_info", {})
    xiyong = base.get("xiyongshen", {})
    sizhu = api_data.get("data", {}).get("sizhu_info", {})
    
    # 解析喜用神 (可能是字符串如"金，水"或对象如{"xiyongshen": "金，水"})
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
        # 如果是字符串格式 "金，水"
        xiyong_str = str(xiyong)
        jishen = ""
        qiangruo = ""
        desc = ""
        scores = {}
    
    # 解析八字四柱
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
    print("测试八字精算 API...")
    
    try:
        # 示例：张三，男，1994年12月3日18:55
        result = call_bazi_api(
            name="张三",
            sex=1,
            year=1994,
            month=12,
            day=3,
            hour=18,
            minute=55,
            province="北京市",
            city="北京",
        )
        
        parsed = parse_bazi_response(result)
        
        print("\n=== 命盘信息 ===")
        print(f"八字：{parsed['birth_chart']}")
        print(f"性别：{parsed['sex']}")
        print(f"五行旺度：{parsed['wuxing_wangdu']}")
        print(f"喜用神：{parsed['xiyongshen']}")
        print(f"忌神：{parsed['jishen']}")
        print(f"八字强弱：{parsed['qiangruo']}")
        print(f"说明：{parsed['xiyongshen_desc']}")
        
        print("\n=== 五行能量 ===")
        scores = parsed.get("wuxing_scores", {})
        for wuxing, score in scores.items():
            print(f"  {wuxing}: {score}")
            
        print("\n=== 四柱 ===")
        for key, val in parsed.get("sizhu", {}).items():
            print(f"  {key}: {val['tg']}{val['dz']}")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    import urllib.parse
    main()
