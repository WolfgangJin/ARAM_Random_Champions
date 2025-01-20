import os
import random
import requests
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk


# 获取最新版本号
def get_latest_version():
    try:
        response = requests.get("https://ddragon.leagueoflegends.com/api/versions.json")
        response.raise_for_status()
        versions = response.json()
        return versions[0]  # 最新版本号
    except requests.RequestException as e:
        print(f"Error fetching versions: {e}")
        return None


# 获取英雄数据
def get_champion_data(version):
    url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        champions = data["data"]
        return {name: champ["id"] for name, champ in champions.items()}
    except requests.RequestException as e:
        print(f"Error fetching champion data: {e}")
        return {}


# 下载图标
def download_icon(champion_id, version):
    base_url = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/champion/"
    icon_url = f"{base_url}{champion_id}.png"
    file_path = f"icons/{champion_id}.png"

    if not os.path.exists(file_path):  # 避免重复下载
        try:
            response = requests.get(icon_url, stream=True)
            response.raise_for_status()
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
        except requests.RequestException as e:
            print(f"Failed to download icon for {champion_id}: {e}")
            return None
    return file_path


# 缓存所有图标并更新进度条
def cache_icons():
    global champions, version
    version = get_latest_version()
    if not version:
        progress_label.config(text="Failed to fetch latest version.")
        return

    champions = get_champion_data(version)
    if not champions:
        progress_label.config(text="Failed to fetch champion data.")
        return

    total_champions = len(champions)
    champion_count_label.config(text=f"当前版本全英雄数量为: {total_champions}")
    progress_bar["maximum"] = total_champions
    count = 0

    for name, champ_id in champions.items():
        download_icon(champ_id, version)
        count += 1
        progress_bar["value"] = count
        progress_label.config(text=f"首次使用正在缓存英雄图标~未响应也请耐心等待喵~(约2~3分钟): {count}/{total_champions}")
        root.update_idletasks()

    progress_label.config(text="图标缓存完成喵!")
    start_button.config(state="normal")  # 启用功能按钮


# 随机选择英雄
def select_random_champions(champions, count):
    return random.sample(list(champions.items()), count)


# 动态调整布局并显示图标，每行固定显示10个英雄
def display_champions(selected):
    for widget in canvas_frame.winfo_children():
        widget.destroy()

    max_icons_per_row = 10  # 每行显示的最大图标数量
    row, col = 0, 0

    for name, champ_id in selected:
        icon_path = f"icons/{champ_id}.png"
        if icon_path and os.path.exists(icon_path):
            img = Image.open(icon_path).resize((64, 64))
            photo = ImageTk.PhotoImage(img)
            label = tk.Label(canvas_frame, image=photo, text=name, compound="top")
            label.image = photo
            label.grid(row=row, column=col, padx=10, pady=10)

        col += 1
        if col >= max_icons_per_row:  # 换行逻辑：每10个图标强制换行
            col = 0
            row += 1

    # 更新滚动区域
    canvas.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))


# 按钮事件：随机选择
def on_select():
    try:
        count = int(entry.get())
        if count > len(champions):
            messagebox.showwarning("Warning", "Number exceeds total champions!")
        else:
            selected = select_random_champions(champions, count)
            display_champions(selected)
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number.")


# 按钮事件：显示所有英雄
def show_all_champions():
    display_champions(list(champions.items()))


# 初始化目录
if not os.path.exists("icons"):
    os.makedirs("icons")

# 初始化主窗口
root = tk.Tk()
root.title("大乱斗比赛专用随机选择器--By南京大学电竞社NJU丶黑喵喵")
root.geometry("1260x800")

# 设置窗口图标
icon_path = "D:/ARAM/gwenicon.png"  # 图标路径
if os.path.exists(icon_path):
    icon_image = ImageTk.PhotoImage(file=icon_path)
    root.iconphoto(True, icon_image)
else:
    print(f"图标文件未找到: {icon_path}")

# 顶部进度条与状态显示
progress_label = tk.Label(root, text="初始化中喵...")
progress_label.pack(pady=10)
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=10)

champion_count_label = tk.Label(root, text="Total Champions: 0")
champion_count_label.pack(pady=10)

# 缓存完成后启用的功能按钮
start_button = tk.Button(root, text="战斗，爽！", state="disabled", command=lambda: start_selection())
start_button.pack(pady=10)

# 主功能区
top_frame = tk.Frame(root)

# 创建滚动区域
canvas = tk.Canvas(root)
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
canvas_frame = tk.Frame(canvas)

canvas.create_window((0, 0), window=canvas_frame, anchor="nw")
canvas.config(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")


def configure_scroll_region(event):
    canvas.configure(scrollregion=canvas.bbox("all"))


canvas_frame.bind("<Configure>", configure_scroll_region)


# 开始选择英雄
def start_selection():
    # 防止重复创建输入窗口
    if top_frame.winfo_children():
        return

    top_frame.pack(pady=20)
    tk.Label(top_frame, text="输入随机英雄数量:").pack(side="left")
    global entry
    entry = tk.Entry(top_frame, width=5)
    entry.pack(side="left", padx=10)
    tk.Button(top_frame, text="随机选择", command=on_select).pack(side="left")
    tk.Button(top_frame, text="显示所有英雄", command=show_all_champions).pack(side="left")


root.after(100, cache_icons)
root.mainloop()
