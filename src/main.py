import os
import time
import pandas as pd
from solver import read_all_kp_instances, plot_scatter, sort_item_sets, solve_dp

def main():
    folder_path = r"D:\College\Junior(2)\RG\Project1\0_1kp\Four kinds of D{0-1}KP instances"

    if not os.path.exists(folder_path):
        print(f"错误：找不到文件夹路径 \n{folder_path}\n请检查路径是否正确。")
        return

    # 1. 自动扫描文件夹下的所有 txt 文件
    print(f"正在扫描目录: {folder_path}")
    data_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]

    if not data_files:
        print("该文件夹下没有找到任何 .txt 数据文件。")
        return

    # 2. 选择要加载的数据集
    print("\n" + "=" * 45)
    print("发现以下数据集文件：")
    for i, file_name in enumerate(data_files):
        print(f" {i + 1}. {file_name}")
    print("=" * 45)

    file_choice = input(f"请选择要加载的数据集序号 (1-{len(data_files)}): ").strip()

    if not (file_choice.isdigit() and 1 <= int(file_choice) <= len(data_files)):
        print("输入无效，程序退出。")
        return

    selected_file = data_files[int(file_choice) - 1]
    full_file_path = os.path.join(folder_path, selected_file)

    # 3. 加载并解析选定的数据文件
    print(f"\n正在解析数据文件: {selected_file} ...")
    instances = read_all_kp_instances(full_file_path)  # 必须确保 read_all_kp_instances 已定义

    if not instances:
        print("未能成功解析任何数据，请检查文件格式。")
        return

    print(f"成功加载！在 {selected_file} 中共发现 {len(instances)} 个测试实例。")

    # 4. 功能交互菜单
    while True:
        print("\n" + "=" * 45)
        print(f"   当前数据集: {selected_file} - 控制台")
        print("=" * 45)
        print(" 1. 查看某个实例的数据散点图")
        print(" 2. 求解指定实例并保存为 TXT")
        print(" 3. 一键求解所有实例并导出 Excel")
        print(" 0. 退出程序 / 重新选择数据集")
        print("=" * 45)

        choice = input("请输入要执行的功能序号 (0-3): ").strip()

        if choice == '0':
            print("退出当前数据集！")
            break

        elif choice == '1':
            idx_str = input(f"请输入要查看的实例编号 (1-{len(instances)}): ")
            if idx_str.isdigit() and 1 <= int(idx_str) <= len(instances):
                idx = int(idx_str) - 1
                plot_scatter(instances[idx]['item_sets'])
            else:
                print("输入无效。")

        elif choice == '2':
            idx_str = input(f"请输入要求解的实例编号 (1-{len(instances)}): ")
            if idx_str.isdigit() and 1 <= int(idx_str) <= len(instances):
                idx = int(idx_str) - 1
                inst = instances[idx]

                print(f"\n正在求解 {inst['name']}...")
                start_time = time.time()

                sorted_items = sort_item_sets(inst['item_sets'])
                max_profit = solve_dp(inst['capacity'], sorted_items)
                time_cost = time.time() - start_time

                print(f"求解完成！最优价值: {max_profit} | 耗时: {time_cost:.4f} 秒")

                # 保存为 txt
                txt_name = f"{inst['name']}_result.txt"
                with open(txt_name, 'w', encoding='utf-8') as f:
                    f.write(
                        f"数据集: {selected_file}\n实例名称: {inst['name']}\n最优价值: {max_profit}\n耗时: {time_cost:.4f} 秒\n")
                print(f"结果已保存至: {txt_name}")
            else:
                print("输入无效。")

        elif choice == '3':
            print("\n正在批量求解，请稍候...")
            results_list = []

            for inst in instances:
                start_time = time.time()
                sorted_items = sort_item_sets(inst['item_sets'])
                max_profit = solve_dp(inst['capacity'], sorted_items)

                results_list.append({
                    'Dataset': selected_file,
                    'Instance Name': inst['name'],
                    'Capacity': inst['capacity'],
                    'Max Profit': max_profit,
                    'Time Cost (s)': round(time.time() - start_time, 4)
                })
                print(f"[{inst['name']}] 完成 -> 最大价值: {max_profit}")

            df = pd.DataFrame(results_list)
            excel_name = f"{selected_file.split('.')[0]}_All_Results.xlsx"
            df.to_excel(excel_name, index=False)
            print(f"\n汇总数据已成功导出至: {excel_name}")

        else:
            print("指令错误，请输入 0-3。")


if __name__ == "__main__":
    main()