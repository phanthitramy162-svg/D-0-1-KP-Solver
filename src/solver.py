import re
import matplotlib.pyplot as plt
import pandas as pd
from typing import List, Tuple, Dict


def read_all_kp_instances(file_path: str) -> List[Dict]:
    """
    读取包含多个 D{0-1} KP 实例的数据文件，兼容各种格式。
    """
    instances = []

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    names = re.findall(r'([a-zA-Z]+KP\d+):', content, re.IGNORECASE)
    capacities = re.findall(r'cubage.*?(\d+)', content, re.IGNORECASE)

    profits_strs = re.findall(r'profit[s\s\w]*?:\s*([0-9\s,\-]+)', content, re.IGNORECASE)
    weights_strs = re.findall(r'weight[s\s\w]*?:\s*([0-9\s,\-]+)', content, re.IGNORECASE)

    min_len = min(len(capacities), len(profits_strs), len(weights_strs))
    if min_len == 0:
        print(f"数据解析失败! 找到: 容量={len(capacities)}个, 价值={len(profits_strs)}个, 重量={len(weights_strs)}个")
        return instances

    for i in range(min_len):
        capacity = int(capacities[i])
        name = names[i] if i < len(names) else f"Instance_{i + 1}"

        profits = [int(p) for p in re.findall(r'-?\d+', profits_strs[i])]
        weights = [int(w) for w in re.findall(r'-?\d+', weights_strs[i])]

        if len(profits) != len(weights) or len(profits) % 3 != 0:
            print(f"警告: {name} 数据异常! 价值数量:{len(profits)}, 重量数量:{len(weights)}")
            continue

        item_sets = []
        for j in range(0, len(profits), 3):
            item_sets.append([
                (profits[j], weights[j]),
                (profits[j + 1], weights[j + 1]),
                (profits[j + 2], weights[j + 2])
            ])

        instances.append({
            'name': name,
            'capacity': capacity,
            'item_sets': item_sets
        })

    return instances


def plot_scatter(item_sets: List[List[Tuple[int, int]]], save_path: str = None) -> None:

    # 绘制数据集中所有物品重量与价值的散点图。
    weights = []
    values = []

    for group in item_sets:
        for v, w in group:
            values.append(v)
            weights.append(w)

    plt.figure(figsize=(10, 6))
    plt.scatter(weights, values, alpha=0.6, color='b', edgecolors='k')
    plt.title('D{0-1} KP Dataset: Weight vs Profit')
    plt.xlabel('Weight')
    plt.ylabel('Profit')
    plt.grid(True, linestyle='--', alpha=0.7)

    if save_path:
        plt.savefig(save_path)
        print(f"散点图已保存至: {save_path}")
    else:
        plt.show()


def sort_item_sets(item_sets: List[List[Tuple[int, int]]]) -> List[List[Tuple[int, int]]]:
    # 对项集按第三项物品的 价值/重量比 进行非递增排序。

    sorted_sets = sorted(
        item_sets,
        key=lambda group: group[2][0] / group[2][1] if group[2][1] != 0 else 0,
        reverse=True
    )
    return sorted_sets


def solve_dp(capacity: int, item_sets: List[List[Tuple[int, int]]]) -> int:
    # 使用动态规划求解 D{0-1} 背包问题。
    dp = [0] * (capacity + 1)

    for group in item_sets:
        for j in range(capacity, -1, -1):
            max_val = dp[j]
            for v, w in group:
                if j >= w:
                    max_val = max(max_val, dp[j - w] + v)
            dp[j] = max_val

    return dp[capacity]