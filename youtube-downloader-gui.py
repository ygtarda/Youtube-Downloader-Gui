import customtkinter as ctk
from tkinter import filedialog
import yt_dlp
import threading
import os

# 🎨 Arayüz Teması
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AdvancedDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Pencere Ayarları
        self.title("Pro YouTube Downloader 🚀")
        self.geometry("600x550")
        self.resizable(False, False)

        # 1. Başlık Alanı
        self.header = ctk.CTkLabel(self, text="YouTube Video & Müzik İndirici", font=("Roboto", 22, "bold"))
        self.header.pack(pady=15)

        # 2. Link Girişi
        self.url_entry = ctk.CTkEntry(self, placeholder_text="YouTube linkini buraya yapıştır...", width=450, height=40)
        self.url_entry.pack(pady=10)

        # 3. Ayarlar Paneli (Frame)
        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.pack(pady=10, padx=20, fill="x")

        # 3a. Format Seçimi (MP4 / MP3)
        self.format_label = ctk.CTkLabel(self.settings_frame, text="Format:", font=("Roboto", 14))
        self.format_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.format_var = ctk.StringVar(value="Video (MP4)")
        self.format_menu = ctk.CTkOptionMenu(self.settings_frame, values=["Video (MP4)", "Sadece Ses (MP3)"], variable=self.format_var, command=self.update_quality_options)
        self.format_menu.grid(row=0, column=1, padx=10, pady=10)

        # 3b. Kalite Seçimi
        self.quality_label = ctk.CTkLabel(self.settings_frame, text="Kalite:", font=("Roboto", 14))
        self.quality_label.grid(row=0, column=2, padx=10, pady=10)

        self.quality_menu = ctk.CTkOptionMenu(self.settings_frame, values=["En İyi (720p+)", "Standart (480p)"])
        self.quality_menu.grid(row=0, column=3, padx=10, pady=10)

        # 4. Dosya Konumu Seçimi
        self.path_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.path_frame.pack(pady=10)

        self.path_entry = ctk.CTkEntry(self.path_frame, placeholder_text="İndirilecek Klasör", width=350, state="disabled")
        self.path_entry.pack(side="left", padx=5)
        
        # Varsayılan olarak masaüstünü ayarla
        self.download_path = os.path.join(os.path.expanduser("~"), "Desktop")
        self.path_entry.configure(state="normal")
        self.path_entry.insert(0, self.download_path)
        self.path_entry.configure(state="disabled")

        self.browse_btn = ctk.CTkButton(self.path_frame, text="Seç 📂", width=80, command=self.select_directory)
        self.browse_btn.pack(side="left", padx=5)

        # 5. İlerleme Çubuğu ve Yüzde
        self.progress_label = ctk.CTkLabel(self, text="0%", font=("Roboto", 16, "bold"))
        self.progress_label.pack(pady=(20, 0))

        self.progress_bar = ctk.CTkProgressBar(self, width=450)
        self.progress_bar.set(0) # Başlangıçta 0
        self.progress_bar.pack(pady=5)

        self.status_label = ctk.CTkLabel(self, text="Hazır", text_color="gray")
        self.status_label.pack(pady=5)

        # 6. İndir Butonu
        self.download_btn = ctk.CTkButton(self, text="İNDİRMEYİ BAŞLAT ⬇️", command=self.start_download_thread, height=50, width=450, font=("Roboto", 16, "bold"), fg_color="#2CC985", hover_color="#24A36B")
        self.download_btn.pack(pady=20)

    def select_directory(self):
        path = filedialog.askdirectory()
        if path:
            self.download_path = path
            self.path_entry.configure(state="normal")
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, self.download_path)
            self.path_entry.configure(state="disabled")

    def update_quality_options(self, choice):
        if choice == "Sadece Ses (MP3)":
            self.quality_menu.configure(values=["En İyi Ses"])
            self.quality_menu.set("En İyi Ses")
        else:
            self.quality_menu.configure(values=["En İyi (720p+)", "Standart (480p)"])
            self.quality_menu.set("En İyi (720p+)")

    def start_download_thread(self):
        link = self.url_entry.get()
        if not link:
            self.status_label.configure(text="❌ Lütfen bir link girin!", text_color="red")
            return
        
        self.download_btn.configure(state="disabled", text="İndiriliyor...")
        self.status_label.configure(text="⏳ Bağlanıyor...", text_color="orange")
        self.progress_bar.set(0)
        
        threading.Thread(target=self.download_content, args=(link,)).start()

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                # Yüzdeyi hesapla ve güncelle
                p = d.get('_percent_str', '0%').replace('%', '')
                progress_val = float(p) / 100
                self.progress_bar.set(progress_val)
                self.progress_label.configure(text=f"%{int(progress_val * 100)}")
                self.status_label.configure(text=f"İndiriliyor... {d.get('_speed_str', '')}", text_color="white")
            except:
                pass
        elif d['status'] == 'finished':
            self.status_label.configure(text="✅ İndirme Tamamlandı! Dönüştürülüyor...", text_color="#2CC985")
            self.progress_bar.set(1)
            self.progress_label.configure(text="100%")

    def download_content(self, link):
        try:
            ydl_opts = {
                'outtmpl': f'{self.download_path}/%(title)s.%(ext)s',
                'progress_hooks': [self.progress_hook],
                'nocheckcertificate': True,
                'ignoreerrors': True,
                'restrictfilenames': True,  # Dosya isimlerindeki garip karakterleri düzeltir
            }

            format_choice = self.format_var.get()
            quality_choice = self.quality_menu.get()

            if format_choice == "Sadece Ses (MP3)":
                # Ses indirme ayarları (M4A indirip garanti olsun diye)
                ydl_opts['format'] = 'bestaudio/best'
            else:
                # Video İndirme Ayarları (SES SORUNU ÇÖZÜMÜ)
                # 'best[ext=mp4]' kullanarak hem ses hem görüntünün olduğu tek dosyayı seçiyoruz.
                # Bu sayede FFmpeg olmadan da ses garanti gelir.
                if quality_choice == "Standart (480p)":
                     ydl_opts['format'] = 'best[height<=480][ext=mp4]/best[height<=480]'
                else:
                    # En iyi kalite (Genelde 720p sesli)
                     ydl_opts['format'] = 'best[ext=mp4]/best'

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])
            
            self.status_label.configure(text="✅ İşlem Başarılı! Dosya Klasörde.", text_color="#2CC985")
            
        except Exception as e:
            self.status_label.configure(text="❌ Bir hata oluştu!", text_color="red")
            print(e)
        
        finally:
            self.download_btn.configure(state="normal", text="İNDİRMEYİ BAŞLAT ⬇️")

if __name__ == "__main__":
    app = AdvancedDownloader()
    app.mainloop()