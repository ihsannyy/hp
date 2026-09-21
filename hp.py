#!/data/data/com.termux/files/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
 hp - Android Quick Tools CLI for Termux
 Control your Android device hardware & system directly from the terminal.
==============================================================================
"""

import sys
import os
import json
import time
import shutil
import argparse
import subprocess
import threading
from datetime import datetime, timedelta

# ANSI Colors - macOS Glass / Modern Palette
CLR_RESET   = "\033[0m"
CLR_BOLD    = "\033[1m"
CLR_DIM     = "\033[2m"
CLR_RED     = "\033[38;2;255;95;86m"
CLR_YELLOW  = "\033[38;2;255;189;46m"
CLR_GREEN   = "\033[38;2;48;209;88m"
CLR_CYAN    = "\033[38;2;90;200;250m"
CLR_BLUE    = "\033[38;2;10;132;255m"
CLR_PURPLE  = "\033[38;2;175;82;222m"
CLR_GRAY    = "\033[38;2;134;142;150m"
CLR_CARD_BG = "\033[48;2;33;34;46m"
CLR_WHITE   = "\033[38;2;240;242;246m"

STATE_DIR = os.path.expanduser("~/.config/hp")
os.makedirs(STATE_DIR, exist_ok=True)
TORCH_STATE = os.path.join(STATE_DIR, "torch.state")

def check_cmd(cmd):
    return shutil.which(cmd) is not None

def run_termux(cmd_list, timeout=5):
    try:
        res = subprocess.run(cmd_list, capture_output=True, text=True, timeout=timeout)
        return res.stdout.strip()
    except Exception as e:
        return None

def toast(msg):
    if check_cmd("termux-toast"):
        run_termux(["termux-toast", "-b", "#14151e", "-c", "#f0f2f6", "-g", "top", msg])
    else:
        print(f"[{msg}]")

# ==============================================================================
# SUBCOMMANDS
# ==============================================================================

def cmd_battery(args):
    """Cek status baterai lengkap & modern"""
    raw = run_termux(["termux-battery-status"])
    if not raw:
        print(f"{CLR_RED}✖ Gagal mengambil info baterai via Termux:API.{CLR_RESET}")
        return

    try:
        data = json.loads(raw)
    except Exception:
        print(f"{CLR_RED}✖ Format data baterai tidak valid.{CLR_RESET}")
        return

    pct = data.get("percentage", 0)
    status = data.get("status", "UNKNOWN")
    health = data.get("health", "GOOD")
    plugged = data.get("plugged", "UNPLUGGED")
    temp = data.get("temperature", 0.0)
    
    # Icons & status color
    if status == "CHARGING":
        icon = "󰂄"
        st_color = CLR_YELLOW
        status_text = "Sedang Dicas (Charging)"
    elif pct <= 20:
        icon = " "
        st_color = CLR_RED
        status_text = "Baterai Lemah!"
    elif pct <= 50:
        icon = " "
        st_color = CLR_YELLOW
        status_text = "Pemakaian Normal"
    else:
        icon = " "
        st_color = CLR_GREEN
        status_text = "Optimal"

    print()
    print(f" {CLR_RED}● {CLR_YELLOW}● {CLR_GREEN}●   {CLR_BOLD}{CLR_BLUE}Status Baterai Android{CLR_RESET}")
    print(f" {CLR_DIM}──────────────────────────────────────────{CLR_RESET}")
    print(f"  {CLR_GRAY}Persentase {CLR_RESET}: {st_color}{CLR_BOLD}{icon} {pct}%{CLR_RESET} ({status_text})")
    print(f"  {CLR_GRAY}Kesehatan  {CLR_RESET}: {CLR_GREEN}  {health}{CLR_RESET}")
    print(f"  {CLR_GRAY}Koneksi    {CLR_RESET}: {CLR_CYAN}  {plugged}{CLR_RESET}")
    print(f"  {CLR_GRAY}Suhu       {CLR_RESET}: {CLR_PURPLE}  {temp}°C{CLR_RESET}")
    print(f" {CLR_DIM}──────────────────────────────────────────{CLR_RESET}")
    print()

def cmd_guard(args):
    """Monitor baterai: Bunyikan notifikasi/suara saat penuh (80%) atau kritis (<20%)"""
    target = args.target or 85
    sound = args.sound
    print(f"{CLR_CYAN}🛡  Baterai Guard Aktif! Menjaga di target {target}%...{CLR_RESET}")
    print(f"{CLR_DIM}Tekan Ctrl+C untuk menghentikan monitoring.{CLR_RESET}\n")
    
    try:
        while True:
            raw = run_termux(["termux-battery-status"])
            if raw:
                try:
                    data = json.loads(raw)
                    pct = data.get("percentage", 0)
                    status = data.get("status", "")
                    
                    now = datetime.now().strftime("%H:%M:%S")
                    print(f"\r[{now}] Level: {pct}% | Status: {status}  ", end="", flush=True)

                    if status == "CHARGING" and pct >= target:
                        msg = f"Baterai sudah mencapai {pct}%! Cabut charger sekarang."
                        toast(msg)
                        if sound and check_cmd("termux-tts-speak"):
                            run_termux(["termux-tts-speak", msg])
                        if check_cmd("termux-notification"):
                            run_termux(["termux-notification", "--id", "hp_guard", "-t", "Baterai Guard!", "-c", msg, "--vibrate", "500,500,500"])
                        print(f"\n{CLR_GREEN}✔ Target tercapai! {msg}{CLR_RESET}")
                        break
                except Exception:
                    pass
            time.sleep(10)
    except KeyboardInterrupt:
        print(f"\n{CLR_GRAY}Monitoring dihentikan.{CLR_RESET}")

def cmd_torch(args):
    """Kontrol Senter (on, off, toggle)"""
    state = "off"
    if os.path.exists(TORCH_STATE):
        try:
            with open(TORCH_STATE, "r") as f:
                state = f.read().strip()
        except Exception:
            state = "off"

    action = args.action
    if not action or action == "toggle":
        action = "off" if state == "on" else "on"

    if action in ("on", "1", "true"):
        run_termux(["termux-torch", "on"])
        with open(TORCH_STATE, "w") as f: f.write("on")
        toast("Senter Menyala 🔦")
        print(f" {CLR_YELLOW}🔦 Senter: ON{CLR_RESET}")
    else:
        run_termux(["termux-torch", "off"])
        with open(TORCH_STATE, "w") as f: f.write("off")
        toast("Senter Mati")
        print(f" {CLR_GRAY}🔦 Senter: OFF{CLR_RESET}")

def cmd_say(args):
    """Text to Speech (TTS) menggunakan suara Google/Android"""
    text = " ".join(args.text)
    if not text.strip():
        print(f"{CLR_YELLOW}Gunakan: hp say <kalimat>{CLR_RESET}")
        return

    lang = args.lang or "id-ID"
    pitch = args.pitch or 1.0
    rate = args.rate or 1.0

    print(f"{CLR_CYAN}🗣 Mengucapkan:{CLR_RESET} \"{text}\"")
    cmd = ["termux-tts-speak", "-l", lang, "-p", str(pitch), "-r", str(rate), text]
    run_termux(cmd, timeout=30)

def cmd_vib(args):
    """Getarkan HP dengan durasi atau ritme pola"""
    ms = args.duration or 300
    if check_cmd("termux-vibrate"):
        run_termux(["termux-vibrate", "-d", str(ms)])
        print(f" {CLR_PURPLE}📳 Bergetar {ms}ms{CLR_RESET}")
    else:
        print(f"{CLR_RED}✖ termux-vibrate tidak tersedia.{CLR_RESET}")

def get_network_info():
    """Dapatkan info jaringan, IP LAN, Gateway, dan ISP secara reliable"""
    import socket
    net = {
        "lan_ip": "127.0.0.1",
        "gateway": "",
        "isp": "",
        "city": "",
        "status": "Online"
    }
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        net["lan_ip"] = s.getsockname()[0]
        s.close()
    except Exception:
        net["status"] = "Offline"
        return net

    # Cek ISP / Publik ringan via thread
    def _fetch_isp():
        try:
            req = urllib.request.Request("http://ip-api.com/json", headers={"User-Agent": "hp-cli"})
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                data = json.loads(resp.read().decode())
                if data.get("status") == "success":
                    net["isp"] = data.get("isp", "")
                    net["city"] = data.get("city", "")
        except Exception:
            pass

    t = threading.Thread(target=_fetch_isp)
    t.start()
    t.join(timeout=1.6)

    return net

def cmd_wifi(args):
    """Informasi status Wi-Fi & Jaringan Lengkap"""
    raw = run_termux(["termux-wifi-connectioninfo"], timeout=2)
    data = {}
    if raw:
        try:
            data = json.loads(raw)
        except Exception:
            data = {}

    net = get_network_info()
    ip = data.get("ip") or net["lan_ip"]
    ssid = data.get("ssid", "")
    speed = data.get("link_speed_mbps", 0)
    rssi = data.get("rssi", 0)
    freq = data.get("frequency_mhz", 0)

    # Format SSID display
    if ssid and ssid not in ("<unknown ssid>", "0x", "null", "<Unknown>"):
        ssid_display = f"{CLR_GREEN}  {ssid}{CLR_RESET}"
    else:
        # Jika Android 10+ menyembunyikan SSID, tampilkan status koneksi cerdas
        if net["isp"]:
            ssid_display = f"{CLR_GREEN}  Wi-Fi Aktif{CLR_RESET} {CLR_GRAY}({net['isp']}){CLR_RESET}"
        else:
            ssid_display = f"{CLR_GREEN}  Wi-Fi Terkoneksi{CLR_RESET}"

    print()
    print(f" {CLR_RED}● {CLR_YELLOW}● {CLR_GREEN}●   {CLR_BOLD}{CLR_CYAN}Status Jaringan & Wi-Fi{CLR_RESET}")
    print(f" {CLR_DIM}──────────────────────────────────────────{CLR_RESET}")
    print(f"  {CLR_GRAY}Status Jaringan {CLR_RESET}: {ssid_display}")
    print(f"  {CLR_GRAY}IP Lokal (LAN)  {CLR_RESET}: {CLR_BLUE}󰩠  {ip}{CLR_RESET}")
    if net["isp"]:
        loc_str = f" ({net['city']})" if net["city"] else ""
        print(f"  {CLR_GRAY}Provider / ISP  {CLR_RESET}: {CLR_PURPLE}  {net['isp']}{loc_str}{CLR_RESET}")
    if speed > 0:
        print(f"  {CLR_GRAY}Kecepatan Link  {CLR_RESET}: {CLR_YELLOW}󰛳  {speed} Mbps{CLR_RESET}")
    if rssi != 0:
        print(f"  {CLR_GRAY}Kekuatan Sinyal {CLR_RESET}: {CLR_PURPLE}󰢾  {rssi} dBm ({freq} MHz){CLR_RESET}")
    print(f" {CLR_DIM}──────────────────────────────────────────{CLR_RESET}")
    print()

def cmd_share(args):
    """Buka Android Share Sheet untuk file atau teks ke WhatsApp, Telegram, dll"""
    target = args.target
    if not target:
        print(f"{CLR_YELLOW}Gunakan: hp share <path_file atau teks>{CLR_RESET}")
        return

    if os.path.exists(target):
        abs_path = os.path.abspath(target)
        cmd = ["termux-share", "-a", "send", abs_path]
        print(f"{CLR_GREEN}📤 Berbagi file:{CLR_RESET} {abs_path}")
    else:
        cmd = ["termux-share", "-a", "send", target]
        print(f"{CLR_GREEN}📤 Berbagi teks ke Android...{CLR_RESET}")
    
    run_termux(cmd)

def cmd_vol(args):
    """Atur volume stream musik/ringtone/call (0-15)"""
    stream = args.stream or "music"
    level = args.level
    if level is None:
        raw = run_termux(["termux-volume"])
        if raw:
            try:
                vols = json.loads(raw)
                print()
                print(f" {CLR_RED}● {CLR_YELLOW}● {CLR_GREEN}●   {CLR_BOLD}{CLR_PURPLE}Volume Suara Android{CLR_RESET}")
                print(f" {CLR_DIM}──────────────────────────────────────────{CLR_RESET}")
                for v in vols:
                    s_name = v.get("stream", "")
                    vol = v.get("volume", 0)
                    max_v = v.get("max_volume", 15)
                    bar = "█" * vol + "░" * (max_v - vol)
                    print(f"  {CLR_GRAY}{s_name.ljust(12)}{CLR_RESET} : {CLR_BLUE}{bar}{CLR_RESET} ({vol}/{max_v})")
                print(f" {CLR_DIM}──────────────────────────────────────────{CLR_RESET}")
                print(f" {CLR_DIM}Contoh atur: hp vol 12 (atau: hp vol 10 --stream ring){CLR_RESET}\n")
            except Exception:
                pass
        return

    cmd = ["termux-volume", stream, str(level)]
    run_termux(cmd)
    toast(f"Volume {stream}: {level}")
    print(f" {CLR_GREEN}✔ Volume {stream} disetel ke: {level}{CLR_RESET}")

def cmd_remind(args):
    """Pasang pengingat timer notifikasi / alarm cepat"""
    msg = args.message
    time_str = args.time
    
    # Parse time (misal: 30s, 5m, 1h, 10)
    seconds = 0
    if time_str.endswith("s"):
        seconds = int(time_str[:-1])
    elif time_str.endswith("m"):
        seconds = int(time_str[:-1]) * 60
    elif time_str.endswith("h"):
        seconds = int(time_str[:-1]) * 3600
    elif time_str.isdigit():
        seconds = int(time_str) * 60 # default menit
    else:
        print(f"{CLR_RED}✖ Format waktu tidak dikenal. Contoh: 30s, 5m, 1h{CLR_RESET}")
        return

    due_time = (datetime.now() + timedelta(seconds=seconds)).strftime("%H:%M:%S")
    print(f" {CLR_GREEN}⏰ Pengingat dipasang:{CLR_RESET} \"{msg}\"")
    print(f" {CLR_DIM}Akan berbunyi pukul {due_time} ({time_str} lagi)...{CLR_RESET}")
    toast(f"⏰ Timer dipasang: {msg} ({time_str})")

    def _wait_and_notify():
        time.sleep(seconds)
        if check_cmd("termux-notification"):
            run_termux([
                "termux-notification",
                "--id", "hp_reminder",
                "-t", "⏰ PENGINGAT HP!",
                "-c", msg,
                "--vibrate", "500,500,500,500",
                "--sound",
                "--priority", "high"
            ])
        if check_cmd("termux-tts-speak"):
            run_termux(["termux-tts-speak", f"Waktunya: {msg}"])

    # Jalankan background proses independen
    t = threading.Thread(target=_wait_and_notify, daemon=True)
    t.start()
    # Biarkan thread tetap jalan jika script selesai
    if not args.sync:
        # Spawn daemon subprocess
        py_code = f"import time, subprocess; time.sleep({seconds}); subprocess.run(['termux-notification', '--id', 'hp_reminder', '-t', '⏰ PENGINGAT HP!', '-c', {repr(msg)}, '--vibrate', '500,500,500', '--sound', '--priority', 'high'])"
        subprocess.Popen([sys.executable, "-c", py_code], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)

def cmd_photo(args):
    """Ambil foto dari kamera belakang/depan langsung ke file"""
    cid = args.camera or "0" # 0: belakang, 1: depan
    target = args.output or os.path.expanduser(f"~/photo_{int(time.time())}.jpg")
    
    print(f" {CLR_CYAN}📸 Mengambil foto dari kamera {cid}...{CLR_RESET}")
    cmd = ["termux-camera-photo", "-c", str(cid), target]
    run_termux(cmd, timeout=10)
    if os.path.exists(target):
        print(f" {CLR_GREEN}✔ Foto tersimpan di:{CLR_RESET} {target}")
        toast("Foto berhasil diambil 📸")
    else:
        print(f" {CLR_RED}✖ Gagal mengambil foto atau izin kamera belum aktif.{CLR_RESET}")

def cmd_dashboard(args):
    """Dashboard Interaktif Status HP"""
    os.system("clear")
    cmd_battery(args)
    cmd_wifi(args)
    cmd_vol(argparse.Namespace(stream=None, level=None))
    print(f" {CLR_BOLD}Menu Pintas:{CLR_RESET}")
    print(f"  {CLR_CYAN}hp torch{CLR_RESET}          -> Nyalakan/matikan senter")
    print(f"  {CLR_CYAN}hp say <kata>{CLR_RESET}     -> Bicara suara Google (TTS)")
    print(f"  {CLR_CYAN}hp remind <teks> <waktu>{CLR_RESET} -> Pasang timer notifikasi (e.g. 5m)")
    print(f"  {CLR_CYAN}hp guard <target>{CLR_RESET}  -> Alarm proteksi baterai (e.g. 80%)")
    print(f"  {CLR_CYAN}hp share <file>{CLR_RESET}   -> Kirim file ke WA/Telegram")
    print()

# ==============================================================================
# MAIN ROUTER
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        prog="hp",
        description="Android Quick Tools CLI for Termux",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contoh Penggunaan:
  hp                     Tampilkan dashboard info HP lengkap
  hp torch               Toggle nyala/mati senter HP
  hp battery             Cek status & kesehatan baterai
  hp guard 85            Bunyikan alarm saat cas baterai mencapai 85%
  hp remind "Minum air" 30m   Pasang timer pengingat 30 menit
  hp say "Halo mas ihsan"      Suara Google bicara
  hp wifi                Cek IP lokal, SSID, dan kecepatan sinyal
  hp vol 10              Atur volume musik ke level 10
  hp share lagu.mp3      Buka menu share Android ke WhatsApp/Telegram
  hp photo               Jepret kamera belakang langsung simpan ke file
        """
    )
    
    subparsers = parser.add_subparsers(dest="command")

    # battery
    p_bat = subparsers.add_parser("battery", aliases=["bat", "b"], help="Cek persentase & kesehatan baterai")
    
    # guard
    p_grd = subparsers.add_parser("guard", help="Alarm pengingat baterai penuh/kritis")
    p_grd.add_argument("target", type=int, nargs="?", default=85, help="Target persentase baterai (default: 85)")
    p_grd.add_argument("--sound", "-s", action="store_true", default=True, help="Bunyikan suara TTS")

    # torch
    p_trc = subparsers.add_parser("torch", aliases=["senter", "t"], help="Nyalakan/matikan senter HP")
    p_trc.add_argument("action", nargs="?", choices=["on", "off", "toggle"], default="toggle", help="Aksi senter")

    # say / tts
    p_say = subparsers.add_parser("say", aliases=["speak", "tts"], help="Suara Google berbicara (TTS)")
    p_say.add_argument("text", nargs="+", help="Teks yang ingin diucapkan")
    p_say.add_argument("--lang", "-l", default="id-ID", help="Bahasa (default: id-ID)")
    p_say.add_argument("--pitch", "-p", type=float, default=1.0, help="Pitch suara")
    p_say.add_argument("--rate", "-r", type=float, default=1.0, help="Kecepatan bicara")

    # vibrate
    p_vib = subparsers.add_parser("vibrate", aliases=["vib", "v"], help="Getarkan HP")
    p_vib.add_argument("duration", type=int, nargs="?", default=300, help="Durasi getar dalam milidetik (default: 300ms)")

    # wifi
    p_wif = subparsers.add_parser("wifi", aliases=["w", "ip"], help="Status Wi-Fi & IP LAN")

    # share
    p_shr = subparsers.add_parser("share", aliases=["send"], help="Kirim file/teks via Android Share Sheet")
    p_shr.add_argument("target", help="Path file atau teks yang mau dibagikan")

    # vol
    p_vol = subparsers.add_parser("volume", aliases=["vol"], help="Lihat atau ubah volume suara")
    p_vol.add_argument("level", type=int, nargs="?", default=None, help="Level volume (0-15)")
    p_vol.add_argument("--stream", "-s", default="music", choices=["music", "ring", "notification", "system", "call"], help="Target stream audio")

    # remind
    p_rmd = subparsers.add_parser("remind", aliases=["alarm", "timer"], help="Pasang timer alarm / pengingat notifikasi")
    p_rmd.add_argument("message", help="Pesan pengingat")
    p_rmd.add_argument("time", help="Waktu hitung mundur (contoh: 30s, 5m, 1h)")
    p_rmd.add_argument("--sync", action="store_true", help="Jalankan di foreground")

    # photo
    p_pht = subparsers.add_parser("photo", aliases=["cam"], help="Ambil foto kamera")
    p_pht.add_argument("--camera", "-c", default="0", choices=["0", "1"], help="0: Kamera Belakang, 1: Kamera Depan")
    p_pht.add_argument("--output", "-o", default=None, help="Lokasi penyimpanan file foto")

    args = parser.parse_args()

    if not args.command:
        cmd_dashboard(args)
    elif args.command in ("battery", "bat", "b"):
        cmd_battery(args)
    elif args.command == "guard":
        cmd_guard(args)
    elif args.command in ("torch", "senter", "t"):
        cmd_torch(args)
    elif args.command in ("say", "speak", "tts"):
        cmd_say(args)
    elif args.command in ("vibrate", "vib", "v"):
        cmd_vib(args)
    elif args.command in ("wifi", "w", "ip"):
        cmd_wifi(args)
    elif args.command in ("share", "send"):
        cmd_share(args)
    elif args.command in ("volume", "vol"):
        cmd_vol(args)
    elif args.command in ("remind", "alarm", "timer"):
        cmd_remind(args)
    elif args.command in ("photo", "cam"):
        cmd_photo(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
