import os
import threading
import time
import multiprocessing
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Version string (update this or pass via build script)
__version__ = "0.0.1"

# Ensure multiprocessing behaves correctly in frozen executables (PyInstaller)
# and prevents worker processes from re‑launching the GUI when spawn is used.
multiprocessing.freeze_support()

# import the programmatic functions from the other scripts
from webpconvert import convert_folder
from upload_dataset import upload_with_progress, generate_presigned_url, ensure_credentials


class ConvertFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.src_var = tk.StringVar()
        self.dst_var = tk.StringVar()
        self.delete_var = tk.BooleanVar(value=False)

        # source directory
        ttk.Label(self, text="Source folder:").grid(row=0, column=0, sticky="w")
        src_entry = ttk.Entry(self, textvariable=self.src_var, width=50)
        src_entry.grid(row=0, column=1, sticky="we", padx=2)
        ttk.Button(self, text="Browse...", command=self.browse_source).grid(row=0, column=2)
        ttk.Button(self, text="Open", command=lambda: self.open_folder(self.src_var.get())).grid(row=0, column=3)

        # destination directory
        ttk.Label(self, text="Destination folder:").grid(row=1, column=0, sticky="w")
        dst_entry = ttk.Entry(self, textvariable=self.dst_var, width=50)
        dst_entry.grid(row=1, column=1, sticky="we", padx=2)
        ttk.Button(self, text="Browse...", command=self.browse_dest).grid(row=1, column=2)
        ttk.Button(self, text="Open", command=lambda: self.open_folder(self.dst_var.get())).grid(row=1, column=3)

        # delete option
        ttk.Checkbutton(self, text="Delete source files/folders", variable=self.delete_var).grid(row=2, column=0, columnspan=4, sticky="w")

        # start button
        self.convert_button = ttk.Button(self, text="Start conversion", command=self.start_conversion)
        self.convert_button.grid(row=3, column=0, columnspan=4, pady=4)

        # progress bar
        self.progress = ttk.Progressbar(self, length=400)
        self.progress.grid(row=4, column=0, columnspan=4, pady=4)

        # log text
        self.log_text = tk.Text(self, height=10)
        self.log_text.grid(row=5, column=0, columnspan=4, sticky="nsew")
        self.grid_rowconfigure(5, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def browse_source(self):
        d = filedialog.askdirectory()
        if d:
            self.src_var.set(d)

    def browse_dest(self):
        d = filedialog.askdirectory()
        if d:
            self.dst_var.set(d)

    def open_folder(self, path):
        if path and os.path.isdir(path):
            try:
                os.startfile(path)
            except Exception:
                pass

    def start_conversion(self):
        src = self.src_var.get().strip()
        dst = self.dst_var.get().strip()
        if not src or not os.path.isdir(src):
            messagebox.showerror("Error", "Please select a valid source folder.")
            return
        if not dst:
            messagebox.showerror("Error", "Please select a destination folder.")
            return

        self.progress['value'] = 0
        self.log_text.delete('1.0', tk.END)
        self.convert_button.config(state='disabled')
        threading.Thread(target=self.run_conversion, args=(src, dst, self.delete_var.get()), daemon=True).start()

    def run_conversion(self, src, dst, delete):
        def progress_cb(count, total):
            self.progress['maximum'] = total
            self.progress['value'] = count

        def log_cb(msg):
            self.log_text.insert(tk.END, msg + "\n")
            self.log_text.see(tk.END)

        zip_path = convert_folder(src, dst, delete_source=delete,
                                  progress_callback=progress_cb,
                                  log_callback=log_cb)
        log_cb(f"Finished: {zip_path}")
        self.convert_button.config(state='normal')


class UploadFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.file_var = tk.StringVar()
        self.key_var = tk.StringVar()
        self.bucket_var = tk.StringVar(value=os.environ.get("TACOPS_BUCKET", "tacops-map-images"))
        self.region_var = tk.StringVar(value=os.environ.get("AWS_DEFAULT_REGION", "eu-central-1"))
        self.expiry_var = tk.IntVar(value=604800)
        self.url_var = tk.StringVar()

        ttk.Label(self, text="Zip file:").grid(row=0, column=0, sticky="w")
        ttk.Entry(self, textvariable=self.file_var, width=50).grid(row=0, column=1, sticky="we", padx=2)
        ttk.Button(self, text="Browse...", command=self.browse_file).grid(row=0, column=2)

        ttk.Label(self, text="S3 key:").grid(row=1, column=0, sticky="w")
        ttk.Entry(self, textvariable=self.key_var, width=50).grid(row=1, column=1, columnspan=2, sticky="we", padx=2)

        ttk.Label(self, text="Bucket:").grid(row=2, column=0, sticky="w")
        ttk.Entry(self, textvariable=self.bucket_var).grid(row=2, column=1, sticky="we", padx=2)
        ttk.Label(self, text="Region:").grid(row=2, column=2, sticky="w")
        ttk.Entry(self, textvariable=self.region_var).grid(row=2, column=3, sticky="we", padx=2)

        ttk.Label(self, text="Expiry (s):").grid(row=3, column=0, sticky="w")
        ttk.Entry(self, textvariable=self.expiry_var).grid(row=3, column=1, sticky="w", padx=2)

        self.upload_button = ttk.Button(self, text="Start upload", command=self.start_upload)
        self.upload_button.grid(row=4, column=0, columnspan=4, pady=4)

        self.progress = ttk.Progressbar(self, length=400)
        self.progress.grid(row=5, column=0, columnspan=4, pady=4)
        self.status_label = ttk.Label(self, text="")
        self.status_label.grid(row=6, column=0, columnspan=4)

        ttk.Label(self, text="Download URL:").grid(row=7, column=0, sticky="w")
        url_entry = ttk.Entry(self, textvariable=self.url_var, width=50)
        url_entry.grid(row=7, column=1, columnspan=2, sticky="we", padx=2)
        ttk.Button(self, text="Copy", command=self.copy_url).grid(row=7, column=3)

        self.grid_columnconfigure(1, weight=1)

        self.bytes_transferred = 0

    def browse_file(self):
        f = filedialog.askopenfilename(filetypes=[("Zip files", "*.zip"), ("All files", "*")])
        if f:
            self.file_var.set(f)
            self.key_var.set(os.path.basename(f))

    def start_upload(self):
        path = self.file_var.get().strip()
        if not path or not os.path.isfile(path):
            messagebox.showerror("Error", "Please select a valid zip file.")
            return
        self.upload_button.config(state='disabled')
        self.progress['value'] = 0
        self.status_label.config(text="")
        self.bytes_transferred = 0
        threading.Thread(target=self.run_upload, daemon=True).start()

    def run_upload(self):
        ensure_credentials()
        file_path = self.file_var.get()
        bucket = self.bucket_var.get()
        key = self.key_var.get()
        region = self.region_var.get()
        expiry = self.expiry_var.get()

        # ensure upload_dataset uses desired region
        import upload_dataset
        upload_dataset.REGION = region

        start_time = time.time()
        total_size = os.path.getsize(file_path)
        self.progress['maximum'] = total_size

        def progress_cb(bytes_transferred):
            self.bytes_transferred += bytes_transferred
            elapsed = time.time() - start_time
            speed = (self.bytes_transferred / elapsed) if elapsed > 0 else 0
            percent = (self.bytes_transferred / total_size * 100) if total_size else 0
            self.progress['value'] = self.bytes_transferred
            self.status_label.config(text=f"{percent:.1f}% ({speed/1024:.1f} KB/s)")

        try:
            s3 = upload_with_progress(file_path, bucket, key, progress_callback=progress_cb)
            url = generate_presigned_url(s3, bucket, key, expiry)
            self.url_var.set(url)
        except Exception as e:
            messagebox.showerror("Upload failed", str(e))
        finally:
            self.upload_button.config(state='normal')

    def copy_url(self):
        self.clipboard_clear()
        self.clipboard_append(self.url_var.get())


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"Tacops Screen Capture Tools v{__version__}")
        self.geometry("700x500")
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)
        notebook.add(ConvertFrame(notebook), text="Convert")
        notebook.add(UploadFrame(notebook), text="Upload")



def main():
    app = App()
    app.mainloop()


if __name__ == '__main__':
    # multiprocessing.freeze_support() has already been called above when the
    # module was imported, but call it again here for good measure.
    multiprocessing.freeze_support()
    main()
