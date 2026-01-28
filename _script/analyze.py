#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
import json
import collections
from datetime import datetime

from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REPO_DIR = Path(__file__).resolve().parent.parent
SSQ_FILE = REPO_DIR / "data" / "ssq.json"

# 读取双色球数据
with open(SSQ_FILE, "r", encoding="utf-8") as f:
    ssq_data = json.loads(f.read())["result"]

# 处理双色球数据，去除无用信息
ssq_all_data = [ 
    {
        "code": i["code"],
        "date_raw": i["date"],
        "date": (i["date"]).split('(')[0],
        "red": i["red"].split(","),
        "blue": i["blue"]
    } for i in ssq_data
]

# [统计] 双色球总期数
ssq_total = len(ssq_all_data)
logger.info(f"[SSQ] Total = {ssq_total}")

# 输出前10条处理后的双色球数据
# print(json.dumps(ssq_all_data[:3], indent=4, ensure_ascii=False))
last_ssq_1 = ssq_all_data[0]
last_ssq_2 = ssq_all_data[1]
last_ssq_3 = ssq_all_data[2]
logger.info(f"[SSQ] 日期 {last_ssq_1['date']}, 红 {last_ssq_1['red']}, 蓝 {last_ssq_1['blue']}")
logger.info(f"[SSQ] 日期 {last_ssq_2['date']}, 红 {last_ssq_2['red']}, 蓝 {last_ssq_2['blue']}")
logger.info(f"[SSQ] 日期 {last_ssq_3['date']}, 红 {last_ssq_3['red']}, 蓝 {last_ssq_3['blue']}")

# 将双色球红球按区间进行统计 1-11、12-22、23-33
def get_zone_ratio(numbers):
    """计算三区比"""
    z1 = sum(1 for x in numbers if 1 <= x <= 11)
    z2 = sum(1 for x in numbers if 12 <= x <= 22)
    z3 = sum(1 for x in numbers if 23 <= x <= 33)
    return f"{z1}:{z2}:{z3}"

last_zone_ratios = []
for entry in ssq_all_data[:3]:
    reds = [int(x) for x in entry['red']]
    zone_ratio = get_zone_ratio(reds)
    last_zone_ratios.append(zone_ratio)
logger.info(f"[SSQ] 最近3期三区比: {last_zone_ratios}")

def analyze_zone_ratios(data, last_n=3, recent_n=30, top_n=3):
    """Compute latest zone ratios and top distributions with configurable windows."""
    zone_ratio_counter = collections.Counter()
    for entry in data[:recent_n]:
        reds = [int(x) for x in entry['red']]
        zone_ratio = get_zone_ratio(reds)
        zone_ratio_counter[zone_ratio] += 1

    recent_total = sum(zone_ratio_counter.values()) or 1
    top_zone_ratios = []
    for ratio, count in zone_ratio_counter.most_common(top_n):
        percent = (count / recent_total) * 100
        top_zone_ratios.append(f"{ratio}={percent:.1f}%")

    logger.info(f"[SSQ] 最近{recent_n}期三区比分布TOP{top_n}: {', '.join(top_zone_ratios)}")
    return last_zone_ratios, top_zone_ratios

# 最近x期三区比分布分析
analyze_zone_ratios(ssq_all_data, last_n=3, recent_n=10, top_n=3)
analyze_zone_ratios(ssq_all_data, last_n=3, recent_n=20, top_n=3)
analyze_zone_ratios(ssq_all_data, last_n=3, recent_n=30, top_n=3)
analyze_zone_ratios(ssq_all_data, last_n=3, recent_n=40, top_n=3)
analyze_zone_ratios(ssq_all_data, last_n=3, recent_n=50, top_n=3)

# 求每期紅球的和
reds_sums = []
for entry in reversed(ssq_all_data):
    reds = [int(x) for x in entry['red']]
    reds_sum = sum(reds)
    reds_sums.append({
        "date": entry['date'],
        "reds_sum": reds_sum
    })
    
# 將reds_sums做成折綫圖
import matplotlib
import matplotlib.pyplot as plt

def _parse_date_safe(date_str):
    """Try to parse dates into datetime; fallback to None if unsupported."""
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y%m%d"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(date_str)
    except Exception:
        return None

def red_sum_plot(reds_sums, count=100):
    """Plot red sums over time."""
    reds_sums = reds_sums[-count:]
    dates_raw = [item['date'] for item in reds_sums]
    sums = [item['reds_sum'] for item in reds_sums]
    dates_parsed = [_parse_date_safe(d) for d in dates_raw]

    plt.figure(figsize=(12, 6))
    if all(isinstance(d, datetime) for d in dates_parsed):
        plt.plot(dates_parsed, sums, marker='o', linestyle='-', color='b')
        plt.gcf().autofmt_xdate()
    else:
        x = list(range(len(sums)))
        plt.plot(x, sums, marker='o', linestyle='-', color='b')
        step = max(1, len(x) // 15)
        plt.xticks(x[::step], dates_raw[::step], rotation=45, ha='right')

    plt.tight_layout()

    # 保存并尝试展示
    output_png = REPO_DIR / f"reds_sum_{count}.png"
    plt.savefig(output_png, dpi=150)
    logger.info(f"[SSQ] 红球和值 {count}期 折线图已保存: {output_png}")

# 生成红球和值折线图
# red_sum_plot(reds_sums, count=50)
# red_sum_plot(reds_sums, count=100)

# 篮球概率分析
# all_blues = [{"code": entry['code'], "blue": int(entry['blue'])} for entry in ssq_all_data]
# analyze_blue = []
# for idx,val in enumerate(all_blues):
#     # 統計val 在接下來10期出現的次數
#     blue = val['blue']
#     before_10 = [i['blue'] for i in all_blues[idx:idx+10] ]
#     count_before_10 = before_10.count(blue)
#     logger.info(f"[SSQ] 篮球 {blue} {before_10} 在前10期出現次數: {count_before_10}")
#     analyze_blue.append( val | {"count_before_10": count_before_10})
#     if idx >= 1000:
#         break


# 将篮球出现次数做成统计图
def blue_count_plot(analyze_blue):
    """Plot blue ball occurrence counts."""
    blues = [item['blue'] for item in analyze_blue]
    counts = [item['count_before_10'] for item in analyze_blue]

    plt.figure(figsize=(12, 6))
    x = list(range(len(blues)))
    plt.bar(x, counts, color='g')

    step = max(1, len(x) // 15)
    plt.xticks(x[::step], blues[::step], rotation=45, ha='right')
    plt.xlabel('Blue Ball Number')
    plt.ylabel('Occurrences in Next 10 Draws')
    plt.title('Blue Ball Occurrence Counts in Next 10 Draws')

    plt.tight_layout()

    # 保存并尝试展示
    output_png = REPO_DIR / f"blue_count.png"
    plt.savefig(output_png, dpi=150)
    logger.info(f"[SSQ] 篮球出现次数统计图已保存: {output_png}")

# blue_count_plot(analyze_blue)

# 统计篮球在最近10期，出现次数大于3的
# lg_2 = []
# for i in analyze_blue:
#     if i['count_before_10'] > 3:
#         lg_2.append(i)
#         logger.info(f"[SSQ] 篮球 {i['blue']}")
# logger.info(f"[SSQ] 篮球在最近10期出现次数大于3的数据 {[ i['blue'] for i in lg_2 ] }")

# # 統計lg_2中篮球出现次数的分布
# result = {}
# for item in lg_2:
#     blue = item["blue"]
#     count = item["count_before_10"]
#     result[blue] = result.get(blue, 0) + count
# print(f"[SSQ] 篮球在前10期出现次数大于2的分布 {result}")

# 红球分析。分析每期红球在上一期红球中出现的个数
red_in_previous_count = []
all_reds = [ {"code": entry['code'], "red": [int(x) for x in entry['red']]} for entry in ssq_all_data ]
all_reds2 = all_reds[:100]

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

for idx,val in enumerate(all_reds2):
    _x = prev_two_hit_rate(val['red'], all_reds2[idx+1]['red'], all_reds2[idx+2]['red'])
    print(_x)