# Changelog

Semua perubahan penting pada proyek ini dicatat di file ini.

## [1.0.0] - 2026-09-23

### Ditambahkan
- Rilis awal InvisibleToggle: efek "jubah tak terlihat" berbasis webcam menggunakan OpenCV dan MediaPipe.
- Deteksi tangan (MediaPipe Hands) untuk tombol toggle interaktif.
- Deteksi wajah (MediaPipe Face Detection) untuk penanda kotak saat mode invisible aktif.
- Animasi halus pada tombol toggle (posisi slider dan warna).
- `README.md`, `LICENSE` (MIT), dan `run.bat` untuk menjalankan program secara otomatis di Windows.

### Diubah
- Seluruh komentar kode diterjemahkan penuh ke Bahasa Indonesia.
- `main.py` dirapikan dengan memecah logika menjadi fungsi-fungsi terpisah (deteksi jari, deteksi wajah, render frame, gambar tombol).
