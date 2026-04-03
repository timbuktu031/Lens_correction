import customtkinter as ctk
from tkinter import filedialog
import cv2
from PIL import Image
import numpy as np
import os
import subprocess

class FPVFixerPro(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FPV Lens Corrector Pro")
        self.geometry("1200x800")
        
        # 데이터 초기화
        self.input_path = ""
        self.cap = None
        self.total_frames = 0
        self.fps = 30
        self.preview_size = (720, 405)

        # UI 레이아웃
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 패널 설정
        self.sidebar = ctk.CTkFrame(self, width=300)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.main_panel = ctk.CTkFrame(self)
        self.main_panel.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.init_sidebar()
        self.init_main_panel()

    def init_sidebar(self):
        # 1. 파일 선택
        ctk.CTkLabel(self.sidebar, text="1. 영상 선택", font=("Arial", 18, "bold")).pack(pady=(20, 10))
        self.btn_browse = ctk.CTkButton(self.sidebar, text="파일 찾기", command=self.browse_file)
        self.btn_browse.pack(pady=5)
        self.path_label = ctk.CTkLabel(self.sidebar, text="파일 없음", font=("Arial", 11), text_color="gray")
        self.path_label.pack(pady=5)

        # 2. 구간 설정 (양방향 동기화: 엔터 및 포커스 아웃 바인딩)
        ctk.CTkLabel(self.sidebar, text="2. 구간 설정 (시:분:초)", font=("Arial", 18, "bold")).pack(pady=(30, 10))
        
        self.start_entry = ctk.CTkEntry(self.sidebar, justify="center", width=150)
        self.start_entry.insert(0, "00:00:00")
        self.start_entry.pack(pady=5)
        self.start_entry.bind("<Return>", lambda e: self.sync_entry_to_slider("start"))
        self.start_entry.bind("<FocusOut>", lambda e: self.sync_entry_to_slider("start"))

        self.end_entry = ctk.CTkEntry(self.sidebar, justify="center", width=150)
        self.end_entry.insert(0, "00:00:00")
        self.end_entry.pack(pady=5)
        self.end_entry.bind("<Return>", lambda e: self.sync_entry_to_slider("end"))
        self.end_entry.bind("<FocusOut>", lambda e: self.sync_entry_to_slider("end"))

        # 3. 왜곡 보정 조절
        ctk.CTkLabel(self.sidebar, text="3. 왜곡 보정 조절", font=("Arial", 18, "bold")).pack(pady=(30, 10))
        
        self.k1_label = ctk.CTkLabel(self.sidebar, text="중앙부 (k1): -0.400")
        self.k1_label.pack()
        self.k1_slider = ctk.CTkSlider(self.sidebar, from_=-1.0, to=0.0, command=self.refresh_preview)
        self.k1_slider.set(-0.400)
        self.k1_slider.pack(pady=5)

        self.k2_label = ctk.CTkLabel(self.sidebar, text="외곽부 (k2): 0.000")
        self.k2_label.pack()
        self.k2_slider = ctk.CTkSlider(self.sidebar, from_=-1.0, to=0.0, command=self.refresh_preview)
        self.k2_slider.set(0.000)
        self.k2_slider.pack(pady=5)

        # 실행 버튼 (검정 글씨로 시인성 확보)
        self.btn_run = ctk.CTkButton(self.sidebar, text="전체 영상 교정 시작", 
                                     fg_color="#2ECC71", text_color="black", 
                                     hover_color="#27AE60", height=50, font=("Arial", 15, "bold"),
                                     command=self.process_video)
        self.btn_run.pack(side="bottom", pady=40, fill="x", padx=20)

    def init_main_panel(self):
        self.img_label = ctk.CTkLabel(self.main_panel, text="영상을 불러와주세요", width=720, height=405, fg_color="#1A1A1A")
        self.img_label.pack(pady=(20, 10), expand=True)

        ctk.CTkLabel(self.main_panel, text="시작점 조절", font=("Arial", 11)).pack()
        self.start_slider = ctk.CTkSlider(self.main_panel, from_=0, to=100, command=self.handle_start_slider)
        self.start_slider.set(0)
        self.start_slider.pack(fill="x", padx=50, pady=5)

        ctk.CTkLabel(self.main_panel, text="종료점 조절", font=("Arial", 11)).pack()
        self.end_slider = ctk.CTkSlider(self.main_panel, from_=0, to=100, command=self.handle_end_slider)
        self.end_slider.set(100)
        self.end_slider.pack(fill="x", padx=50, pady=5)

    def sync_entry_to_slider(self, mode):
        """텍스트 입력값을 슬라이더 위치로 변환 및 화면 갱신 (FocusOut 반영)"""
        if not self.cap: return

        try:
            time_str = self.start_entry.get() if mode == "start" else self.end_entry.get()
            parts = list(map(int, time_str.split(':')))
            
            if len(parts) == 3: # HH:MM:SS
                total_seconds = parts[0] * 3600 + parts[1] * 60 + parts[2]
            elif len(parts) == 2: # MM:SS
                total_seconds = parts[0] * 60 + parts[1]
            else:
                total_seconds = parts[0]

            target_frame = int(total_seconds * self.fps)
            target_frame = max(0, min(target_frame, self.total_frames - 1))

            if mode == "start":
                if target_frame > self.end_slider.get(): target_frame = self.end_slider.get()
                self.start_slider.set(target_frame)
                self.handle_start_slider(target_frame)
            else:
                if target_frame < self.start_slider.get(): target_frame = self.start_slider.get()
                self.end_slider.set(target_frame)
                self.handle_end_slider(target_frame)
        except ValueError:
            pass 

    def browse_file(self):
        path = filedialog.askopenfilename(filetypes=[("Video", "*.mp4 *.mov *.mkv")])
        if path:
            self.input_path = path
            self.path_label.configure(text=os.path.basename(path), text_color="white")
            self.cap = cv2.VideoCapture(path)
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)

            self.start_slider.configure(from_=0, to=self.total_frames - 1)
            self.end_slider.configure(from_=0, to=self.total_frames - 1)
            self.start_slider.set(0)
            self.end_slider.set(self.total_frames - 1)
            
            self.update_time_text(self.start_entry, 0)
            self.update_time_text(self.end_entry, self.total_frames - 1)
            self.load_and_show_frame(0)

    def handle_start_slider(self, value):
        if value > self.end_slider.get():
            self.start_slider.set(self.end_slider.get())
            value = self.end_slider.get()
        self.update_time_text(self.start_entry, value)
        self.load_and_show_frame(int(value))

    def handle_end_slider(self, value):
        if value < self.start_slider.get():
            self.end_slider.set(self.start_slider.get())
            value = self.start_slider.get()
        self.update_time_text(self.end_entry, value)
        self.load_and_show_frame(int(value))

    def update_time_text(self, entry, frame_idx):
        seconds = frame_idx / self.fps
        h, m, s = int(seconds // 3600), int((seconds % 3600) // 60), int(seconds % 60)
        entry.delete(0, 'end')
        entry.insert(0, f"{h:02d}:{m:02d}:{s:02d}")

    def load_and_show_frame(self, frame_idx):
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = self.cap.read()
            if ret:
                self.raw_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.refresh_preview()

    def refresh_preview(self, _=None):
        if not hasattr(self, 'raw_frame'): return
        k1, k2 = self.k1_slider.get(), self.k2_slider.get()
        self.k1_label.configure(text=f"중앙부 (k1): {k1:.3f}")
        self.k2_label.configure(text=f"외곽부 (k2): {k2:.3f}")

        h, w = self.raw_frame.shape[:2]
        cam_matrix = np.array([[w, 0, w/2], [0, w, h/2], [0, 0, 1]], dtype=np.float32)
        dist_coeffs = np.array([k1, k2, 0, 0], dtype=np.float32)
        
        new_cam_mtx, _ = cv2.getOptimalNewCameraMatrix(cam_matrix, dist_coeffs, (w,h), 1, (w,h))
        fixed = cv2.undistort(self.raw_frame, cam_matrix, dist_coeffs, None, new_cam_mtx)
        
        img = Image.fromarray(cv2.resize(fixed, self.preview_size))
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=self.preview_size)
        self.img_label.configure(image=ctk_img, text="")

    def process_video(self):
        if not self.input_path: return
        start_t, end_t = self.start_entry.get(), self.end_entry.get()
        k1, k2 = self.k1_slider.get(), self.k2_slider.get()
        
        # 보정 계수 적용: FFmpeg은 OpenCV보다 민감하므로 수치를 낮춤
        ffmpeg_k1, ffmpeg_k2 = k1 * 0.6, k2 * 0.6
        output_path = os.path.splitext(self.input_path)[0] + "_fixed_final.mp4"

        # FFmpeg 명령어 구성 (lenscorrection 필터 적용)
        cmd = [
            'ffmpeg', '-y', '-i', self.input_path,
            '-ss', start_t, '-to', end_t,
            '-vf', f'lenscorrection=k1={ffmpeg_k1}:k2={ffmpeg_k2}',
            '-c:v', 'libx264', '-crf', '18', '-c:a', 'copy', output_path
        ]
        
        self.btn_run.configure(text="작업 중...", state="disabled")
        self.update()
        try:
            # 윈도우 환경에서 안정적인 실행을 위해 subprocess.run 사용
            subprocess.run(cmd, check=True, shell=True)
            self.path_label.configure(text="저장 완료!", text_color="#2ECC71")
        except Exception as e:
            self.path_label.configure(text="변환 실패", text_color="red")
            print(f"Error: {e}")
        self.btn_run.configure(text="전체 영상 교정 시작", state="normal")

if __name__ == "__main__":
    app = FPVFixerPro()
    app.mainloop()