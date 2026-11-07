"""Split one or more images into three vertical strips."""
from pathlib import Path
from tkinter import Tk, Button, Label, filedialog, messagebox
from PIL import Image


def split_image(file_path):
    source = Path(file_path)
    output_folder = source.parent / f"{source.stem} - Cut photo"
    output_folder.mkdir(parents=True, exist_ok=True)

    with Image.open(source) as image:
        # JPEG doesn't support transparency; use a white background when needed.
        if image.mode in ("RGBA", "LA") or "transparency" in image.info:
            rgba = image.convert("RGBA")
            background = Image.new("RGB", rgba.size, "white")
            background.paste(rgba, mask=rgba.getchannel("A"))
            image = background
        else:
            image = image.convert("RGB")

        width, height = image.size
        if width < 3:
            raise ValueError("The image must be at least 3 pixels wide.")

        for i in range(3):
            left = (i * width) // 3
            right = ((i + 1) * width) // 3
            strip = image.crop((left, 0, right, height))
            strip.save(output_folder / f"part_{i + 1}.jpg", quality=95)
    return output_folder


def select_and_process_images():
    files = filedialog.askopenfilenames(
        title="Select one or more images",
        filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")],
    )
    if not files:
        return

    success_count = 0
    errors = []
    for file_path in files:
        try:
            split_image(file_path)
            success_count += 1
        except Exception as exc:
            errors.append(f"{Path(file_path).name}: {exc}")

    summary = f"Processed {success_count} of {len(files)} image(s)."
    if errors:
        summary += "\n\nErrors:\n" + "\n".join(errors[:10])
        if len(errors) > 10:
            summary += f"\n... and {len(errors) - 10} more error(s)."
        messagebox.showwarning("Processing completed with errors", summary)
    else:
        messagebox.showinfo("Processing completed", summary)


def create_interface():
    window = Tk()
    window.title("Crop - Split Images into 3 Parts")
    window.geometry("450x170")
    Label(window, text="Split images into 3 vertical strips").pack(pady=(20, 8))
    Button(window, text="Select one or more images", command=select_and_process_images).pack(pady=8)
    window.mainloop()


if __name__ == "__main__":
    create_interface()
