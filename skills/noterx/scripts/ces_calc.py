"""
CES 评分计算 — NoteRx 核心算法

CES = 点赞×1 + 收藏×1 + 评论×4 + 转发×4 + 关注×8

参考：小红书官方种草学公式
"""


def calculate_ces(liked_count: int = 0, collected_count: int = 0,
                  comment_count: int = 0, share_count: int = 0,
                  follow_count: int = 0) -> int:
    """
    计算 CES 总分

    Args:
        liked_count: 点赞数
        collected_count: 收藏数
        comment_count: 评论数
        share_count: 分享数
        follow_count: 关注数（极少出现在笔记详情页）

    Returns:
        CES 总分（整数）
    """
    return (liked_count * 1 +
            collected_count * 1 +
            comment_count * 4 +
            share_count * 4 +
            follow_count * 8)


def calculate_ces_breakdown(liked: int, collected: int,
                             commented: int, shared: int,
                             follow: int = 0) -> str:
    """生成 CES 计算说明文字"""
    parts = []
    if liked: parts.append(f"点赞×1 = {liked}")
    if collected: parts.append(f"收藏×1 = {collected}")
    if commented: parts.append(f"评论×4 = {commented}")
    if shared: parts.append(f"分享×4 = {shared}")
    if follow: parts.append(f"关注×8 = {follow}")
    if not parts:
        return "无互动数据"
    return " + ".join(parts) + f" = {calculate_ces(liked, collected, commented, shared, follow)}"


def estimate_views(liked_count: int) -> int:
    """
    基于点赞数估算阅读量（经验公式）

    小红书普通笔记点赞率约 1-5%，头部笔记更低
    用点赞数反推阅读量时，假设点赞率 3%（中性估计）

    这个估算只用于 ER 计算，不用于 CES
    """
    if liked_count <= 0:
        return 0
    return int(liked_count / 0.03)


def judge_er(engagement_rate: float) -> str:
    """
    判断互动率水平

    Args:
        engagement_rate: 0-1 之间的小数（不是百分比）

    Returns:
        评级字符串
    """
    if engagement_rate > 0.10:
        return "🔥 超爆款（ER>10%，极易传播）"
    elif engagement_rate > 0.05:
        return "⭐ 爆款（ER>5%，高于平均水平）"
    elif engagement_rate > 0.03:
        return "✅ 达标（ER>3%，有爆款潜力）"
    elif engagement_rate > 0.01:
        return "⚠️ 偏低（ER 1-3%，需优化）"
    else:
        return "❌ 偏低（ER<1%，内容或赛道问题）"


def predict_viral(ces_score: int, er: float, time_window_hours: float = 2.0) -> dict:
    """
    预测爆款概率（启发式）

    Args:
        ces_score: CES 总分
        er: 互动率（小数，不是百分比）
        time_window_hours: 观察窗口（小时）

    Returns:
        dict with probability, reasoning
    """
    # 基于 CES 和 ER 的简单启发式预测
    if ces_score == 0:
        return {
            "probability": "N/A",
            "reasoning": "暂无互动数据，无法预测",
            "time_to_wait": "发布后48小时看数据",
        }

    # ER > 3% 是爆款临界线
    if er > 0.10:
        prob = "35-50%"
        reason = "互动率极高，内容极具传播潜力"
        wait = "24-48小时"
    elif er > 0.05:
        prob = "20-35%"
        reason = "互动率良好，算法正在放大"
        wait = "48-72小时"
    elif er > 0.03:
        prob = "10-20%"
        reason = "达到爆款临界线，有机会被推荐"
        wait = "3-5天"
    else:
        prob = "5%以下"
        reason = "互动偏低，需优化内容或等待自然增长"
        wait = "7天以上"

    return {
        "probability": prob,
        "reasoning": reason,
        "time_to_wait": wait,
    }


if __name__ == "__main__":
    # 演示
    ces = calculate_ces(liked_count=100, collected_count=50, comment_count=10, share_count=5)
    print(f"CES: {ces}")
    # CES = 100*1 + 50*1 + 10*4 + 5*4 = 210

    views = estimate_views(100)
    er = 100 / views
    print(f"预估阅读量: {views:,}, ER: {er:.2%}")
    # 预估阅读量: 3,333, ER: 3.00%

    print(judge_er(er))
    # ✅ 达标（ER>3%，有爆款潜力）

    v = predict_viral(ces, er)
    print(v)
    # {'probability': '10-20%', 'reasoning': '...', 'time_to_wait': '3-5天'}
