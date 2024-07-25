import os
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
from reportlab.pdfgen import canvas

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


def gif_to_pdf(gif_path, pdf_path, progress_callback=None):
    with Image.open(gif_path) as img:
        width, height = img.size
        c = canvas.Canvas(pdf_path, pagesize=(width, height))

        try:
            for frame in range(0, img.n_frames):
                if progress_callback:
                    progress_callback(frame, img.n_frames)
                img.seek(frame)
                rgb_frame = img.convert('RGB')
                temp_jpg = f"temp_frame_{frame}.jpg"
                rgb_frame.save(temp_jpg)
                c.drawImage(temp_jpg, 0, 0, width, height)
                c.showPage()
                os.remove(temp_jpg)

            c.save()
            return True
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return False


class GifToPdfConverter(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Multi-file GIF to PDF Converter")
        self.geometry("600x400")

        self.gif_paths = []
        self.total_frames = 0

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(4, weight=1)

        self.select_button = ctk.CTkButton(self.main_frame, text="Select GIF Files", command=self.browse_gifs)
        self.select_button.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        self.files_label = ctk.CTkLabel(self.main_frame, text="No files selected")
        self.files_label.grid(row=1, column=0, padx=20, pady=10)

        self.progress = ctk.CTkProgressBar(self.main_frame)
        self.progress.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.progress.set(0)

        self.status_label = ctk.CTkLabel(self.main_frame, text="")
        self.status_label.grid(row=3, column=0, padx=20, pady=10)

        self.convert_button = ctk.CTkButton(self.main_frame, text="Convert", command=self.start_conversion)
        self.convert_button.grid(row=4, column=0, padx=20, pady=(10, 20), sticky="ew")

    def browse_gifs(self):
        filenames = filedialog.askopenfilenames(filetypes=[("GIF files", "*.gif")])
        self.gif_paths = list(filenames)
        self.files_label.configure(text=f"{len(self.gif_paths)} files selected")

        # Count total frames
        self.total_frames = 0
        for gif_path in self.gif_paths:
            with Image.open(gif_path) as img:
                self.total_frames += img.n_frames

    def start_conversion(self):
        if not self.gif_paths:
            messagebox.showerror("Error", "Please select GIF files to convert.")
            return

        self.progress.set(0)
        self.convert_button.configure(state="disabled")

        conversion_thread = threading.Thread(target=self.convert_files)
        conversion_thread.start()

    def convert_files(self):
        frames_converted = 0
        for i, gif_path in enumerate(self.gif_paths):
            pdf_path = os.path.splitext(gif_path)[0] + ".pdf"
            self.status_label.configure(text=f"Converting {os.path.basename(gif_path)}...")

            def update_progress(frame, total_frames):
                nonlocal frames_converted
                frames_converted += 1
                progress = frames_converted / self.total_frames
                self.progress.set(progress)
                self.update_idletasks()

            success = gif_to_pdf(gif_path, pdf_path, progress_callback=update_progress)

            if not success:
                messagebox.showerror("Error", f"Failed to convert {os.path.basename(gif_path)}")

        self.status_label.configure(text="Conversion completed!")
        self.convert_button.configure(state="normal")
        messagebox.showinfo("Success", "All files have been converted!")


if __name__ == "__main__":
    app = GifToPdfConverter()
    app.mainloop()