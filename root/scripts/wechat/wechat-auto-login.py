#!/usr/bin/env python3
import os
import sys
import time
import subprocess
from PIL import ImageGrab

ENABLE_AUTO_LOGIN = os.environ.get("ENABLE_WECHAT_AUTO_LOGIN", "true").lower() == "true"
AUTO_LOGIN_DELAY = int(os.environ.get("AUTO_LOGIN_DELAY", "3"))

if not ENABLE_AUTO_LOGIN:
    print("ℹ️ WeChat auto-login disabled via ENABLE_WECHAT_AUTO_LOGIN=false.")
    sys.exit(0)

def get_active_window():
    try:
        out = subprocess.check_output(
            ["xdotool", "search", "--onlyvisible", ""],
            env={"DISPLAY": os.environ.get("DISPLAY", ":1")}
        ).decode().splitlines()
        
        for wid in out:
            try:
                name = subprocess.check_output(
                    ["xdotool", "getwindowname", wid],
                    env={"DISPLAY": os.environ.get("DISPLAY", ":1")}
                ).decode().strip()
                geom = subprocess.check_output(
                    ["xdotool", "getwindowgeometry", "--shell", wid],
                    env={"DISPLAY": os.environ.get("DISPLAY", ":1")}
                ).decode().splitlines()
                
                g_dict = {l.split("=")[0]: int(l.split("=")[1]) for l in geom if "=" in l and l.split("=")[1].isdigit()}
                width = g_dict.get("WIDTH", 0)
                height = g_dict.get("HEIGHT", 0)
                
                if width > 300 and height > 300:
                    return wid, name, g_dict
            except Exception:
                continue
    except Exception:
        pass
    return None, "", {}

def run_auto_login():
    print(f"🔍 [1/3] Searching for WeChat window (max wait 15s)...")
    win_id = None
    win_name = ""
    geom = {}
    
    for _ in range(15):
        win_id, win_name, geom = get_active_window()
        if win_id:
            break
        time.sleep(1)

    if not win_id:
        print("⚠️ WeChat window not found within 15 seconds.")
        sys.exit(0)

    print(f"✅ [2/3] Found window ID: {win_id}, Title: '{win_name}', Dimensions: {geom.get('WIDTH')}x{geom.get('HEIGHT')}")

    if win_name == "Weixin":
        print("🎉 [State: Logged In] WeChat is already logged in and active on main screen.")
        sys.exit(0)

    print(f"⏳ Waiting {AUTO_LOGIN_DELAY} seconds for UI rendering...")
    time.sleep(AUTO_LOGIN_DELAY)

    img = ImageGrab.grab()
    pixels = list(img.get_flattened_data() if hasattr(img, "get_flattened_data") else img.getdata())
    green_count = sum(1 for p in pixels if len(p) >= 3 and p[0] < 50 and 150 <= p[1] <= 240 and 60 <= p[2] <= 140)
    
    print(f"📊 [3/3] UI Color Feature Count (Green/Blue Button Pixels): {green_count}")

    if green_count > 1200:
        print("🟢 [State: Pending Login Button] Login button detected! Executing auto-login action...")
        disp_env = {"DISPLAY": os.environ.get("DISPLAY", ":1")}
        subprocess.call(["xdotool", "windowactivate", "--sync", win_id], env=disp_env)
        time.sleep(0.5)
        subprocess.call(["xdotool", "key", "Return"], env=disp_env)
        
        width = geom.get("WIDTH", 1000)
        height = geom.get("HEIGHT", 800)
        btn_x = width // 2
        btn_y = int(height * 0.70)
        subprocess.call(["xdotool", "mousemove", "--window", win_id, str(btn_x), str(btn_y), "click", "1"], env=disp_env)
        print("🚀 Auto-login command dispatched successfully.")
    else:
        print("""
============================================================
📱 [State: QR Code Required]
WeChat is currently displaying the QR code login screen.

👉 Please scan the QR code using WeChat on your mobile phone:
   • HTTPS: https://<HOST_IP>:3001
   • HTTP : http://<HOST_IP>:3000
============================================================
""")

if __name__ == "__main__":
    run_auto_login()
