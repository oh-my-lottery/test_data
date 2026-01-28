import json
import collections
import statistics
import math

from pathlib import Path
REPO_DIR = Path(__file__).resolve().parent.parent
FILE_PATH = REPO_DIR / "data" / "ssq.json"
RECENT_COUNT = 30      # 分析最近多少期的热度

def calculate_ac(numbers):
    """计算AC值 (Arithmetic Complexity)"""
    if len(numbers) < 6: return 0
    diffs = set()
    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            diffs.add(abs(numbers[i] - numbers[j]))
    # AC值 = 差值个数 - (号码个数 - 1)
    return len(diffs) - (len(numbers) - 1)

def get_zone_ratio(numbers):
    """计算三区比"""
    z1 = sum(1 for x in numbers if 1 <= x <= 11)
    z2 = sum(1 for x in numbers if 12 <= x <= 22)
    z3 = sum(1 for x in numbers if 23 <= x <= 33)
    return f"{z1}:{z2}:{z3}"

def analyze_ssq():
    print(f"[*] 正在加载数据文件: {FILE_PATH} ...")
    
    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            # 兼容不同的JSON结构，你的文件主要数据在 'result' 中
            data_list = raw_data.get('result', raw_data)
    except Exception as e:
        print(f"[!] 文件加载失败: {e}")
        return

    # 数据预处理：按期号从小到大排序（历史->最新）
    # 注意：你的文件原始数据可能是倒序的（最新在最前），需要反转
    if data_list and int(data_list[0]['code']) > int(data_list[-1]['code']):
        data_list = data_list[::-1]

    total_periods = len(data_list)
    print(f"[*] 成功加载 {total_periods} 期历史数据。")
    print("-" * 50)

    # --- 核心统计容器 ---
    red_freq = collections.Counter()
    blue_freq = collections.Counter()
    red_omission = {i: 0 for i in range(1, 34)}
    blue_omission = {i: 0 for i in range(1, 17)}
    
    sums = []
    acs = []
    
    # --- 遍历历史数据 ---
    for idx, entry in enumerate(data_list):
        reds = [int(x) for x in entry['red'].split(',')]
        blue = int(entry['blue'])
        
        # 1. 统计频次
        red_freq.update(reds)
        blue_freq.update([blue])
        
        # 2. 计算实时遗漏 (每次出现重置为0，否则+1)
        for r in range(1, 34):
            if r in reds:
                red_omission[r] = 0
            else:
                red_omission[r] += 1
                
        for b in range(1, 17):
            if b == blue:
                blue_omission[b] = 0
            else:
                blue_omission[b] += 1
                
        # 3. 统计形态指标
        current_sum = sum(reds)
        current_ac = calculate_ac(reds)
        sums.append(current_sum)
        acs.append(current_ac)

    # --- 输出分析报告 ---
    
    latest = data_list[-1]
    print(f"\n【最新一期分析】 期号: {latest['code']}")
    print(f"红球: {latest['red']}  |  蓝球: {latest['blue']}")
    print(f"和值: {sum([int(x) for x in latest['red'].split(',')])} (理论均值102)")
    print(f"AC值: {calculate_ac([int(x) for x in latest['red'].split(',')])} (理论均值8)")
    print(f"三区比: {get_zone_ratio([int(x) for x in latest['red'].split(',')])}")

    print("\n" + "="*20 + " 六维统计情报 " + "="*20)

    # 1. 红球遗漏警报 (Cold Numbers)
    print("\n[!] 红球遗漏警报 (当前需关注的冷号):")
    cold_reds = sorted(red_omission.items(), key=lambda x: x[1], reverse=True)[:5]
    for num, om in cold_reds:
        print(f"  号码 {num:02d} : 已遗漏 {om} 期")

    # 2. 红球热度榜 (Hot Numbers)
    print("\n[!] 红球总热度榜 (历史出现最频繁):")
    hot_reds = red_freq.most_common(5)
    for num, count in hot_reds:
        print(f"  号码 {num:02d} : 出现 {count} 次")

    # 3. 蓝球推荐分析
    print("\n[!] 蓝球数据分析:")
    print(f"  当前最冷蓝球: {max(blue_omission, key=blue_omission.get):02d} (遗漏 {max(blue_omission.values())} 期)")
    print(f"  当前最热蓝球: {blue_freq.most_common(1)[0][0]:02d} (出现 {blue_freq.most_common(1)[0][1]} 次)")
    
    # 4. 下期策略建议 (Strategy)
    last_sum = sums[-1]
    avg_sum = statistics.mean(sums)
    print("\n" + "="*20 + " 数学天才的建议 " + "="*20)
    print(f"1. 和值趋势: 上期和值为 {last_sum}。")
    if last_sum > 120:
        print("   -> 建议: 极高值，下期强烈建议关注和值回落 (选小号)。")
    elif last_sum < 80:
        print("   -> 建议: 极低值，下期强烈建议关注和值回升 (选大号)。")
    else:
        print("   -> 建议: 和值处于正常波动范围，可维持现状。")

    print("2. 胆码推荐 (基于遗漏回补率):")
    # 简单的策略：选取遗漏期数在 5-9 期之间的号码，这通常是回补的黄金期
    gold_omission = [k for k, v in red_omission.items() if 5 <= v <= 9]
    print(f"   关注黄金回补号: {[f'{x:02d}' for x in gold_omission]}")

if __name__ == "__main__":
    analyze_ssq()
