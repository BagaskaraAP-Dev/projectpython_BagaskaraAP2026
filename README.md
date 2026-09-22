# InvisibleToggle 🫥

Program "jubah tak terlihat" (invisibility cloak) berbasis webcam, dibuat menggunakan **Python**, **OpenCV**, dan **MediaPipe**. Proyek ini sepenuhnya dibuat sendiri sebagai eksperimen computer vision — mendeteksi gerakan tangan secara real-time untuk mengaktifkan/menonaktifkan efek "menghilang" di layar.

## Cara Kerja

1. **Perekaman latar belakang** — saat program dijalankan, pengguna diminta menjauh dari kamera selama 3 detik pertama. Frame yang tertangkap saat itu disimpan sebagai "latar belakang kosong".
2. **Deteksi tangan** — menggunakan MediaPipe Hands untuk melacak posisi ujung jari telunjuk secara real-time.
3. **Tombol toggle interaktif** — pengguna cukup mengarahkan jari telunjuk ke tombol di sudut kiri atas layar untuk menyalakan atau mematikan mode "invisible", lengkap dengan animasi slider dan warna yang halus.
4. **Efek menghilang** — ketika mode invisible aktif, frame kamera diganti dengan frame latar belakang yang sudah direkam, sehingga tubuh pengguna seolah menghilang dari layar.
5. **Pelacakan wajah** — menggunakan MediaPipe Face Detection untuk tetap menandai posisi wajah dengan kotak hijau dan label "INVISIBLE" selama mode aktif.

## Kebutuhan Sistem

- Python **3.9 - 3.12** (MediaPipe belum mendukung Python 3.13/3.14)
- Webcam yang terhubung ke komputer

## Instalasi & Menjalankan Program

### Windows (otomatis)

Cukup jalankan file `run.bat`. Skrip ini akan otomatis:
- Membuat virtual environment Python 3.11 (menggunakan `uv` jika tersedia, atau `venv` bawaan Python)
- Menginstal seluruh dependensi dari `requirements.txt`
- Menjalankan `main.py`

```
run.bat
```

### Manual (semua platform)

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/Mac

pip install -r requirements.txt
python main.py
```

## Kontrol

| Aksi | Cara |
|---|---|
| Nyalakan/matikan mode invisible | Arahkan ujung jari telunjuk ke tombol toggle di kiri atas layar |
| Keluar dari program | Tekan tombol `q` pada jendela video |

## Dependensi

Lihat [`requirements.txt`](requirements.txt):
- `mediapipe==0.10.21` — deteksi tangan & wajah
- `opencv-python<4.12` — pengambilan & pengolahan video
- `numpy<2` — komputasi numerik untuk animasi warna/posisi

## Lisensi & Kontribusi

Proyek ini dibuat dan dikembangkan sepenuhnya oleh saya sendiri, **Bagaskara AP**, sebagai proyek pribadi/eksperimen belajar computer vision dengan Python. Tidak ada kontributor lain.
