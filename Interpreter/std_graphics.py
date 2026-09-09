import tkinter as tk
import time

# Corvus Built-in Zero-Config Graphics & Windowing Engine (Version 4.2)

class CorvusGraphicsEngine:
    def __init__(self):
        self.root = None
        self.canvas = None
        self.width = 800
        self.height = 600
        self.title = "Corvus Desktop Graphics"
        self.bg_color = "black"
        self.pressed_keys = set()
        self.mouse_pos = [0, 0]
        self.mouse_clicked = False
        self.is_running = False

    def init_window(self, title="Corvus App", width=800, height=600, bg_color="black"):
        self.title = title
        self.width = int(width)
        self.height = int(height)
        self.bg_color = bg_color

        if self.root:
            try:
                self.root.destroy()
            except Exception:
                pass

        self.root = tk.Tk()
        self.root.title(self.title)
        self.root.geometry(f"{self.width}x{self.height}")
        self.root.configure(bg=self.bg_color)
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg=self.bg_color, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.pressed_keys = set()
        self.mouse_pos = [0, 0]
        self.mouse_clicked = False

        def _on_key_press(event):
            k = event.keysym
            self.pressed_keys.add(k)
            if k == "Escape":
                self.close()

        def _on_key_release(event):
            k = event.keysym
            self.pressed_keys.discard(k)

        def _on_mouse_move(event):
            self.mouse_pos = [event.x, event.y]

        def _on_mouse_down(event):
            self.mouse_clicked = True

        def _on_mouse_up(event):
            self.mouse_clicked = False

        def _on_close():
            self.close()

        self.root.bind("<KeyPress>", _on_key_press)
        self.root.bind("<KeyRelease>", _on_key_release)
        self.root.bind("<Motion>", _on_mouse_move)
        self.root.bind("<ButtonPress-1>", _on_mouse_down)
        self.root.bind("<ButtonRelease-1>", _on_mouse_up)
        self.root.protocol("WM_DELETE_WINDOW", _on_close)

        self.is_running = True
        self.update()
        return True

    def clear(self, color=None):
        if not self.canvas: return
        self.canvas.delete("all")
        if color:
            self.canvas.configure(bg=color)

    def draw_rect(self, x, y, w, h, color="white", fill=True):
        if not self.canvas: return
        x1, y1, x2, y2 = x, y, x + w, y + h
        fill_color = color if fill else ""
        self.canvas.create_rectangle(x1, y1, x2, y2, outline=color, fill=fill_color)

    def draw_circle(self, x, y, radius, color="white", fill=True):
        if not self.canvas: return
        x1, y1, x2, y2 = x - radius, y - radius, x + radius, y + radius
        fill_color = color if fill else ""
        self.canvas.create_oval(x1, y1, x2, y2, outline=color, fill=fill_color)

    def draw_line(self, x1, y1, x2, y2, color="white", thickness=2):
        if not self.canvas: return
        self.canvas.create_line(x1, y1, x2, y2, fill=color, width=thickness)

    def draw_text(self, text, x, y, font_size=16, color="white"):
        if not self.canvas: return
        self.canvas.create_text(x, y, text=str(text), fill=color, font=("Consolas", int(font_size), "bold"), anchor="nw")

    def draw_polygon(self, points, color="white", fill=True):
        if not self.canvas: return
        flat_points = []
        for p in points:
            if isinstance(p, (list, tuple)):
                flat_points.extend(p)
            else:
                flat_points.append(p)
        fill_color = color if fill else ""
        self.canvas.create_polygon(*flat_points, outline=color, fill=fill_color)

    def update(self):
        if self.root and self.is_running:
            try:
                self.root.update_idletasks()
                self.root.update()
            except Exception:
                self.is_running = False

    def is_open(self):
        return self.is_running and self.root is not None

    def poll_events(self):
        self.update()
        return self.is_open()

    def is_key_pressed(self, key_name):
        if not self.is_running: return False
        if key_name.lower() in ("up", "down", "left", "right"):
            key_name = key_name.capitalize()
        return key_name in self.pressed_keys

    def get_mouse_pos(self):
        return self.mouse_pos

    def is_mouse_clicked(self):
        return self.mouse_clicked

    def sleep(self, seconds):
        end_time = time.time() + seconds
        while time.time() < end_time:
            self.update()
            time.sleep(0.005)

    def fps(self, target_fps=60):
        if target_fps <= 0: return
        frame_time = 1.0 / target_fps
        self.sleep(frame_time)

    def close(self):
        self.is_running = False
        if self.root:
            try:
                self.root.destroy()
            except Exception:
                pass
            self.root = None
            self.canvas = None

_global_graphics = CorvusGraphicsEngine()
