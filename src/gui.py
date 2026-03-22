import os
import time
import threading
import pandas as pd
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox

# 导入所有核心功能
from solver import (read_all_kp_instances, plot_scatter, sort_item_sets,
                    solve_dp, solve_greedy, plot_comparison, generate_custom_dataset)


class DKP_GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("D{0-1} KP 智能求解与评测系统")
        self.root.geometry("850x750")

        # --- 初始化目录 ---
        self.folder_path = r"D:\College\Junior(2)\RG\Project1\0_1kp\Four kinds of D{0-1}KP instances"
        self.result_dir = r"D:\College\Junior(2)\RG\Project1\0_1kp\result"

        # 确保 result 文件夹存在，不存在则自动创建
        os.makedirs(self.result_dir, exist_ok=True)

        self.instances = []
        self.data_files = []

        # 创建多标签页 (Tabs)
        self.notebook = ttk.Notebook(self.root, bootstyle=INFO)
        self.notebook.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        self.tab_solver = ttk.Frame(self.notebook, padding=15)
        self.tab_generator = ttk.Frame(self.notebook, padding=15)

        self.notebook.add(self.tab_solver, text=' 🚀 核心求解器 ')
        self.notebook.add(self.tab_generator, text=' 🛠️ 数据集生成器 ')

        self.build_solver_tab()
        self.build_generator_tab()
        self.scan_folder()

    def build_solver_tab(self):
        """构建求解器标签页"""
        control_frame = ttk.Labelframe(self.tab_solver, text=" ⚙️ 数据配置 ", padding=20, bootstyle=INFO)
        control_frame.pack(fill=X, pady=(0, 15))

        ttk.Label(control_frame, text="选择数据集:", font=("Helvetica", 10)).grid(row=0, column=0, sticky=W, pady=5)
        self.file_var = ttk.StringVar()
        self.file_combo = ttk.Combobox(control_frame, textvariable=self.file_var, state="readonly", width=35,
                                       bootstyle=INFO)
        self.file_combo.grid(row=0, column=1, padx=15, pady=5)
        self.file_combo.bind("<<ComboboxSelected>>", self.load_dataset)

        ttk.Label(control_frame, text="选择测试实例:", font=("Helvetica", 10)).grid(row=1, column=0, sticky=W, pady=5)
        self.instance_var = ttk.StringVar()
        self.instance_combo = ttk.Combobox(control_frame, textvariable=self.instance_var, state="readonly", width=35,
                                           bootstyle=INFO)
        self.instance_combo.grid(row=1, column=1, padx=15, pady=5)

        btn_frame = ttk.Frame(self.tab_solver)
        btn_frame.pack(fill=X, pady=(0, 15))

        # 按钮区域
        ttk.Button(btn_frame, text="📊 散点图", command=self.action_plot, bootstyle=(OUTLINE, PRIMARY)).pack(side=LEFT,
                                                                                                            padx=5)
        ttk.Button(btn_frame, text="⬇️ 导出排序", command=self.action_export_sorted, bootstyle=INFO).pack(side=LEFT,
                                                                                                          padx=5)
        ttk.Button(btn_frame, text="DP求解当前实例", command=lambda: self.action_solve_single("DP"), bootstyle=SUCCESS).pack(
            side=LEFT, padx=5)
        ttk.Button(btn_frame, text="贪心求解当前实例", command=lambda: self.action_solve_single("Greedy"),
                   bootstyle=INFO).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="批量对比导出 (含柱状图)", command=self.action_solve_all, bootstyle=WARNING).pack(
            side=LEFT, padx=5)

        # 【拓展4】动态进度条
        self.progress = ttk.Progressbar(self.tab_solver, bootstyle="success-striped", mode='determinate')
        self.progress.pack(fill=X, pady=(0, 15))

        # 日志区
        log_frame = ttk.Labelframe(self.tab_solver, text=" 📝 运行日志 ", padding=15)
        log_frame.pack(fill=BOTH, expand=YES)
        self.log_text = ttk.Text(log_frame, wrap=WORD, state=DISABLED, font=("Consolas", 10))
        self.log_text.pack(fill=BOTH, expand=YES, side=LEFT)
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview, bootstyle=ROUND)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

    def build_generator_tab(self):
        """构建生成器标签页"""
        gen_frame = ttk.Labelframe(self.tab_generator, text=" 【拓展】自定义数据集生成 ", padding=20, bootstyle=PRIMARY)
        gen_frame.pack(fill=BOTH, expand=YES)

        ttk.Label(gen_frame, text="自动生成符合 D{0-1}KP 规则的数据集，并将其保存到结果文件夹中。",
                  foreground="gray").pack(pady=(0, 20))

        input_frame = ttk.Frame(gen_frame)
        input_frame.pack(fill=X)

        ttk.Label(input_frame, text="生成文件名 (.txt):").grid(row=0, column=0, pady=10, sticky=W)
        self.gen_name_var = ttk.StringVar(value="CustomDataset.txt")
        ttk.Entry(input_frame, textvariable=self.gen_name_var, width=30).grid(row=0, column=1, padx=10)

        ttk.Label(input_frame, text="包含实例数量:").grid(row=1, column=0, pady=10, sticky=W)
        self.gen_inst_var = ttk.IntVar(value=5)
        ttk.Entry(input_frame, textvariable=self.gen_inst_var, width=30).grid(row=1, column=1, padx=10)

        ttk.Label(input_frame, text="每个实例物品总数 (需为3的倍数):").grid(row=2, column=0, pady=10, sticky=W)
        self.gen_items_var = ttk.IntVar(value=300)
        ttk.Entry(input_frame, textvariable=self.gen_items_var, width=30).grid(row=2, column=1, padx=10)

        ttk.Button(gen_frame, text="🛠️ 一键生成并保存至 Result 文件夹", command=self.action_generate,
                   bootstyle=SUCCESS).pack(pady=30, ipadx=10, ipady=5)

    def log(self, message):
        self.log_text.config(state=NORMAL)
        self.log_text.insert(END, message + "\n")
        self.log_text.see(END)
        self.log_text.config(state=DISABLED)
        self.root.update()

    def scan_folder(self):
        if not os.path.exists(self.folder_path):
            self.log(f"[❌ 错误] 找不到文件夹路径: \n{self.folder_path}")
            return
        self.data_files = [f for f in os.listdir(self.folder_path) if f.endswith('.txt')]
        if self.data_files:
            self.file_combo['values'] = self.data_files
            self.log(f"[✅ 系统就绪] 发现 {len(self.data_files)} 个数据集文件。输出目录: {self.result_dir}")

    def load_dataset(self, event=None):
        selected_file = self.file_var.get()
        if not selected_file: return
        full_path = os.path.join(self.folder_path, selected_file)
        self.log(f"\n[⏳ 加载] 正在解析 {selected_file} ...")
        self.instances = read_all_kp_instances(full_path)
        if self.instances:
            self.instance_combo['values'] = [inst['name'] for inst in self.instances]
            self.instance_combo.current(0)
            self.log(f"[✅ 成功] 共解析出 {len(self.instances)} 个测试实例。")

    def get_selected_instance(self):
        idx = self.instance_combo.current()
        if idx == -1 or not self.instances:
            messagebox.showwarning("提示", "请先选择数据集和实例！")
            return None
        return self.instances[idx]

    def action_plot(self):
        inst = self.get_selected_instance()
        if inst:
            self.log(f"[*] 正在生成 {inst['name']} 散点图...")
            # 将散点图保存到 result 文件夹
            chart_path = os.path.join(self.result_dir, f"{inst['name']}_scatter.png")
            plot_scatter(inst['item_sets'], save_path=chart_path)

    def action_export_sorted(self):
        inst = self.get_selected_instance()
        if not inst: return
        self.log(f"\n[*] 正在对 {inst['name']} 进行非递增排序...")
        sorted_items = sort_item_sets(inst['item_sets'])

        txt_name = os.path.join(self.result_dir, f"{inst['name']}_sorted.txt")
        with open(txt_name, 'w', encoding='utf-8') as f:
            f.write(f"数据集: {self.file_var.get()} | 实例: {inst['name']}\n")
            f.write("=" * 65 + "\n")
            for group in sorted_items:
                ratio = group[2][0] / group[2][1] if group[2][1] != 0 else 0
                f.write(f"{str(group):<45} | {ratio:.4f}\n")
        self.log(f"[✅ 保存] 排序明细已导出至: {txt_name}")

    def action_solve_single(self, algo_type):
        inst = self.get_selected_instance()
        if not inst: return

        def task():
            self.log(f"\n[⚡ {algo_type} 求解] {inst['name']} (容量: {inst['capacity']})...")
            start = time.time()
            sorted_items = sort_item_sets(inst['item_sets'])

            if algo_type == "DP":
                profit = solve_dp(inst['capacity'], sorted_items)
            else:
                profit = solve_greedy(inst['capacity'], sorted_items)

            cost = time.time() - start
            self.log(f"[🏆 结果] 最优价值: {profit} | 耗时: {cost:.4f} 秒")

            txt_name = os.path.join(self.result_dir, f"{inst['name']}_{algo_type}_result.txt")
            with open(txt_name, 'w', encoding='utf-8') as f:
                f.write(f"算法: {algo_type}\n实例: {inst['name']}\n最优价值: {profit}\n耗时: {cost:.4f} 秒\n")
            self.log(f"[💾 保存] 结果写入: {txt_name}")

        threading.Thread(target=task, daemon=True).start()

    def action_solve_all(self):
        if not self.instances: return
        dataset_name = self.file_var.get()

        def task():
            self.log("\n[🚀 批量任务] 对比 DP 与 Greedy 算法，请稍候...")
            self.progress['maximum'] = len(self.instances)
            self.progress['value'] = 0

            names, dp_t, greedy_t, results = [], [], [], []

            for i, inst in enumerate(self.instances):
                sorted_items = sort_item_sets(inst['item_sets'])

                # 跑贪心
                t0 = time.time()
                greedy_val = solve_greedy(inst['capacity'], sorted_items)
                g_cost = time.time() - t0

                # 跑DP
                t1 = time.time()
                dp_val = solve_dp(inst['capacity'], sorted_items)
                d_cost = time.time() - t1

                names.append(inst['name'])
                dp_t.append(d_cost)
                greedy_t.append(g_cost)

                results.append({
                    'Instance': inst['name'],
                    'DP Profit': dp_val, 'Greedy Profit': greedy_val,
                    'DP Time(s)': round(d_cost, 4), 'Greedy Time(s)': round(g_cost, 4)
                })

                self.log(f"  -> {inst['name']} | DP:{dp_val} ({d_cost:.2f}s) | Greedy:{greedy_val} ({g_cost:.4f}s)")

                # 推进进度条
                self.progress['value'] = i + 1
                self.root.update()

            # 保存 Excel
            excel_name = os.path.join(self.result_dir, f"{dataset_name.split('.')[0]}_Comparison.xlsx")
            df = pd.DataFrame(results)
            df.to_excel(excel_name, index=False)
            self.log(f"\n[💾 保存] 对比Excel已导出至: {excel_name}")

            # 生成并保存柱状图
            chart_path = os.path.join(self.result_dir, f"{dataset_name.split('.')[0]}_Performance_Chart.png")
            # plot_comparison(names, dp_t, greedy_t, save_path=chart_path)
            self.root.after(0, plot_comparison, names, dp_t, greedy_t, chart_path)
            self.log(f"[📊 保存] 性能柱状图已保存至: {chart_path}")

            self.progress['value'] = 0
            messagebox.showinfo("完成", f"批量对比完成！\nExcel与图表已保存至 result 目录。")

        threading.Thread(target=task, daemon=True).start()

    def action_generate(self):
        name = self.gen_name_var.get()
        if not name.endswith('.txt'): name += '.txt'

        # 将生成的数据也放入 result 文件夹中，避免污染原始文件夹
        full_path = os.path.join(self.result_dir, name)

        generate_custom_dataset(full_path, self.gen_inst_var.get(), self.gen_items_var.get())
        messagebox.showinfo("成功", f"自定义数据集已生成！\n保存在: {full_path}")
        self.log(f"[🛠️ 生成] 自定义数据成功生成: {full_path}")


if __name__ == "__main__":
    root = ttk.Window(themename="cosmo")
    app = DKP_GUI(root)
    root.mainloop()