import cv2
import os
import sys
import zipfile
from pathlib import Path
import send2trash
import re
from concurrent.futures import ProcessPoolExecutor, as_completed

# default configuration (used by CLI; override via environment variables)
ROOT_FOLDER = os.environ.get("TACOPS_SOURCE", "")
ZIP_OUTPUT_FOLDER = os.environ.get("TACOPS_OUTPUT", "")

# Create output folder if it doesn't exist (CLI only)
if ZIP_OUTPUT_FOLDER:
    os.makedirs(ZIP_OUTPUT_FOLDER, exist_ok=True)

def parse_png_filename(filename):
    """Extract map name, x value, and y value from PNG filename
    Expected format: <map_name>_<x>_<y>.png
    """
    match = re.match(r'^(.+?)_(\d+)_(\d+)\.png$', filename, re.IGNORECASE)
    if match:
        return match.group(1), int(match.group(2)), int(match.group(3))
    return None, None, None

def convert_png_to_webp(png_file_path):
    """Convert PNG to WebP"""
    try:
        # Read the PNG image
        png_img = cv2.imread(png_file_path, cv2.IMREAD_UNCHANGED)
        
        if png_img is None:
            print(f"Error: Could not read image from {png_file_path}")
            return None
        
        # Create WebP file path
        webp_file_path = png_file_path.replace('.png', '.webp')
        
        # Convert to WebP
        success = cv2.imwrite(webp_file_path, png_img, [int(cv2.IMWRITE_WEBP_QUALITY), 100])
        
        if not success:
            print(f"Error: Failed to convert {png_file_path} to WebP")
            return None
        
        return webp_file_path
        
    except Exception as e:
        print(f"Error processing {png_file_path}: {e}")
        return None

def move_to_recycle_bin(file_path):
    """Move file to recycle bin"""
    try:
        send2trash.send2trash(file_path)
        print(f"Moved to recycle bin: {file_path}")
        return True
    except Exception as e:
        print(f"Error moving {file_path} to recycle bin: {e}")
        return False

def process_png(png_file_path):
    """Worker: convert a single PNG and recycle the original."""
    webp = convert_png_to_webp(png_file_path)
    if webp:
        move_to_recycle_bin(png_file_path)
        # return relative path for zipping + coords tuple
        filename = os.path.basename(png_file_path)
        mapname, x, y = parse_png_filename(filename)
        rel = os.path.relpath(webp, ROOT_FOLDER).replace('\\','/')
        return webp, rel, mapname, x, y
    return None


def convert_folder(root_folder, zip_output_folder, delete_source=False,
                   progress_callback=None, log_callback=print):
    """Convert pngs and zip, with optional callbacks.

    progress_callback(count, total) will be called each file.
    log_callback(msg) is used for logging.
    """
    os.makedirs(zip_output_folder, exist_ok=True)
    png_paths = []
    for root, dirs, files in os.walk(root_folder):
        for f in files:
            if f.lower().endswith('.png'):
                png_paths.append(os.path.join(root, f))

    total = len(png_paths)
    log_callback(f"Found {total} PNGs at {root_folder}")

    webp_files = []
    map_name = None
    xs = []
    ys = []

    count = 0
    # use parallel executor for conversion
    with ProcessPoolExecutor() as pool:
        futures = {pool.submit(process_png, p): p for p in png_paths}
        for fut in as_completed(futures):
            count += 1
            png_file_path = futures[fut]
            rel = os.path.relpath(png_file_path, root_folder)
            try:
                res = fut.result()
            except Exception as e:
                log_callback(f"Error converting {rel}: {e}")
                res = None

            if res:
                webp, relative_webp, m, x, y = res
                webp_files.append((webp, relative_webp))
                if map_name is None and m:
                    map_name = m
                if x is not None:
                    xs.append(x); ys.append(y)
            else:
                log_callback(f"Failed to convert: {rel}")

            log_callback(f"Processed ({count}/{total}): {rel}")
            if progress_callback:
                progress_callback(count, total)

    if map_name and xs and ys:
        min_x = min(xs); max_x = max(xs)
        min_y = min(ys); max_y = max(ys)
        zip_name = f"{map_name}_{min_x}-{min_y}_{max_x}-{max_y}.zip"
    else:
        zip_name = 'webp_images.zip'

    zip_path = os.path.join(zip_output_folder, zip_name)

    if webp_files:
        log_callback(f"Creating zip archive: {zip_path}")
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for webp_file_path, relative_path in webp_files:
                    zipf.write(webp_file_path, arcname=relative_path)
                    log_callback(f"Added to zip: {relative_path}")
        except Exception as e:
            log_callback(f"Error creating zip: {e}")
            return None

        for webp_file_path, _ in webp_files:
            try:
                os.remove(webp_file_path)
            except Exception:
                pass

        if delete_source:
            for dirpath, dirnames, filenames in os.walk(root_folder, topdown=False):
                if not dirnames and not filenames:
                    try:
                        os.rmdir(dirpath)
                    except Exception:
                        pass

    else:
        log_callback("No WebP files generated; skipping zip.")
        return None

    log_callback(f"Conversion complete; zip created: {zip_path}")
    return zip_path

def main():
    # CLI entrypoint uses environment variable globals and always deletes source directories
    if not ROOT_FOLDER or not os.path.isdir(ROOT_FOLDER):
        print("Error: TACOPS_SOURCE environment variable not set or folder does not exist.")
        sys.exit(1)
    if not ZIP_OUTPUT_FOLDER:
        print("Error: TACOPS_OUTPUT environment variable not set.")
        sys.exit(1)
    print(f"Starting PNG to WebP conversion from: {ROOT_FOLDER}\n")
    convert_folder(ROOT_FOLDER, ZIP_OUTPUT_FOLDER, delete_source=True)

if __name__ == '__main__':
    main()