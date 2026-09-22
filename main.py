"""
InvisibleToggle
================
Program "jubah tak terlihat" berbasis webcam menggunakan OpenCV dan MediaPipe.

Cara kerja singkat:
1. Program merekam 3 detik pertama sebagai gambar "latar belakang kosong"
   (jadi pengguna harus menjauh dari kamera dulu di awal).
2. Tangan pengguna dilacak dengan MediaPipe Hands. Saat ujung jari telunjuk
   menyentuh area tombol toggle di layar, status ON/OFF berubah.
3. Selama status ON (invisible), frame kamera yang tampil diganti dengan
   frame latar belakang yang sudah direkam, sehingga tubuh pengguna
   "menghilang" dari layar - sementara wajah tetap dilacak dan ditandai
   dengan kotak hijau bertuliskan "INVISIBLE".
4. Tombol toggle digambar dengan animasi halus (posisi slider dan warna
   latar tombol berinterpolasi bertahap) agar terasa lebih hidup.

Kontrol: tekan tombol toggle di kiri atas layar dengan jari telunjuk untuk
menyalakan/mematikan mode invisible. Tekan 'q' untuk keluar dari program.
"""

import cv2
# pyrefly: ignore [missing-import]
import mediapipe as mp
import time
import numpy as np

# --- Pengaturan tombol toggle ---
BTN_X, BTN_Y = 60, 60
BTN_W, BTN_H = 160, 80
RADIUS = BTN_H // 2

COLOR_OFF = np.array([150, 150, 150], dtype=float)
COLOR_ON = np.array([220, 120, 0], dtype=float)  # Oranye (format BGR)
ANIM_SPEED = 0.15  # Kecepatan interpolasi animasi tombol (0-1, makin besar makin cepat)
COOLDOWN_FRAMES = 25  # Jeda antar-toggle agar tidak berkedip saat jari menahan tombol
BACKGROUND_CAPTURE_DELAY = 3  # Detik menunggu sebelum merekam latar belakang


def detect_finger_toggle_press(hands_results, frame, w, h):
    """Cari posisi ujung jari telunjuk dan cek apakah sedang menekan tombol toggle."""
    finger_pos = None
    pressing_button = False

    if hands_results.multi_hand_landmarks:
        for hand_landmarks in hands_results.multi_hand_landmarks:
            index_finger = hand_landmarks.landmark[8]  # Titik landmark ujung jari telunjuk
            fx, fy = int(index_finger.x * w), int(index_finger.y * h)
            finger_pos = (fx, fy)
            cv2.circle(frame, (fx, fy), 10, (0, 255, 0), -1)

            if BTN_X < fx < BTN_X + BTN_W and BTN_Y < fy < BTN_Y + BTN_H:
                pressing_button = True

    return finger_pos, pressing_button


def detect_face_bbox(face_results, w, h):
    """Ambil kotak pembatas (bounding box) wajah pertama yang terdeteksi."""
    if not face_results.detections:
        return None

    detection = face_results.detections[0]
    bbox = detection.location_data.relative_bounding_box
    bx, by = int(bbox.xmin * w), int(bbox.ymin * h)
    bw, bh = int(bbox.width * w), int(bbox.height * h)
    return (bx, by, bw, bh)


def render_frame(frame, background, is_invisible, last_bbox, current_bbox):
    """Susun frame yang akan ditampilkan: latar belakang kosong (invisible) atau frame asli."""
    if background is not None and is_invisible:
        display_frame = background.copy()
        if last_bbox is not None:
            bx, by, bw, bh = last_bbox
            cv2.rectangle(display_frame, (bx, by), (bx + bw, by + bh), (0, 255, 0), 2)
            cv2.putText(display_frame, "INVISIBLE", (bx, by - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    else:
        display_frame = frame.copy()
        if current_bbox is not None:
            bx, by, bw, bh = current_bbox
            cv2.rectangle(display_frame, (bx, by), (bx + bw, by + bh), (0, 255, 0), 2)

    return display_frame


def draw_toggle_button(display_frame, anim_slider_x, anim_bg_color, is_invisible):
    """Gambar tombol toggle beserta slider dan label ON/OFF dengan animasi halus."""
    fill_color = (int(anim_bg_color[0]), int(anim_bg_color[1]), int(anim_bg_color[2]))

    # Bentuk kapsul dibuat dari satu persegi panjang di tengah dan dua lingkaran di kedua ujungnya
    cv2.circle(display_frame, (BTN_X + RADIUS, BTN_Y + RADIUS), RADIUS, fill_color, -1)
    cv2.circle(display_frame, (BTN_X + BTN_W - RADIUS, BTN_Y + RADIUS), RADIUS, fill_color, -1)
    cv2.rectangle(display_frame, (BTN_X + RADIUS, BTN_Y), (BTN_X + BTN_W - RADIUS, BTN_Y + BTN_H),
                  fill_color, -1)

    # Teks label "ON"/"OFF" di dalam tombol
    is_more_on = anim_bg_color[0] > 180
    text_color = (255, 255, 255) if is_more_on else (200, 200, 200)

    if is_invisible:
        cv2.putText(display_frame, "ON", (BTN_X + 25, BTN_Y + 52),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, text_color, 3)
    else:
        cv2.putText(display_frame, "  OFF", (BTN_X + BTN_W - 95, BTN_Y + 52),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, text_color, 3)

    # Ball/slider putih yang bergerak halus mengikuti status toggle
    slider_center_x = int(anim_slider_x)
    cv2.circle(display_frame, (BTN_X + slider_center_x, BTN_Y + RADIUS),
               RADIUS - 6, (255, 255, 255), -1)


def main():
    # Inisialisasi MediaPipe untuk deteksi tangan dan wajah
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.8, min_tracking_confidence=0.5)

    mp_face_detection = mp.solutions.face_detection
    face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)

    cap = cv2.VideoCapture(0)

    background = None      # Frame latar belakang yang direkam saat program pertama kali jalan
    is_invisible = False   # Status toggle: True = mode "tak terlihat" aktif
    last_bbox = None       # Kotak pembatas wajah terakhir yang terdeteksi
    cooldown = 0            # Jeda antar-toggle agar tidak berkedip saat jari menahan tombol

    # Variabel untuk animasi HALUS (interpolasi posisi & warna tombol)
    anim_slider_x = float(RADIUS)
    anim_bg_color = COLOR_OFF.copy()

    print("Menjauh dari kamera untuk merekam latar belakang...")
    start_time = time.time()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        if background is None:
            if time.time() - start_time < BACKGROUND_CAPTURE_DELAY:
                continue
            background = frame.copy()
            print("Latar belakang tersimpan. Tombol toggle sudah aktif.")

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # --- Update animasi halus tombol (posisi slider & warna) ---
        if is_invisible:
            target_slider_x = float(BTN_W - RADIUS)
            target_bg_color = COLOR_ON
        else:
            target_slider_x = float(RADIUS)
            target_bg_color = COLOR_OFF

        anim_slider_x += (target_slider_x - anim_slider_x) * ANIM_SPEED
        anim_bg_color += (target_bg_color - anim_bg_color) * ANIM_SPEED

        # --- Deteksi tangan & telunjuk untuk menekan tombol toggle ---
        hands_results = hands.process(rgb_frame)
        if cooldown > 0:
            cooldown -= 1

        _, pressing_button = detect_finger_toggle_press(hands_results, frame, w, h)
        if pressing_button and cooldown == 0 and background is not None:
            is_invisible = not is_invisible
            cooldown = COOLDOWN_FRAMES

        # --- Pelacakan wajah untuk menampilkan kotak & label saat mode invisible ---
        face_results = face_detection.process(rgb_frame)
        current_bbox = detect_face_bbox(face_results, w, h)
        if current_bbox is not None:
            last_bbox = current_bbox

        # --- Render frame utama & tombol toggle ---
        display_frame = render_frame(frame, background, is_invisible, last_bbox, current_bbox)
        draw_toggle_button(display_frame, anim_slider_x, anim_bg_color, is_invisible)

        cv2.imshow('Smooth Beautiful Toggle', display_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
