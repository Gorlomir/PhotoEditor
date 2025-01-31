import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, colorchooser
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageFilter

class PhotoEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Фото редактор by Gorlomir")
        self.image_path = None
        self.image = None
        self.photo = None
        self.drawing = False
        self.last_x, self.last_y = 0, 0
        self.drawing_color = "black"
        self.drawing_width = 2
        self.crop_box = None
        self.text_to_add = None
        self.selected_position = None
        self.create_menu()
        self.create_canvas_with_scrollbars()

    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Открыть", command=self.open_image)
        file_menu.add_command(label="Сохранить", command=self.save_image)
        menu_bar.add_cascade(label="Меню", menu=file_menu)

        tools_menu = tk.Menu(menu_bar, tearoff=0)
        tools_menu.add_command(label="Добавить текст", command=self.add_text_dialog)
        tools_menu.add_command(label="Обрезать", command=self.crop_dialog)
        tools_menu.add_command(label="Рисовать", command=self.enable_drawing)
        tools_menu.add_command(label="Добавить фильтр", command=self.apply_filter_dialog)
        tools_menu.add_command(label="Вставить изображение", command=self.add_image_dialog)
        menu_bar.add_cascade(label="Инструменты", menu=tools_menu)

    def create_canvas_with_scrollbars(self):
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.frame, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        h_scrollbar = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        v_scrollbar = tk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.canvas.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)

        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)

    def on_canvas_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox(tk.ALL))

    def open_image(self):
        self.image_path = filedialog.askopenfilename(title="Выберите файл",
                                                   filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if self.image_path:
            try:
                self.image = Image.open(self.image_path)
                self.photo = ImageTk.PhotoImage(self.image)
                self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
                self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
                self.root.update_idletasks()
                self.root.geometry(f"{self.image.width + 40}x{self.image.height + 100}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть изображение: {e}")

    def save_image(self):
        if self.image:
            save_path = filedialog.asksaveasfilename(defaultextension=".jpg",
                                                   filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")])
            if save_path:
                try:
                    self.image.save(save_path)
                    messagebox.showinfo("Сохранение", "Изображение сохранено")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось сохранить изображение: {e}")
        else:
            messagebox.showerror("Ошибка", "Изображение не открыто")

    def add_text_dialog(self):
        text = simpledialog.askstring("Вставка текста", "Введите текст:")
        if text:
            self.text_to_add = text
            self.canvas.bind("<Button-1>", self.on_text_position_selected)
            messagebox.showinfo("Информация", "Кликните на холсте, чтобы выбрать позицию для текста.")

    def on_text_position_selected(self, event):
        position = (event.x, event.y)
        self.canvas.unbind("<Button-1>")
        if self.text_to_add:
            self.add_text_to_image(self.text_to_add, position)

    def add_text_to_image(self, text, position, font_path="Triodion-Regular.ttf", font_size=30, color=(255, 255, 255)):
        try:
            draw = ImageDraw.Draw(self.image)
            font = ImageFont.truetype(font_path, font_size)
            draw.text(position, text, font=font, fill=color)
            self.photo = ImageTk.PhotoImage(self.image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
            self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        except IOError:
            messagebox.showerror("Ошибка", "Не удалось найти шрифт. Проверьте путь к файлу шрифта.")

    def choose_position(self):
        self.selected_position = None
        self.position_selected = tk.BooleanVar(value=False)
        self.canvas.unbind("<Button-1>")
        self.canvas.bind("<Button-1>", self.on_position_selected)
        messagebox.showinfo("Информация", "Кликните на холсте, чтобы выбрать позицию для нового изображения.")
        self.root.wait_variable(self.position_selected)

    def on_position_selected(self, event):
        self.selected_position = (event.x, event.y)
        self.position_selected.set(True)
        self.canvas.unbind("<Button-1>")

    def add_image_dialog(self):
        overlay_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if overlay_path:
            self.choose_position()
            if self.selected_position:
                self.add_image_to_image(overlay_path, self.selected_position)

    def add_image_to_image(self, overlay_path, position):
        try:
            overlay = Image.open(overlay_path).convert("RGBA")
            self.image.paste(overlay, position, overlay)
            self.photo = ImageTk.PhotoImage(self.image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
            self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось вставить изображение: {e}")

    def apply_filter_dialog(self):
        self.filter_window = tk.Toplevel(self.root)
        self.filter_window.title("Выберите фильтр")
        self.filter_window.geometry("300x350")
        filters = {
            "BLUR": ImageFilter.BLUR(),
            "CONTOUR": ImageFilter.CONTOUR(),
            "DETAIL": ImageFilter.DETAIL(),
            "EDGE_ENHANCE": ImageFilter.EDGE_ENHANCE(),
            "EMBOSS": ImageFilter.EMBOSS(),
            "FIND_EDGES": ImageFilter.FIND_EDGES(),
            "SHARPEN": ImageFilter.SHARPEN(),
            "SMOOTH": ImageFilter.SMOOTH(),
            "SMOOTH_MORE": ImageFilter.SMOOTH_MORE()
        }
        for i, (filter_name, filter_instance) in enumerate(filters.items()):
            button = tk.Button(self.filter_window, text=filter_name, command=lambda f=filter_instance: self.apply_filter(f))
            button.pack(pady=5)

    def apply_filter(self, filter_func):
        try:
            if isinstance(filter_func, ImageFilter.Filter):
                self.image = self.image.filter(filter_func)
            else:
                raise ValueError(f"Неверный тип фильтра: {filter_func}")
            self.photo = ImageTk.PhotoImage(self.image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
            self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
            self.filter_window.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось применить фильтр: {e}")

    def start_drawing(self, event):
        self.drawing = True
        self.last_x, self.last_y = event.x, event.y

    def draw(self, event):
        if self.drawing:
            self.canvas.create_line(self.last_x, self.last_y, event.x, event.y, fill=self.drawing_color, width=self.drawing_width)
            self.last_x, self.last_y = event.x, event.y

    def stop_drawing(self, event):
        self.drawing = False

    def enable_drawing(self):
        self.canvas.bind("<Button-1>", self.start_drawing)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)

    def crop_dialog(self):
        self.crop_box = []
        self.canvas.bind("<Button-1>", self.on_crop_start)
        self.canvas.bind("<B1-Motion>", self.on_crop_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_crop_end)

    def on_crop_start(self, event):
        self.crop_box.append(event.x)
        self.crop_box.append(event.y)
        self.crop_rect = self.canvas.create_rectangle(event.x, event.y, event.x, event.y, outline="red")

    def on_crop_drag(self, event):
        self.canvas.coords(self.crop_rect, self.crop_box[0], self.crop_box[1], event.x, event.y)

    def on_crop_end(self, event):
        self.crop_box.extend([event.x, event.y])
        self.crop_image(*self.crop_box)
        self.canvas.delete(self.crop_rect)
        self.crop_box = []

    def crop_image(self, x1, y1, x2, y2):
        try:
            self.image = self.image.crop((x1, y1, x2, y2))
            self.photo = ImageTk.PhotoImage(self.image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
            self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обрезать изображение: {e}")

    def on_canvas_click(self, event):
        pass

    def on_canvas_drag(self, event):
        pass

    def on_canvas_release(self, event):
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoEditorApp(root)
    root.mainloop()