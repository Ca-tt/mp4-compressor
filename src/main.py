import os
import subprocess
import customtkinter as ctk
from customtkinter import set_appearance_mode
import threading
from tkinter import filedialog
import time
from os import path
from tkinterdnd2 import TkinterDnD, DND_FILES
import re



class VideoCompressor:
    def __init__(self, original_file_path):
        self.original_file_path = path.normpath(original_file_path)
        self.new_compressed_file_name = "c_" + path.basename(self.original_file_path)
        self.compressed_file_path = path.normpath(
            path.join(path.expanduser("~/Desktop/"), self.new_compressed_file_name)
        )

    def compress_mp4(self, progress_callback=None):
        try:
            compressor_settings = [
                "ffmpeg",
                "-y",
                "-i",
                self.original_file_path,
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "23",
                "-c:a",
                "aac",
                "-b:a",
                "96k",
                "-movflags",
                "faststart",
                self.compressed_file_path,
            ]

            start_time = time.time()
            process = subprocess.Popen(
                compressor_settings,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW,
                text=True,
            )
            total_duration = None

            for line in process.stdout:
                if "Duration" in line and total_duration is None:
                    total_duration = self._get_duration_from_ffmpeg_output(line)
                elif "time=" in line:
                    current_time = self._get_time_from_ffmpeg_output(line)
                    if (
                        total_duration
                        and current_time is not None
                        and progress_callback
                    ):
                        progress = (current_time / total_duration) * 100
                        progress_callback(progress)

            process.wait()
            end_time = time.time()
            compression_time = end_time - start_time

            if process.returncode == 0:
                print("Video compression completed successfully.")
                if progress_callback:
                    progress_callback(100)
                return compression_time
            else:
                print(f"Error compressing video: {process.returncode}")
                return None

        except subprocess.CalledProcessError as e:
            print(f"Error compressing video: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    def _get_duration_from_ffmpeg_output(self, line):
        try:
            time_str = line.split("Duration: ")[1].split(",")[0].strip()
            return self._time_str_to_seconds(time_str)
        except (IndexError, ValueError) as e:
            print(f"Error parsing duration from ffmpeg output: {e}")
            return None

    def _get_time_from_ffmpeg_output(self, line):
        try:
            time_str = line.split("time=")[1].split(" ")[0].strip()
            return self._time_str_to_seconds(time_str)
        except (IndexError, ValueError) as e:
            print(f"Error parsing time from ffmpeg output: {e}")
            return None

    def _time_str_to_seconds(self, time_str):
        try:
            parts = time_str.split(":")
            if len(parts) == 3:
                h, m, s = map(float, parts)
                return h * 3600 + m * 60 + s
            else:
                return None
        except ValueError as e:
            print(f"Error converting time string to seconds: {e}")
            return None

    def get_file_info(self):
        try:
            command = ["ffmpeg", "-i", self.original_file_path, "-hide_banner"]
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            output = process.communicate()[0]

            duration = None
            for line in output.splitlines():
                if "Duration" in line:
                    duration = self._get_duration_from_ffmpeg_output(line)
                    break

            size = os.path.getsize(self.original_file_path) / (
                1024 * 1024
            )  # Size in MB

            return size, duration
        except Exception as e:
            print(f"Error getting file info: {e}")
            return None, None


class Interface:
    def __init__(self):
        self.window = TkinterDnD.Tk()   

        self.window_width = 400
        self.window_height = 350


        # static texts
        self.WINDOW_TITLE = "MP4 Compressor"
        self.CHOOSE_FILE_BUTTON_TEXT = "Выбери файл, чтобы начать"
        self.COMPRESS_BUTTON_TEXT = "Сжать файл"
        self.PROGRESS_LABEL_TEXT = "Прогресс"
        self.VIDEO_INFORMATION_START_TEXT = "Пока ничего не выбрано"
        self.ESTIMATED_COMPRESSION_TIME = "Примерное время сжатия"


        self.window.geometry(f"{self.window_width}x{self.window_height}")
        self.window.title(self.WINDOW_TITLE)

        self.active_theme = "light"
        set_appearance_mode(self.active_theme)

        self.center_window()

        self.video_compressor = None
        self.original_file_path = None
        self._compressed_file_path = None

        self.config_file_path = os.path.expanduser("~/compressor.json")

        self.create_widgets()
        self.place_widgets()
        self.configure_layout()
        self.bring_to_front()
        
        
        self.window.drop_target_register(DND_FILES)
        self.window.dnd_bind('<<Drop>>', self.on_drop)
        
        
    """ Window and widgets """
    def configure_layout(self):
        """set rows and columns width and height"""
        self.window.grid_columnconfigure((0, 1), weight=1)
        

    def bring_to_front(self):
        self.window.lift()
        self.window.attributes("-topmost", True)
        self.window.after_idle(self.window.attributes, "-topmost", False)
        
 
    def create_widgets(self):
        self.choose_file_button = ctk.CTkButton(
            self.window, text=self.CHOOSE_FILE_BUTTON_TEXT, height=50, command=self.choose_file
        )
        self.compress_button = ctk.CTkButton(
            self.window, text=self.COMPRESS_BUTTON_TEXT, state="disabled", height=35, command=self.compress_video
        )

        self.progress_label = ctk.CTkLabel(self.window, text=f"{self.PROGRESS_LABEL_TEXT} 0%")
        self.progress_bar = ctk.CTkProgressBar(
            self.window, width=self.window_width * 0.8
        )

        self.result_label = ctk.CTkLabel(self.window, text=self.VIDEO_INFORMATION_START_TEXT)


    def place_widgets(self):
        self.choose_file_button.grid(row=0, column=0, columnspan=4, pady=(15, 30))
        self.compress_button.grid(row=2, column=0, columnspan=4, pady=30)
        self.progress_label.grid(row=3, column=0, columnspan=4, padx=10, pady=(10, 0))
        self.progress_bar.grid(row=4, column=0, columnspan=4, padx=10, pady=(0, 10))
        self.progress_bar.set(0)
        self.result_label.grid(row=5, column=0, columnspan=4, padx=10, pady=(10, 10))


    def center_window(self):
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window_width // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window_height // 2)
        self.window.geometry(
            "{}x{}+{}+{}".format(self.window_width, self.window_height, x, y)
        )



    """ Video information """
    def display_video_data(self, file_path):
        self.original_file_path = path.normpath(file_path)
        
        try:
            self.video_compressor = VideoCompressor(self.original_file_path)
            self.video_size, self.video_duration = self.video_compressor.get_file_info()

            if self.video_size is not None and self.video_duration is not None:
                self.calculate_duration()
                self.display_video_information()
            else:
                self.result_label.configure(text="Не могу получить данные из файла.\nПопробуй переименовать файл")
        except Exception as e:
            self.result_label.configure(text=f"Error getting file info: {e}")
            print(f"Error: {e}")


    def calculate_duration(self):
        """ calculate hours, minutes and seconds using video duration (in seconds) """
        self.hours = int(self.video_duration // 60 // 60)
        self.minutes = int(self.video_duration - self.hours * 60 * 60) // 60
        self.seconds = int(self.video_duration - ( (self.hours * 60 * 60) + (self.minutes * 60) ))

    def display_video_information(self):
        if self.video_size is not None and self.video_duration is not None:
            self.result_label.configure(
                text=f"Размер файла: {self.video_size:.2f} MB\nДлительность: {str(self.hours) + ':' if int(self.hours) > 0 else ""}{self.minutes}:{self.seconds}"
            )
            self.compress_button.configure(state="normal")
        else: 
            self.result_label.configure(text="Не могу получить данные из файла.\nПопробуй переименовать файл")

    
    def _format_time(self, seconds):
        m, s = divmod(seconds, 60)
        return f"{int(m)}m {int(s)}s"
    

    def _compress_and_update_ui(self):
        compression_time = self.video_compressor.compress_mp4(self.update_progress)
        if compression_time is not None:
            original_size = os.path.getsize(self.original_file_path)
            compressed_size = os.path.getsize(self._compressed_file_path)
            compression_percent = (
                (original_size - compressed_size) / original_size
            ) * 100
            compression_time_str = self._format_time(compression_time)
            self.result_label.configure(
                text=f"Compression complete: {compression_percent:.2f}%\nNew file size: {compressed_size / (1024 * 1024):.2f} MB\nCompression time: {compression_time_str}"
            )
            self.compress_button.configure(state="normal")
            

        
    """ event handlers """
    
    """ dropdown """    
    def on_drop(self, event):
        file_path = event.data
        file_path = re.sub(r'[{}]', '', file_path).strip()
        
        self.display_video_data(file_path)


    """ choose file button """    
    def choose_file(self):
        file_path = filedialog.askopenfilename()
        
        self.display_video_data(file_path)
        
        
    """ progress bar updates """    
    def update_progress(self, progress):
        """ and window title """
        self.progress_bar.set(progress / 100)
        self.progress_label.configure(text=f"{self.PROGRESS_LABEL_TEXT}: {int(progress)}%")

        self.window.title(f"{int(progress)}% | {self.WINDOW_TITLE}")
        
    
    """ Compression """
    def compress_video(self):
        if self.original_file_path and os.path.isfile(self.original_file_path):
            self.compress_button.configure(state="disabled")
            self.choose_file_button.configure(state="disabled")

            self._new_compressed_file_name = "c_" + path.basename(
                self.original_file_path
            )
            self._compressed_file_path = path.normpath(
                path.join(path.expanduser("~/Desktop/"), self._new_compressed_file_name)
            )

            thread = threading.Thread(target=self._compress_and_update_ui)
            thread.start()
        else:
            print(f"Error: {self.original_file_path} not found")


    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    interface = Interface()
    interface.run()
