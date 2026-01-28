import json
import collections

from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
SSQ_FILE = REPO_DIR / "data" / "ssq.json"

# 读取双色球数据
with open(SSQ_FILE, "r", encoding="utf-8") as f:
    ssq_data = json.loads(f.read())["result"]

# 处理双色球数据，去除无用信息
history_data = [
    {
        "code": i["code"],
        "date_raw": i["date"],
        "date": (i["date"]).split('(')[0],
        "red": [int(x) for x in i["red"].split(",")],
        "blue": int(i["blue"]) if isinstance(i["blue"], str) else i["blue"]
    } for i in ssq_data
]

def calculate_score():
    scores = {i: 0 for i in range(1, 34)}
    
    # --- 1. 频次权重 (Frequency) ---
    # 近7期热号，惯性很大，给予基础分
    all_reds = []
    for h in history_data:
        all_reds.extend(h['red'])
    freq = collections.Counter(all_reds)
    
    for num, count in freq.items():
        scores[num] += count * 2  # 出现一次加2分

    # --- 2. 邻号引力 (Neighbor Gravity) ---
    # 上一期(2026007)是: 09, 13, 19, 27, 29, 30
    # 它们的邻居(±1)有大概率被拉动
    last_reds = history_data[0]['red']
    for val in last_reds:
        # 左邻
        if val - 1 >= 1: scores[val - 1] += 3
        # 右邻
        if val + 1 <= 33: scores[val + 1] += 3

    # --- 3. 遗漏值补偿 (Omission Recovery) ---
    # 寻找那是“蓄力已久”的号码（遗漏5-10期）
    # 简单计算遗漏
    omission = {i: 0 for i in range(1, 34)}
    for i in range(1, 34):
        is_missing = True
        for h in history_data:
            if i in h['red']:
                is_missing = False
                break
            omission[i] += 1
    
    for num, om in omission.items():
        if 5 <= om <= 9:
            scores[num] += 4  # 黄金回补期，加4分
        elif om > 15:
            scores[num] += 1  # 极冷号，加分少（风险大）

    return scores, freq, omission

scores, freq, omission = calculate_score()

# 排序输出前15名
sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

print("【双色球智能评分模型 V2.0】")
print("-" * 30)
print("Top 10 高分红球 (推荐重点关注):")
for rank, (num, score) in enumerate(sorted_scores[:10], 1):
    status = "热" if freq[num] >= 2 else "冷"
    print(f"第{rank}名: 号码 {num:02d} (得分: {score}) - [{status}]")

print("\n【杀号建议】 (得分最低的号码，建议排除):")
print([f"{x[0]:02d}" for x in sorted_scores[-5:]])
