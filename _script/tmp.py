# 双色球数据
data = [
    {"code": "2026010", "red": [4, 9, 10, 15, 19, 26]},
    {"code": "2026009", "red": [3, 6, 13, 19, 23, 25]},
    {"code": "2026008", "red": [6, 9, 16, 27, 31, 33]},
]

def prev_two_hit_rate(current_red, prev_1, prev_2):
    """
    计算前两期红球在当前期中的出现情况

    :param current_red: list[int]，当前期红球
    :param prev_1: list[int]，前一期红球
    :param prev_2: list[int]，前两期红球
    :return: dict，统计结果
    """
    current_set = set(current_red)
    prev_two = set(prev_1) | set(prev_2)
    hit = current_set & prev_two

    return {
        "prev_two_red": sorted(prev_two),
        "hit_red": sorted(hit),
        "hit_count": len(hit),
        "hit_ratio": round(len(hit) / len(prev_two), 3) if prev_two else 0
    }


result = prev_two_hit_rate(data[0]['red'], data[1]['red'], data[2]['red'])
print("前两期红球在当前期中的出现情况：", result)