import os
import time
import threading
import pandas as pd
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox

# 导入核心算法模块 (确保 solver.py 就在旁边)
from solver import read_all_kp_instances, plot_scatter, sort_item_sets, solve_dp


class DKP_GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("D{0-1} KP 智能求解系统")
        # 稍微加宽一点窗口，以容纳四个按钮
        self.root.geometry("820x650")

        # 内部状态变量
        self.instances = []
        self.data_files = []
        self.folder_path = r"D:\College\Junior(2)\RG\Project1\0_1kp\Four kinds of D{0-1}KP instances"

        self.create_widgets()
        self.scan_folder()

    def create_widgets(self):
        # 整体的主容器，增加内边距
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=BOTH, expand=YES)

        # --- 顶部标题区 ---
        title_label = ttk.Label(
            main_frame,
            text="D{0-1} Knapsack Problem Solver",
            font=("Consolas", 18, "bold"),
            bootstyle=PRIMARY
        )
        title_label.pack(pady=(0, 20))

        # --- 数据集与实例控制区 (卡片式设计) ---
        control_frame = ttk.Labelframe(main_frame, text=" ⚙️ 数据配置 ", padding=20, bootstyle=INFO)
        control_frame.pack(fill=X, pady=(0, 20))

        # 数据集选择
        ttk.Label(control_frame, text="选择数据集:", font=("Helvetica", 10)).grid(row=0, column=0, sticky=W, pady=10)
        self.file_var = ttk.StringVar()
        self.file_combo = ttk.Combobox(control_frame, textvariable=self.file_var, state="readonly", width=35,
                                       bootstyle=INFO)
        self.file_combo.grid(row=0, column=1, padx=15, pady=10)
        self.file_combo.bind("<<ComboboxSelected>>", self.load_dataset)

        # 实例选择
        ttk.Label(control_frame, text="选择测试实例:", font=("Helvetica", 10)).grid(row=1, column=0, sticky=W, pady=10)
        self.instance_var = ttk.StringVar()
        self.instance_combo = ttk.Combobox(control_frame, textvariable=self.instance_var, state="readonly", width=35,
                                           bootstyle=INFO)
        self.instance_combo.grid(row=1, column=1, padx=15, pady=10)

        # --- 中部按钮操作区 ---
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=X, pady=(0, 20))

        # 散点图按钮 (任务 2)
        ttk.Button(
            btn_frame, text="📊 查看数据散点图", command=self.action_plot, bootstyle=(OUTLINE, PRIMARY)
        ).pack(side=LEFT, padx=(0, 10), ipadx=5, ipady=5)

        # 导出排序结果按钮 (任务 3)
        ttk.Button(
            btn_frame, text="⬇️ 导出排序结果", command=self.action_export_sorted, bootstyle=INFO
        ).pack(side=LEFT, padx=10, ipadx=5, ipady=5)

        # 单实例求解按钮 (任务 4)
        ttk.Button(
            btn_frame, text="求解当前实例", command=self.action_solve_single, bootstyle=SUCCESS
        ).pack(side=LEFT, padx=10, ipadx=5, ipady=5)

        # 批量导出按钮 (任务 5)
        ttk.Button(
            btn_frame, text="一键求解导出 Excel", command=self.action_solve_all, bootstyle=WARNING
        ).pack(side=LEFT, padx=10, ipadx=5, ipady=5)

        # --- 底部控制台日志区 ---
        log_frame = ttk.Labelframe(main_frame, text=" 📝 运行日志 ", padding=15)
        log_frame.pack(fill=BOTH, expand=YES)

        self.log_text = ttk.Text(log_frame, wrap=WORD, state=DISABLED, font=("Consolas", 10))
        self.log_text.pack(fill=BOTH, expand=YES, side=LEFT)

        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview, bootstyle=ROUND)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

    def log(self, message):
        """向日志区追加文本的辅助函数"""
        self.log_text.config(state=NORMAL)
        self.log_text.insert(END, message + "\n")
        self.log_text.see(END)
        self.log_text.config(state=DISABLED)
        # 强制刷新界面，确保日志实时显示
        self.root.update()

    def scan_folder(self):
        """扫描指定文件夹获取数据集"""
        if not os.path.exists(self.folder_path):
            self.log(f"[❌ 错误] 找不到文件夹路径: \n{self.folder_path}")
            return

        self.data_files = [f for f in os.listdir(self.folder_path) if f.endswith('.txt')]
        if self.data_files:
            self.file_combo['values'] = self.data_files
            self.log(f"[系统就绪] 发现 {len(self.data_files)} 个数据集文件。请在上方下拉菜单中选择。")
        else:
            self.log("[!!!警告] 该文件夹下没有找到 .txt 数据文件。")

    def load_dataset(self, event=None):
        """用户在下拉菜单选择文件后触发的解析函数"""
        selected_file = self.file_var.get()
        if not selected_file:
            return

        full_path = os.path.join(self.folder_path, selected_file)
        self.log(f"\n[⏳ 加载] 正在解析 {selected_file} ...")

        self.instances = read_all_kp_instances(full_path)

        if self.instances:
            instance_names = [inst['name'] for inst in self.instances]
            self.instance_combo['values'] = instance_names
            self.instance_combo.current(0)
            self.log(f"[✅ 成功] 共解析出 {len(self.instances)} 个测试实例。")
        else:
            self.instance_combo.set('')
            self.instance_combo['values'] = []
            self.log("[❌ 失败] 解析失败，未找到有效数据。")

    def get_selected_instance(self):
        """安全地获取当前用户选中的测试实例字典"""
        idx = self.instance_combo.current()
        if idx == -1 or not self.instances:
            messagebox.showwarning("提示", "请先选择一个有效的数据集和实例！")
            return None
        return self.instances[idx]

    def action_plot(self):
        """按钮：绘制散点图"""
        inst = self.get_selected_instance()
        if inst:
            self.log(f"[*] 正在生成 {inst['name']} 的散点图...")
            plot_scatter(inst['item_sets'])

    def action_export_sorted(self):
        """按钮事件：完成要求3，按价值重量比非递增排序并导出"""
        inst = self.get_selected_instance()
        if not inst: return

        self.log(f"\n[*] 正在对 {inst['name']} 按第三项价值/重量比进行非递增排序...")

        # 调用 solver.py 里的核心排序算法
        sorted_items = sort_item_sets(inst['item_sets'])

        txt_name = f"{inst['name']}_sorted.txt"
        with open(txt_name, 'w', encoding='utf-8') as f:
            f.write(f"数据集: {self.file_var.get()} | 实例: {inst['name']}\n")
            f.write("排序规则: 按项集第三项的 (价值/重量) 比例非递增排序\n")
            f.write("=" * 65 + "\n")
            f.write(f"{'项集数据 [(v1, w1), (v2, w2), (v3, w3)]':<45} | {'性价比比值 (Ratio)':<15}\n")
            f.write("-" * 65 + "\n")

            for group in sorted_items:
                ratio = group[2][0] / group[2][1] if group[2][1] != 0 else 0
                f.write(f"{str(group):<45} | {ratio:.4f}\n")

        self.log(f"[✅ 保存] 排序结果明细已导出至文件: {txt_name}")

    def action_solve_single(self):
        """按钮：求解单个实例 """
        inst = self.get_selected_instance()
        if not inst: return

        def calculate_task():
            self.log(f"\n[⚡ 求解] 实例: {inst['name']} (背包容量: {inst['capacity']}) ...正在后台狂奔，请稍候！")
            start_time = time.time()

            sorted_items = sort_item_sets(inst['item_sets'])
            max_profit = solve_dp(inst['capacity'], sorted_items)

            time_cost = time.time() - start_time
            self.log(f"[🏆 结果] {inst['name']} 求解完成! 最优价值: {max_profit} | 耗时: {time_cost:.4f} 秒")

            txt_name = f"{inst['name']}_result.txt"
            with open(txt_name, 'w', encoding='utf-8') as f:
                f.write(f"实例名称: {inst['name']}\n最优价值: {max_profit}\n耗时: {time_cost:.4f} 秒\n")
            self.log(f"[💾 保存] 结果已写入文件: {txt_name}")

        # 启动后台线程执行计算，避免卡死界面
        threading.Thread(target=calculate_task, daemon=True).start()

    def action_solve_all(self):
        """按钮：批量求解并导出Excel """
        if not self.instances:
            messagebox.showwarning("提示", "请先加载数据集！")
            return

        dataset_name = self.file_var.get()

        def calculate_all_task():
            self.log("\n[🚀 批量任务] 开始后台求解所有实例，可能会耗时数十秒，请耐心等待...")
            results_list = []

            for inst in self.instances:
                start_time = time.time()
                sorted_items = sort_item_sets(inst['item_sets'])
                max_profit = solve_dp(inst['capacity'], sorted_items)
                time_cost = time.time() - start_time

                results_list.append({
                    'Dataset': dataset_name,
                    'Instance Name': inst['name'],
                    'Capacity': inst['capacity'],
                    'Max Profit': max_profit,
                    'Time Cost (s)': round(time_cost, 4)
                })
                self.log(f"  -> [{inst['name']}] 完成，最优价值: {max_profit} (耗时: {time_cost:.2f}s)")

            excel_name = f"{dataset_name.split('.')[0]}_All_Results.xlsx"
            df = pd.DataFrame(results_list)
            df.to_excel(excel_name, index=False)
            self.log(f"[💾 保存] 批量汇总数据已导出至: {excel_name}")
            messagebox.showinfo("任务完成", f"批量求解完成！\n数据已保存为: {excel_name}")

        # 启动后台线程执行批量计算
        threading.Thread(target=calculate_all_task, daemon=True).start()


if __name__ == "__main__":
    root = ttk.Window(themename="cosmo")
    app = DKP_GUI(root)
    root.mainloop()