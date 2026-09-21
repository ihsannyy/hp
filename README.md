# 📱 hp - Android Quick Tools CLI for Termux

Alat serbaguna untuk mengontrol hardware dan fitur smartphone Android kamu langsung dari command line Termux.

---

## 🚀 Fitur & Perintah

| Perintah | Contoh | Deskripsi |
|---|---|---|
| `hp` | `hp` | Menampilkan dashboard status lengkap baterai, Wi-Fi, dan volume |
| `hp torch` / `senter` | `hp torch` atau `hp torch on/off` | Menyalakan / mematikan senter HP (auto toggle) |
| `hp battery` / `bat` | `hp battery` | Cek persentase, suhu, voltase, dan kesehatan baterai |
| `hp guard [target]` | `hp guard 80` | Alarm otomatis + suara Google saat baterai mencapai target |
| `hp say <teks>` | `hp say "halo dunia"` | Google Text-to-Speech (bicara suara jernih) |
| `hp remind <teks> <waktu>` | `hp remind "Minum air" 30m` | Pasang alarm / pengingat notifikasi (30s, 5m, 1h) |
| `hp wifi` | `hp wifi` | Cek SSID, IP lokal LAN, link speed, dan kekuatan sinyal |
| `hp volume [level]` | `hp vol 10` atau `hp vol` | Lihat / atur volume suara multimedia / ringtone |
| `hp vibrate [ms]` | `hp vib 500` | Getarkan HP dengan durasi milidetik |
| `hp share <file>` | `hp share file.txt` | Buka menu Android Share Sheet (kirim ke WA/Telegram) |
| `hp photo` | `hp photo` | Jepret kamera belakang/depan langsung ke file |

---

> [!NOTE]
> **Catatan mengenai Nama Wi-Fi (SSID):**
> * Di **Android 8.0 & 9.0 ke bawah**, nama SSID dapat langsung terbaca normal.
> * Di **Android 10 s/d 13**, nama SSID baru terbaca jika izin *Lokasi (Location)* dan GPS utama HP dalam keadaan aktif (kebijakan privasi Google).
> * Di **Android 14+ / 16 (HyperOS / MIUI)**, nama SSID mentah dikunci total oleh sistem keamanan OS sehingga otomatis ditampilkan sebagai status koneksi aman (`Wi-Fi Terkoneksi`) beserta IP LAN lokal yang valid.

---

---

## ⚡ Instalasi Global

Tool ini otomatis tersedia di path sistem:
```bash
hp --help
```
Lengkap dengan auto-completion tab di Fish Shell.
