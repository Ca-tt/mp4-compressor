import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD

class Application(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("CustomTkinter Drag and Drop Files")
        self.geometry("600x400")

        # Create an invisible frame that covers the entire window
        self.drop_frame = ctk.CTkFrame(self, width=600, height=400, fg_color="transparent")
        self.drop_frame.pack(fill="both", expand=True)
        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind('<<Drop>>', self.on_file_drop)

        # Label to display file paths
        self.file_paths = ctk.CTkLabel(self.drop_frame, text="", width=400, height=100, fg_color="white")
        self.file_paths.place(relx=0.5, rely=0.8, anchor="center")

    def on_file_drop(self, event):
        files = self.split_files(event.data)
        self.file_paths.configure(text="\n".join(files))

    def split_files(self, file_string):
        if file_string:
            files = file_string.split()
            files = [f.strip('{}') for f in files]  # Remove braces from paths with spaces
            return files
        return []

if __name__ == "__main__":
    ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
    
    app = Application()
    app.mainloop()
