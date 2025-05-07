import os
import ttkbootstrap as ttk
from tkinter import filedialog, colorchooser
from tkinter.messagebox import showerror
from PIL import Image, ImageOps, ImageTk, ImageFilter, ImageDraw

# — Config
CANVAS_W, CANVAS_H = 750, 560
TOOLBAR_W = 200

# — Globals
file_path = ""
original_image = None
current_image = None
image_draw = None
photo_image = None
pen_color = "black"
pen_size = 3
is_flipped_vert = False
rotation_angle = 0

# — Helpers
script_dir = os.path.dirname(os.path.abspath(__file__))
icons_dir = os.path.join(script_dir, "icons")

def load_icon(name, size=(24,24)):
    """Try to load icon; return PhotoImage or None if missing."""
    path = os.path.join(icons_dir, name)
    if not os.path.isfile(path):
        return None
    try:
        img = Image.open(path).resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None

def update_canvas_image():
    global photo_image
    display = current_image.resize((CANVAS_W, CANVAS_H), Image.LANCZOS)
    photo_image = ImageTk.PhotoImage(display)
    canvas.delete("all")
    canvas.create_image(0, 0, anchor="nw", image=photo_image)

# — Actions
def open_image():
    global file_path, original_image, current_image, image_draw
    path = filedialog.askopenfilename(
        title="Open Image File",
        filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.gif;*.bmp")]
    )
    if not path:
        return
    file_path = path
    img = Image.open(path).resize((CANVAS_W, CANVAS_H), Image.LANCZOS)
    original_image = img.copy()
    current_image = img.copy()
    image_draw = ImageDraw.Draw(current_image)
    update_canvas_image()

def flip_image():
    global current_image, image_draw, is_flipped_vert
    if current_image is None:
        showerror("Error", "Please open an image first!")
        return
    mode = Image.FLIP_TOP_BOTTOM if not is_flipped_vert else Image.FLIP_LEFT_RIGHT
    current_image = current_image.transpose(mode)
    image_draw = ImageDraw.Draw(current_image)
    is_flipped_vert = not is_flipped_vert
    update_canvas_image()

def rotate_image():
    global current_image, image_draw, rotation_angle
    if current_image is None:
        showerror("Error", "Please open an image first!")
        return
    rotation_angle = (rotation_angle + 90) % 360
    current_image = (
        current_image
        .rotate(rotation_angle, expand=True)
        .resize((CANVAS_W, CANVAS_H), Image.LANCZOS)
    )
    image_draw = ImageDraw.Draw(current_image)
    update_canvas_image()

def apply_filter(event=None):
    global current_image, image_draw
    if current_image is None:
        showerror("Error", "Please open an image first!")
        return
    f = filter_combobox.get()
    img = current_image
    if f == "Black and White":
        img = ImageOps.grayscale(img).convert("RGB")
    elif f == "Blur":
        img = img.filter(ImageFilter.BLUR)
    elif f == "Contour":
        img = img.filter(ImageFilter.CONTOUR)
    elif f == "Detail":
        img = img.filter(ImageFilter.DETAIL)
    elif f == "Emboss":
        img = img.filter(ImageFilter.EMBOSS)
    elif f == "Edge Enhance":
        img = img.filter(ImageFilter.EDGE_ENHANCE)
    elif f == "Sharpen":
        img = img.filter(ImageFilter.SHARPEN)
    elif f == "Smooth":
        img = img.filter(ImageFilter.SMOOTH)
    current_image = img
    image_draw = ImageDraw.Draw(current_image)
    update_canvas_image()

def draw(event):
    if current_image is None:
        return
    x, y = event.x, event.y
    # Canvas
    canvas.create_oval(
        x-pen_size, y-pen_size, x+pen_size, y+pen_size,
        fill=pen_color, outline=""
    )
    # PIL
    image_draw.ellipse(
        [(x-pen_size, y-pen_size), (x+pen_size, y+pen_size)],
        fill=pen_color, outline=None
    )

def change_color():
    global pen_color
    c = colorchooser.askcolor(title="Select Pen Color")
    if c[1]:
        pen_color = c[1]

def erase_lines():
    if original_image is None:
        return
    # Reset back to original image (no drawings)
    current_image.paste(original_image)
    image_draw = ImageDraw.Draw(current_image)
    update_canvas_image()

def save_image():
    if current_image is None:
        showerror("Error", "Nothing to save!")
        return
    save_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")]
    )
    if save_path:
        current_image.save(save_path)

# — UI Setup
root = ttk.Window(themename="cosmo")
root.title("Image Editor")
root.geometry(f"{TOOLBAR_W+CANVAS_W}x{CANVAS_H}+300+110")
root.resizable(False, False)

# Window icon (falls back silently)
win_icon = load_icon("icon.png", size=(32,32))
if win_icon:
    root.iconphoto(False, win_icon)

# Toolbar
left = ttk.Frame(root, width=TOOLBAR_W, height=CANVAS_H)
left.pack(side="left", fill="y")

ttk.Label(left, text="Select Filter:", background="white")\
    .pack(pady=(10,2))
filters = ["Contour", "Black and White", "Blur", "Detail",
           "Emboss", "Edge Enhance", "Sharpen", "Smooth"]
filter_combobox = ttk.Combobox(left, values=filters, width=15)
filter_combobox.pack(pady=5)
filter_combobox.bind("<<ComboboxSelected>>", apply_filter)

# Buttons (icon or text)
btns = [
    ("add.png",    "Open",   open_image),
    ("flip.png",   "Flip",   flip_image),
    ("rotate.png", "Rotate", rotate_image),
    ("color.png",  "Color",  change_color),
    ("erase.png",  "Erase",  erase_lines),
    ("saved.png",  "Save",   save_image),
]
for ico_file, text, cmd in btns:
    ico = load_icon(ico_file)
    if ico:
        b = ttk.Button(left, image=ico, bootstyle="light", command=cmd)
        b.image = ico
    else:
        b = ttk.Button(left, text=text, bootstyle="light", command=cmd)
    b.pack(pady=8)

# Canvas
canvas = ttk.Canvas(root, width=CANVAS_W, height=CANVAS_H)
canvas.pack(side="right", fill="both", expand=True)
canvas.bind("<B1-Motion>", draw)

root.mainloop()
