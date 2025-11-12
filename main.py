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
        print(f"获取版本号失败: {e}")
        return None


# 获取中文英雄数据
def get_champion_data(version):
    url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/zh_CN/champion.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        champions = data["data"]
        # 返回 id 映射到 中文信息
        return {
            champ["id"]: {
                "title": champ["title"],  # 英雄称号（显示在图标下）
                "name": champ["name"],    # 英雄中文名（如 暗裔剑魔）
                "blurb": champ["blurb"]   # 简介
            }
            for champ in champions.values()
        }
    except requests.RequestException as e:
        print(f"获取英雄数据失败: {e}")
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
            print(f"下载图标失败 {champion_id}: {e}")
            return None
    return file_path


# 缓存图标并更新进度条
def cache_icons():
    global champions, version
    version = get_latest_version()
    if not version:
        progress_label.config(text="❌ 获取版本号失败")
        return

    champions = get_champion_data(version)
    if not champions:
        progress_label.config(text="❌ 获取英雄数据失败")
        return

    total = len(champions)
    champion_count_label.config(text=f"当前版本全英雄数量: {total}")
    progress_bar["maximum"] = total
    count = 0

    for champ_id in champions.keys():
        download_icon(champ_id, version)
        count += 1
        progress_bar["value"] = count
        progress_label.config(text=f"首次使用正在缓存英雄图标中，请稍候喵... {count}/{total}")
        root.update_idletasks()

    progress_label.config(text="✅ 图标缓存完成喵！")
    start_button.config(state="normal")


# 随机选择英雄
def select_random_champions(champions, count):
    return random.sample(list(champions.items()), count)


# 点击头像显示英雄信息
def show_champion_info(info):
    messagebox.showinfo(
        title=info["title"],
        message=f"{info['name']}\n\n{info['blurb']}"
    )


# 显示图标（中文标题）
def display_champions(selected):
    for widget in canvas_frame.winfo_children():
        widget.destroy()

    max_icons_per_row = 10
    row, col = 0, 0

    for champ_id, info in selected:
        icon_path = f"icons/{champ_id}.png"
        if os.path.exists(icon_path):
            img = Image.open(icon_path).resize((64, 64))
            photo = ImageTk.PhotoImage(img)
            btn = tk.Button(
                canvas_frame,
                image=photo,
                text=info["title"],  # 中文称号
                compound="top",
                command=lambda c=info: show_champion_info(c)
            )
            btn.image = photo
            btn.grid(row=row, column=col, padx=10, pady=10)

        col += 1
        if col >= max_icons_per_row:
            col = 0
            row += 1

    canvas.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))


# 随机选择事件
def on_select():
    try:
        count = int(entry.get())
        if count > len(champions):
            messagebox.showwarning("警告", "输入数量超过英雄总数！")
        else:
            selected = select_random_champions(champions, count)
            display_champions(selected)
    except ValueError:
        messagebox.showerror("错误", "请输入有效数字！")


# 显示全部英雄
def show_all_champions():
    display_champions(list(champions.items()))


# 初始化 icons 文件夹
if not os.path.exists("icons"):
    os.makedirs("icons")

# 创建主窗口
root = tk.Tk()
root.title("大乱斗随机英雄选择器 — By 南京大学电竞社 黑喵喵")
root.geometry("1260x800")

# 设置窗口图标
icon_path = r"D:\Mygithub\ARAM_Random_Champions\gwenicon.png"
if os.path.exists(icon_path):
    icon_image = ImageTk.PhotoImage(file=icon_path)
    root.iconphoto(True, icon_image)

# 顶部信息与进度条
progress_label = tk.Label(root, text="初始化中喵...")
progress_label.pack(pady=10)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=10)

champion_count_label = tk.Label(root, text="当前版本全英雄数量: 0")
champion_count_label.pack(pady=10)

# 主功能按钮
start_button = tk.Button(root, text="战斗，爽！", state="disabled", command=lambda: start_selection())
start_button.pack(pady=10)

# 滚动区
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

# 顶部输入区
top_frame = tk.Frame(root)


def start_selection():
    if top_frame.winfo_children():
        return
    top_frame.pack(pady=20)
    tk.Label(top_frame, text="输入随机英雄数量:").pack(side="left")
    global entry
    entry = tk.Entry(top_frame, width=5)
    entry.pack(side="left", padx=10)
    tk.Button(top_frame, text="随机选择", command=on_select).pack(side="left")
    tk.Button(top_frame, text="显示全部英雄", command=show_all_champions).pack(side="left")


# 启动缓存
root.after(100, cache_icons)
root.mainloop()

# cd /d D:\Mygithub\ARAM_Random_Champions
# python -m PyInstaller --noconsole --onefile --add-data "icons;icons" --icon "gwenicon.png" main.py