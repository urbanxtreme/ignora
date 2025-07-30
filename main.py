import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import os
from PIL import Image, ImageTk, ImageFilter, ImageEnhance, ImageOps, ImageDraw
from collections import deque
import numpy as np

class ImageEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Ignora Pro - Image Editor")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2c3e50')
        
        # Variables
        self.current_image = None
        self.original_image = None
        self.display_image = None
        self.image_path = None
        self.undo_stack = deque(maxlen=20)
        self.redo_stack = deque(maxlen=20)
        self.zoom_factor = 1.0
        self.drawing_mode = False
        self.draw_color = '#000000'
        self.brush_size = 5
        self.last_x = None
        self.last_y = None
        
        # Create UI
        self.create_ui()
        self.center_window()
        
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_ui(self):
        """Create the main user interface"""
        # Main container
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top toolbar
        self.create_toolbar(main_frame)
        
        # Content area
        content_frame = tk.Frame(main_frame, bg='#2c3e50')
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Left panel (tools)
        self.create_left_panel(content_frame)
        
        # Center (canvas)
        self.create_canvas_area(content_frame)
        
        # Right panel (properties)
        self.create_right_panel(content_frame)
        
        # Status bar
        self.create_status_bar(main_frame)
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self.open_image())
        self.root.bind('<Control-s>', lambda e: self.save_image())
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())
        self.root.bind('<Control-plus>', lambda e: self.zoom_in())
        self.root.bind('<Control-minus>', lambda e: self.zoom_out())
        
    def create_toolbar(self, parent):
        """Create the top toolbar"""
        toolbar = tk.Frame(parent, bg='#34495e', height=60)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        toolbar.pack_propagate(False)
        
        # File operations
        file_frame = tk.Frame(toolbar, bg='#34495e')
        file_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.create_button(file_frame, "📁 Open", self.open_image, "#3498db")
        self.create_button(file_frame, "💾 Save", self.save_image, "#27ae60")
        self.create_button(file_frame, "💾 Save As", self.save_as_image, "#27ae60")
        
        # Edit operations
        edit_frame = tk.Frame(toolbar, bg='#34495e')
        edit_frame.pack(side=tk.LEFT, padx=20, pady=10)
        
        self.create_button(edit_frame, "↶ Undo", self.undo, "#e67e22")
        self.create_button(edit_frame, "↷ Redo", self.redo, "#e67e22")
        
        # Zoom controls
        zoom_frame = tk.Frame(toolbar, bg='#34495e')
        zoom_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        
        self.create_button(zoom_frame, "🔍+", self.zoom_in, "#9b59b6")
        self.create_button(zoom_frame, "🔍-", self.zoom_out, "#9b59b6")
        self.create_button(zoom_frame, "🔍 Fit", self.fit_to_window, "#9b59b6")
        
    def create_button(self, parent, text, command, color="#34495e"):
        """Create a styled button"""
        btn = tk.Button(parent, text=text, command=command, 
                       bg=color, fg='white', font=('Arial', 10, 'bold'),
                       relief=tk.FLAT, padx=15, pady=5, cursor='hand2')
        btn.pack(side=tk.LEFT, padx=2)
        
        # Hover effects
        def on_enter(e):
            btn.configure(bg=self.lighten_color(color))
        def on_leave(e):
            btn.configure(bg=color)
            
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        return btn
        
    def lighten_color(self, color):
        """Lighten a hex color"""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        rgb = tuple(min(255, int(c * 1.2)) for c in rgb)
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        
    def create_left_panel(self, parent):
        """Create the left tool panel"""
        left_panel = tk.Frame(parent, bg='#34495e', width=200)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Create scrollable frame for tools
        canvas_tools = tk.Canvas(left_panel, bg='#34495e', highlightthickness=0)
        scrollbar_tools = ttk.Scrollbar(left_panel, orient="vertical", command=canvas_tools.yview)
        scrollable_frame = tk.Frame(canvas_tools, bg='#34495e')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas_tools.configure(scrollregion=canvas_tools.bbox("all"))
        )
        
        canvas_tools.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas_tools.configure(yscrollcommand=scrollbar_tools.set)
        
        # Tools section
        tools_label = tk.Label(scrollable_frame, text="🛠️ TOOLS", bg='#34495e', 
                              fg='white', font=('Arial', 12, 'bold'))
        tools_label.pack(pady=10)
        
        # Basic tools
        self.create_tool_button(scrollable_frame, "✂️ Crop", self.crop_tool)
        self.create_tool_button(scrollable_frame, "🔄 Rotate", self.rotate_tool)
        self.create_tool_button(scrollable_frame, "🖌️ Draw", self.toggle_draw_mode)
        self.create_tool_button(scrollable_frame, "🎨 Color Picker", self.choose_draw_color)
        
        # Separator
        separator = tk.Frame(scrollable_frame, height=2, bg='#2c3e50')
        separator.pack(fill=tk.X, pady=10, padx=10)
        
        # Filters section
        filters_label = tk.Label(scrollable_frame, text="🎭 FILTERS", bg='#34495e', 
                                fg='white', font=('Arial', 12, 'bold'))
        filters_label.pack(pady=10)
        
        self.create_tool_button(scrollable_frame, "⚫ Grayscale", self.apply_grayscale)
        self.create_tool_button(scrollable_frame, "📸 Sepia", self.apply_sepia)
        self.create_tool_button(scrollable_frame, "🔄 Invert", self.apply_invert)
        self.create_tool_button(scrollable_frame, "✨ Blur", self.apply_blur)
        self.create_tool_button(scrollable_frame, "🔍 Sharpen", self.apply_sharpen)
        self.create_tool_button(scrollable_frame, "🌟 Emboss", self.apply_emboss)
        
        # Separator
        separator2 = tk.Frame(scrollable_frame, height=2, bg='#2c3e50')
        separator2.pack(fill=tk.X, pady=10, padx=10)
        
        # Transform section
        transform_label = tk.Label(scrollable_frame, text="🔄 TRANSFORM", bg='#34495e', 
                                  fg='white', font=('Arial', 12, 'bold'))
        transform_label.pack(pady=10)
        
        self.create_tool_button(scrollable_frame, "↔️ Flip H", self.flip_horizontal)
        self.create_tool_button(scrollable_frame, "↕️ Flip V", self.flip_vertical)
        self.create_tool_button(scrollable_frame, "🔄 Rotate 90°", self.rotate_90)
        self.create_tool_button(scrollable_frame, "🔄 Rotate 180°", self.rotate_180)
        self.create_tool_button(scrollable_frame, "🔄 Rotate 270°", self.rotate_270)
        self.create_tool_button(scrollable_frame, "🔄 Transpose", self.transpose_image)
        
        # Pack the canvas and scrollbar
        canvas_tools.pack(side="left", fill="both", expand=True)
        scrollbar_tools.pack(side="right", fill="y")
        
    def create_tool_button(self, parent, text, command):
        """Create a tool button"""
        btn = tk.Button(parent, text=text, command=command,
                       bg='#3498db', fg='white', font=('Arial', 10),
                       relief=tk.FLAT, pady=8, cursor='hand2')
        btn.pack(fill=tk.X, padx=10, pady=2)
        
        def on_enter(e):
            btn.configure(bg='#2980b9')
        def on_leave(e):
            btn.configure(bg='#3498db')
            
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        return btn
        
    def create_canvas_area(self, parent):
        """Create the main canvas area"""
        canvas_frame = tk.Frame(parent, bg='#ecf0f1', relief=tk.SUNKEN, bd=2)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Canvas with scrollbars
        self.canvas = tk.Canvas(canvas_frame, bg='white', cursor='crosshair')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack scrollbars and canvas
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind mouse events for drawing
        self.canvas.bind('<Button-1>', self.start_draw)
        self.canvas.bind('<B1-Motion>', self.draw)
        self.canvas.bind('<ButtonRelease-1>', self.end_draw)
        
    def create_right_panel(self, parent):
        """Create the right properties panel"""
        right_panel = tk.Frame(parent, bg='#34495e', width=250)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_panel.pack_propagate(False)
        
        # Properties section
        props_label = tk.Label(right_panel, text="⚙️ PROPERTIES", bg='#34495e', 
                              fg='white', font=('Arial', 12, 'bold'))
        props_label.pack(pady=10)
        
        # Image info
        self.info_frame = tk.Frame(right_panel, bg='#34495e')
        self.info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.size_label = tk.Label(self.info_frame, text="Size: No image", 
                                  bg='#34495e', fg='white', font=('Arial', 9))
        self.size_label.pack(anchor=tk.W)
        
        self.format_label = tk.Label(self.info_frame, text="Format: -", 
                                    bg='#34495e', fg='white', font=('Arial', 9))
        self.format_label.pack(anchor=tk.W)
        
        # Separator
        separator = tk.Frame(right_panel, height=2, bg='#2c3e50')
        separator.pack(fill=tk.X, pady=10, padx=10)
        
        # Adjustments
        adj_label = tk.Label(right_panel, text="🎛️ ADJUSTMENTS", bg='#34495e', 
                            fg='white', font=('Arial', 12, 'bold'))
        adj_label.pack(pady=10)
        
        # Brightness
        self.create_slider(right_panel, "Brightness", -100, 100, 0, self.adjust_brightness)
        
        # Contrast
        self.create_slider(right_panel, "Contrast", -100, 100, 0, self.adjust_contrast)
        
        # Saturation
        self.create_slider(right_panel, "Saturation", -100, 100, 0, self.adjust_saturation)
        
        # Drawing tools
        draw_label = tk.Label(right_panel, text="✏️ DRAWING", bg='#34495e', 
                             fg='white', font=('Arial', 12, 'bold'))
        draw_label.pack(pady=(20, 10))
        
        # Brush size
        brush_frame = tk.Frame(right_panel, bg='#34495e')
        brush_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(brush_frame, text="Brush Size:", bg='#34495e', fg='white').pack(anchor=tk.W)
        self.brush_scale = tk.Scale(brush_frame, from_=1, to=20, orient=tk.HORIZONTAL,
                                   bg='#34495e', fg='white', highlightthickness=0,
                                   command=self.update_brush_size)
        self.brush_scale.set(5)
        self.brush_scale.pack(fill=tk.X)
        
        # Color display
        color_frame = tk.Frame(right_panel, bg='#34495e')
        color_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(color_frame, text="Color:", bg='#34495e', fg='white').pack(anchor=tk.W)
        self.color_display = tk.Frame(color_frame, bg=self.draw_color, height=30, relief=tk.RAISED, bd=2)
        self.color_display.pack(fill=tk.X, pady=5)
        
    def create_slider(self, parent, label, min_val, max_val, default, command):
        """Create a labeled slider"""
        frame = tk.Frame(parent, bg='#34495e')
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(frame, text=f"{label}:", bg='#34495e', fg='white').pack(anchor=tk.W)
        
        slider = tk.Scale(frame, from_=min_val, to=max_val, orient=tk.HORIZONTAL,
                         bg='#34495e', fg='white', highlightthickness=0,
                         command=lambda val: command(int(val)))
        slider.set(default)
        slider.pack(fill=tk.X)
        
        return slider
        
    def create_status_bar(self, parent):
        """Create the status bar"""
        self.status_bar = tk.Label(parent, text="Ready", relief=tk.SUNKEN, 
                                  bg='#ecf0f1', fg='#2c3e50', anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        
    def update_status(self, message):
        """Update status bar message"""
        self.status_bar.config(text=message)
        self.root.after(3000, lambda: self.status_bar.config(text="Ready"))
        
    def open_image(self):
        """Open an image file"""
        file_path = filedialog.askopenfilename(
            title="Open Image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("PNG files", "*.png"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.original_image = Image.open(file_path)
                self.current_image = self.original_image.copy()
                self.image_path = file_path
                
                # Clear undo/redo stacks
                self.undo_stack.clear()
                self.redo_stack.clear()
                self.save_state()
                
                self.display_image_on_canvas()
                self.update_image_info()
                self.update_status(f"Opened: {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not open image: {str(e)}")
                
    def save_image(self):
        """Save the current image"""
        if not self.current_image:
            messagebox.showwarning("Warning", "No image to save!")
            return
            
        if not self.image_path:
            self.save_as_image()
            return
            
        try:
            self.current_image.save(self.image_path)
            self.update_status("Image saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save image: {str(e)}")
            
    def save_as_image(self):
        """Save image with new name"""
        if not self.current_image:
            messagebox.showwarning("Warning", "No image to save!")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save Image As",
            defaultextension=".jpg",
            filetypes=[
                ("JPEG files", "*.jpg"),
                ("PNG files", "*.png"),
                ("BMP files", "*.bmp"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.current_image.save(file_path)
                self.image_path = file_path
                self.update_status(f"Saved as: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save image: {str(e)}")
                
    def display_image_on_canvas(self):
        """Display the current image on canvas"""
        if not self.current_image:
            return
            
        # Get canvas dimensions
        self.canvas.update_idletasks()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            self.root.after(100, self.display_image_on_canvas)
            return
            
        img_width, img_height = self.current_image.size
        
        # Calculate scale to fit image in canvas
        scale_x = (canvas_width - 20) / img_width  # Leave some margin
        scale_y = (canvas_height - 20) / img_height
        scale = min(scale_x, scale_y, 1.0) * self.zoom_factor  # Don't upscale beyond 100% unless zoomed
        
        new_width = max(1, int(img_width * scale))
        new_height = max(1, int(img_height * scale))
        
        # Resize image for display
        try:
            self.display_image = self.current_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(self.display_image)
            
            # Clear canvas and display image
            self.canvas.delete("all")
            
            # Center the image
            x = canvas_width // 2
            y = canvas_height // 2
            
            self.canvas.create_image(x, y, image=self.photo, anchor=tk.CENTER)
            
            # Update scroll region
            bbox = self.canvas.bbox("all")
            if bbox:
                self.canvas.configure(scrollregion=bbox)
        except Exception as e:
            print(f"Error displaying image: {e}")
            self.update_status("Error displaying image")
        
    def update_image_info(self):
        """Update image information display"""
        if self.current_image:
            width, height = self.current_image.size
            self.size_label.config(text=f"Size: {width} × {height}")
            self.format_label.config(text=f"Format: {self.current_image.format or 'Unknown'}")
        else:
            self.size_label.config(text="Size: No image")
            self.format_label.config(text="Format: -")
            
    def save_state(self):
        """Save current state to undo stack"""
        if self.current_image:
            self.undo_stack.append(self.current_image.copy())
            self.redo_stack.clear()
            
    def undo(self):
        """Undo last operation"""
        if len(self.undo_stack) > 1:
            self.redo_stack.append(self.undo_stack.pop())
            self.current_image = self.undo_stack[-1].copy()
            self.display_image_on_canvas()
            self.update_status("Undo successful")
            
    def redo(self):
        """Redo last undone operation"""
        if self.redo_stack:
            self.current_image = self.redo_stack.pop()
            self.undo_stack.append(self.current_image.copy())
            self.display_image_on_canvas()
            self.update_status("Redo successful")
            
    def zoom_in(self):
        """Zoom in"""
        self.zoom_factor = min(self.zoom_factor * 1.2, 5.0)
        self.display_image_on_canvas()
        
    def zoom_out(self):
        """Zoom out"""
        self.zoom_factor = max(self.zoom_factor / 1.2, 0.1)
        self.display_image_on_canvas()
        
    def fit_to_window(self):
        """Fit image to window"""
        self.zoom_factor = 1.0
        self.display_image_on_canvas()
        
    # Drawing functions
    def toggle_draw_mode(self):
        """Toggle drawing mode"""
        self.drawing_mode = not self.drawing_mode
        cursor = 'pencil' if self.drawing_mode else 'crosshair'
        self.canvas.configure(cursor=cursor)
        status = "Drawing mode ON" if self.drawing_mode else "Drawing mode OFF"
        self.update_status(status)
        
    def choose_draw_color(self):
        """Choose drawing color"""
        color = colorchooser.askcolor(color=self.draw_color)[1]
        if color:
            self.draw_color = color
            self.color_display.configure(bg=color)
            
    def update_brush_size(self, value):
        """Update brush size"""
        self.brush_size = int(value)
        
    def start_draw(self, event):
        """Start drawing"""
        if self.drawing_mode and self.current_image:
            self.last_x = event.x
            self.last_y = event.y
            
    def draw(self, event):
        """Draw on image"""
        if self.drawing_mode and self.current_image and self.last_x and self.last_y:
            # Calculate position on actual image
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            img_width, img_height = self.current_image.size
            scale_x = canvas_width / img_width
            scale_y = canvas_height / img_height
            scale = min(scale_x, scale_y) * self.zoom_factor
            
            # Convert canvas coordinates to image coordinates
            center_x = canvas_width // 2
            center_y = canvas_height // 2
            
            img_x = int((event.x - center_x) / scale + img_width // 2)
            img_y = int((event.y - center_y) / scale + img_height // 2)
            last_img_x = int((self.last_x - center_x) / scale + img_width // 2)
            last_img_y = int((self.last_y - center_y) / scale + img_height // 2)
            
            # Draw on the actual image
            draw = ImageDraw.Draw(self.current_image)
            draw.line([last_img_x, last_img_y, img_x, img_y], 
                     fill=self.draw_color, width=self.brush_size)
            
            self.display_image_on_canvas()
            
            self.last_x = event.x
            self.last_y = event.y
            
    def end_draw(self, event):
        """End drawing"""
        if self.drawing_mode:
            self.save_state()
            self.last_x = None
            self.last_y = None
            
    # Filter functions
    def apply_grayscale(self):
        """Apply grayscale filter"""
        if self.current_image:
            self.save_state()
            self.current_image = self.current_image.convert('L').convert('RGB')
            self.display_image_on_canvas()
            self.update_status("Grayscale filter applied")
            
    def apply_sepia(self):
        """Apply sepia filter"""
        if self.current_image:
            self.save_state()
            # Convert to numpy array for easier manipulation
            img_array = np.array(self.current_image)
            
            # Sepia transformation matrix
            sepia_filter = np.array([
                [0.393, 0.769, 0.189],
                [0.349, 0.686, 0.168],
                [0.272, 0.534, 0.131]
            ])
            
            sepia_img = img_array.dot(sepia_filter.T)
            sepia_img = np.clip(sepia_img, 0, 255).astype(np.uint8)
            
            self.current_image = Image.fromarray(sepia_img)
            self.display_image_on_canvas()
            self.update_status("Sepia filter applied")
            
    def apply_invert(self):
        """Apply invert filter"""
        if self.current_image:
            self.save_state()
            self.current_image = ImageOps.invert(self.current_image)
            self.display_image_on_canvas()
            self.update_status("Invert filter applied")
            
    def apply_blur(self):
        """Apply blur filter"""
        if self.current_image:
            self.save_state()
            self.current_image = self.current_image.filter(ImageFilter.BLUR)
            self.display_image_on_canvas()
            self.update_status("Blur filter applied")
            
    def apply_sharpen(self):
        """Apply sharpen filter"""
        if self.current_image:
            self.save_state()
            self.current_image = self.current_image.filter(ImageFilter.SHARPEN)
            self.display_image_on_canvas()
            self.update_status("Sharpen filter applied")
            
    def apply_emboss(self):
        """Apply emboss filter"""
        if self.current_image:
            self.save_state()
            self.current_image = self.current_image.filter(ImageFilter.EMBOSS)
            self.display_image_on_canvas()
            self.update_status("Emboss filter applied")
            
    # Transform functions
    def flip_horizontal(self):
        """Flip image horizontally"""
        if self.current_image:
            self.save_state()
            self.current_image = self.current_image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            self.display_image_on_canvas()
            self.update_status("Flipped horizontally")
            
    def flip_vertical(self):
        """Flip image vertically"""
        if self.current_image:
            self.save_state()
            self.current_image = self.current_image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            self.display_image_on_canvas()
            self.update_status("Flipped vertically")
            
    def rotate_90(self):
        """Rotate image 90 degrees"""
        if self.current_image:
            self.save_state()
            self.current_image = self.current_image.transpose(Image.Transpose.ROTATE_90)
            self.display_image_on_canvas()
            self.update_image_info()
            self.update_status("Rotated 90°")
            
    def rotate_180(self):
        """Rotate image 180 degrees"""
        if self.current_image:
            self.save_state()
            self.current_image = self.current_image.transpose(Image.Transpose.ROTATE_180)
            self.display_image_on_canvas()
    def rotate_270(self):
        """Rotate image 270 degrees"""
        if self.current_image:
            self.save_state()
            self.current_image = self.current_image.transpose(Image.Transpose.ROTATE_270)
            self.display_image_on_canvas()
            self.update_image_info()
            self.update_status("Rotated 270°")
            
    def transpose_image(self):
        """Transpose image (swap width and height)"""
        if self.current_image:
            self.save_state()
            self.current_image = self.current_image.transpose(Image.Transpose.TRANSPOSE)
            self.display_image_on_canvas()
            self.update_image_info()
            self.update_status("Image transposed")
            
    # Adjustment functions
    def adjust_brightness(self, value):
        """Adjust image brightness"""
        if self.current_image and value != 0:
            enhancer = ImageEnhance.Brightness(self.original_image)
            factor = 1.0 + (value / 100.0)
            self.current_image = enhancer.enhance(factor)
            self.display_image_on_canvas()
            
    def adjust_contrast(self, value):
        """Adjust image contrast"""
        if self.current_image and value != 0:
            enhancer = ImageEnhance.Contrast(self.original_image)
            factor = 1.0 + (value / 100.0)
            self.current_image = enhancer.enhance(factor)
            self.display_image_on_canvas()
            
    def adjust_saturation(self, value):
        """Adjust image saturation"""
        if self.current_image and value != 0:
            enhancer = ImageEnhance.Color(self.original_image)
            factor = 1.0 + (value / 100.0)
            self.current_image = enhancer.enhance(factor)
            self.display_image_on_canvas()
            
    # Tool functions
    def crop_tool(self):
        """Activate crop tool"""
        if not self.current_image:
            messagebox.showwarning("Warning", "No image loaded!")
            return
            
        self.update_status("Crop tool: Click and drag to select area, then press SPACE to crop")
        
        # Crop variables
        self.crop_start_x = None
        self.crop_start_y = None
        self.crop_rect = None
        self.crop_active = True
        
        def start_crop(event):
            if not self.crop_active:
                return
            self.crop_start_x = self.canvas.canvasx(event.x)
            self.crop_start_y = self.canvas.canvasy(event.y)
            
        def draw_crop_rect(event):
            if not self.crop_active or self.crop_start_x is None:
                return
            if self.crop_rect:
                self.canvas.delete(self.crop_rect)
            
            current_x = self.canvas.canvasx(event.x)
            current_y = self.canvas.canvasy(event.y)
            
            self.crop_rect = self.canvas.create_rectangle(
                self.crop_start_x, self.crop_start_y, current_x, current_y,
                outline='red', width=2, dash=(5, 5))
                
        def perform_crop(event):
            if not self.crop_active or not self.crop_rect:
                return
                
            try:
                # Get crop coordinates
                coords = self.canvas.coords(self.crop_rect)
                
                # Get canvas dimensions and image position
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                
                img_width, img_height = self.current_image.size
                
                # Calculate scale and position
                scale_x = canvas_width / img_width
                scale_y = canvas_height / img_height
                scale = min(scale_x, scale_y) * self.zoom_factor
                
                # Calculate image position on canvas
                scaled_width = int(img_width * scale)
                scaled_height = int(img_height * scale)
                img_x = (canvas_width - scaled_width) // 2
                img_y = (canvas_height - scaled_height) // 2
                
                # Convert canvas coordinates to image coordinates
                x1 = max(0, int((coords[0] - img_x) / scale))
                y1 = max(0, int((coords[1] - img_y) / scale))
                x2 = min(img_width, int((coords[2] - img_x) / scale))
                y2 = min(img_height, int((coords[3] - img_y) / scale))
                
                # Ensure we have a valid crop area
                if x2 > x1 and y2 > y1:
                    self.save_state()
                    self.current_image = self.current_image.crop((x1, y1, x2, y2))
                    self.display_image_on_canvas()
                    self.update_image_info()
                    self.update_status("Image cropped successfully")
                else:
                    self.update_status("Invalid crop area")
                
                # Clean up
                if self.crop_rect:
                    self.canvas.delete(self.crop_rect)
                    self.crop_rect = None
                self.crop_active = False
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not crop image: {str(e)}")
                self.crop_active = False
                
        def cancel_crop(event):
            if self.crop_rect:
                self.canvas.delete(self.crop_rect)
                self.crop_rect = None
            self.crop_active = False
            self.update_status("Crop cancelled")
            
        # Bind events temporarily
        self.canvas.bind('<Button-1>', start_crop)
        self.canvas.bind('<B1-Motion>', draw_crop_rect)
        self.root.bind('<space>', perform_crop)
        self.root.bind('<Escape>', cancel_crop)
        
        # Set focus to root to capture key events
        self.root.focus_set()
        
    def rotate_tool(self):
        """Open rotate tool window"""
        if not self.current_image:
            messagebox.showwarning("Warning", "No image loaded!")
            return
            
        # Create rotate window
        rotate_window = tk.Toplevel(self.root)
        rotate_window.title("Rotate Image")
        rotate_window.geometry("350x250")
        rotate_window.configure(bg='#34495e')
        rotate_window.resizable(False, False)
        
        # Center the window
        rotate_window.transient(self.root)
        rotate_window.grab_set()
        
        # Title
        title_label = tk.Label(rotate_window, text="Rotate Image", 
                              bg='#34495e', fg='white', font=('Arial', 14, 'bold'))
        title_label.pack(pady=20)
        
        # Angle slider
        angle_frame = tk.Frame(rotate_window, bg='#34495e')
        angle_frame.pack(pady=20)
        
        tk.Label(angle_frame, text="Angle (degrees):", 
                bg='#34495e', fg='white', font=('Arial', 11)).pack()
        
        angle_var = tk.IntVar()
        angle_scale = tk.Scale(angle_frame, from_=-180, to=180, orient=tk.HORIZONTAL,
                              variable=angle_var, bg='#34495e', fg='white',
                              highlightthickness=0, length=250, 
                              activebackground='#3498db', troughcolor='#2c3e50')
        angle_scale.pack(pady=10)
        
        # Current angle display
        angle_display = tk.Label(angle_frame, text="0°", 
                                bg='#34495e', fg='#3498db', font=('Arial', 12, 'bold'))
        angle_display.pack()
        
        def update_angle_display(val):
            angle_display.config(text=f"{val}°")
            
        angle_scale.config(command=update_angle_display)
        
        # Quick rotate buttons
        quick_frame = tk.Frame(rotate_window, bg='#34495e')
        quick_frame.pack(pady=10)
        
        tk.Label(quick_frame, text="Quick Rotate:", 
                bg='#34495e', fg='white', font=('Arial', 10)).pack()
        
        quick_buttons_frame = tk.Frame(quick_frame, bg='#34495e')
        quick_buttons_frame.pack(pady=5)
        
        def set_angle(angle):
            angle_scale.set(angle)
            
        tk.Button(quick_buttons_frame, text="90°", command=lambda: set_angle(90),
                 bg='#3498db', fg='white', font=('Arial', 9), width=6).pack(side=tk.LEFT, padx=2)
        tk.Button(quick_buttons_frame, text="180°", command=lambda: set_angle(180),
                 bg='#3498db', fg='white', font=('Arial', 9), width=6).pack(side=tk.LEFT, padx=2)
        tk.Button(quick_buttons_frame, text="270°", command=lambda: set_angle(270),
                 bg='#3498db', fg='white', font=('Arial', 9), width=6).pack(side=tk.LEFT, padx=2)
        
        # Buttons
        button_frame = tk.Frame(rotate_window, bg='#34495e')
        button_frame.pack(pady=20)
        
        def apply_rotation():
            angle = angle_var.get()
            if angle != 0:
                try:
                    self.save_state()
                    # Use expand=True to avoid cutting off parts of the image
                    self.current_image = self.current_image.rotate(-angle, expand=True, fillcolor='white')
                    self.display_image_on_canvas()
                    self.update_image_info()
                    self.update_status(f"Rotated by {angle}°")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not rotate image: {str(e)}")
            rotate_window.destroy()
            
        def preview_rotation():
            angle = angle_var.get()
            if angle != 0:
                try:
                    preview_img = self.current_image.rotate(-angle, expand=True, fillcolor='white')
                    # Temporarily show preview
                    temp_current = self.current_image
                    self.current_image = preview_img
                    self.display_image_on_canvas()
                    # Restore after 1 second
                    self.root.after(1000, lambda: self.restore_from_preview(temp_current))
                except Exception as e:
                    messagebox.showerror("Error", f"Could not preview rotation: {str(e)}")
                    
        def restore_from_preview(original):
            self.current_image = original
            self.display_image_on_canvas()
            
        tk.Button(button_frame, text="Preview", command=preview_rotation,
                 bg='#f39c12', fg='white', font=('Arial', 10), padx=15, relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Apply", command=apply_rotation,
                 bg='#27ae60', fg='white', font=('Arial', 10), padx=15, relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=rotate_window.destroy,
                 bg='#e74c3c', fg='white', font=('Arial', 10), padx=15, relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
                 
    def reset_adjustments(self):
        """Reset all adjustments to original image"""
        if self.original_image:
            self.save_state()
            self.current_image = self.original_image.copy()
            self.display_image_on_canvas()
            self.update_status("Reset to original image")
            
    def create_new_image(self):
        """Create a new blank image"""
        # Create new image dialog
        new_window = tk.Toplevel(self.root)
        new_window.title("New Image")
        new_window.geometry("300x250")
        new_window.configure(bg='#34495e')
        
        # Title
        title_label = tk.Label(new_window, text="Create New Image", 
                              bg='#34495e', fg='white', font=('Arial', 14, 'bold'))
        title_label.pack(pady=20)
        
        # Size inputs
        size_frame = tk.Frame(new_window, bg='#34495e')
        size_frame.pack(pady=20)
        
        tk.Label(size_frame, text="Width:", bg='#34495e', fg='white').grid(row=0, column=0, padx=5, pady=5)
        width_entry = tk.Entry(size_frame, width=10)
        width_entry.insert(0, "800")
        width_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(size_frame, text="Height:", bg='#34495e', fg='white').grid(row=1, column=0, padx=5, pady=5)
        height_entry = tk.Entry(size_frame, width=10)
        height_entry.insert(0, "600")
        height_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Color selection
        color_frame = tk.Frame(new_window, bg='#34495e')
        color_frame.pack(pady=10)
        
        tk.Label(color_frame, text="Background:", bg='#34495e', fg='white').pack()
        
        color_var = tk.StringVar(value="white")
        color_options = [("White", "white"), ("Black", "black"), ("Transparent", "transparent")]
        
        for text, value in color_options:
            tk.Radiobutton(color_frame, text=text, variable=color_var, value=value,
                          bg='#34495e', fg='white', selectcolor='#34495e').pack(anchor=tk.W)
        
        # Buttons
        button_frame = tk.Frame(new_window, bg='#34495e')
        button_frame.pack(pady=20)
        
        def create_image():
            try:
                width = int(width_entry.get())
                height = int(height_entry.get())
                color = color_var.get()
                
                if width <= 0 or height <= 0:
                    messagebox.showerror("Error", "Width and height must be positive numbers!")
                    return
                    
                if color == "transparent":
                    self.current_image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
                else:
                    self.current_image = Image.new('RGB', (width, height), color)
                
                self.original_image = self.current_image.copy()
                self.image_path = None
                
                # Clear undo/redo stacks
                self.undo_stack.clear()
                self.redo_stack.clear()
                self.save_state()
                
                self.display_image_on_canvas()
                self.update_image_info()
                self.update_status(f"Created new {width}×{height} image")
                new_window.destroy()
                
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for width and height!")
                
        tk.Button(button_frame, text="Create", command=create_image,
                 bg='#27ae60', fg='white', font=('Arial', 10), padx=20).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=new_window.destroy,
                 bg='#e74c3c', fg='white', font=('Arial', 10), padx=20).pack(side=tk.LEFT, padx=5)
                 
    def show_image_info(self):
        """Show detailed image information"""
        if not self.current_image:
            messagebox.showwarning("Warning", "No image loaded!")
            return
            
        # Create info window
        info_window = tk.Toplevel(self.root)
        info_window.title("Image Information")
        info_window.geometry("400x300")
        info_window.configure(bg='#34495e')
        
        # Title
        title_label = tk.Label(info_window, text="Image Information", 
                              bg='#34495e', fg='white', font=('Arial', 14, 'bold'))
        title_label.pack(pady=20)
        
        # Information frame
        info_frame = tk.Frame(info_window, bg='#34495e')
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Get image info
        width, height = self.current_image.size
        mode = self.current_image.mode
        format_name = self.current_image.format or "Unknown"
        
        # Calculate file size if image is saved
        file_size = "Unknown"
        if self.image_path and os.path.exists(self.image_path):
            size_bytes = os.path.getsize(self.image_path)
            if size_bytes < 1024:
                file_size = f"{size_bytes} bytes"
            elif size_bytes < 1024 * 1024:
                file_size = f"{size_bytes / 1024:.1f} KB"
            else:
                file_size = f"{size_bytes / (1024 * 1024):.1f} MB"
        
        # Display information
        info_items = [
            ("Filename:", os.path.basename(self.image_path) if self.image_path else "Untitled"),
            ("Dimensions:", f"{width} × {height} pixels"),
            ("Color Mode:", mode),
            ("Format:", format_name),
            ("File Size:", file_size),
            ("Aspect Ratio:", f"{width/height:.2f}:1"),
        ]
        
        for i, (label, value) in enumerate(info_items):
            tk.Label(info_frame, text=label, bg='#34495e', fg='#bdc3c7', 
                    font=('Arial', 10), anchor=tk.W).grid(row=i, column=0, sticky=tk.W, pady=5)
            tk.Label(info_frame, text=value, bg='#34495e', fg='white', 
                    font=('Arial', 10, 'bold'), anchor=tk.W).grid(row=i, column=1, sticky=tk.W, padx=(20, 0), pady=5)
                    
    def run(self):
        """Start the application"""
        # Add menu bar
        self.create_menu_bar()
        
        # Start the main loop
        self.root.mainloop()
        
    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New...", command=self.create_new_image, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self.open_image, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self.save_image, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_as_image, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Image Info...", command=self.show_image_info)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Reset to Original", command=self.reset_adjustments)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Zoom In", command=self.zoom_in, accelerator="Ctrl++")
        view_menu.add_command(label="Zoom Out", command=self.zoom_out, accelerator="Ctrl+-")
        view_menu.add_command(label="Fit to Window", command=self.fit_to_window, accelerator="Ctrl+0")
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Crop", command=self.crop_tool)
        tools_menu.add_command(label="Rotate", command=self.rotate_tool)
        tools_menu.add_command(label="Drawing Mode", command=self.toggle_draw_mode)
        
        # Filters menu
        filters_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Filters", menu=filters_menu)
        filters_menu.add_command(label="Grayscale", command=self.apply_grayscale)
        filters_menu.add_command(label="Sepia", command=self.apply_sepia)
        filters_menu.add_command(label="Invert", command=self.apply_invert)
        filters_menu.add_separator()
        filters_menu.add_command(label="Blur", command=self.apply_blur)
        filters_menu.add_command(label="Sharpen", command=self.apply_sharpen)
        filters_menu.add_command(label="Emboss", command=self.apply_emboss)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Bind additional keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self.create_new_image())
        self.root.bind('<Control-Shift-S>', lambda e: self.save_as_image())
        self.root.bind('<Control-0>', lambda e: self.fit_to_window())
        
    def show_shortcuts(self):
        """Show keyboard shortcuts"""
        shortcuts_window = tk.Toplevel(self.root)
        shortcuts_window.title("Keyboard Shortcuts")
        shortcuts_window.geometry("400x500")
        shortcuts_window.configure(bg='#34495e')
        
        # Title
        title_label = tk.Label(shortcuts_window, text="Keyboard Shortcuts", 
                              bg='#34495e', fg='white', font=('Arial', 14, 'bold'))
        title_label.pack(pady=20)
        
        # Shortcuts frame
        shortcuts_frame = tk.Frame(shortcuts_window, bg='#34495e')
        shortcuts_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        shortcuts = [
            ("File Operations", ""),
            ("Ctrl + N", "New Image"),
            ("Ctrl + O", "Open Image"),
            ("Ctrl + S", "Save"),
            ("Ctrl + Shift + S", "Save As"),
            ("", ""),
            ("Edit Operations", ""),
            ("Ctrl + Z", "Undo"),
            ("Ctrl + Y", "Redo"),
            ("", ""),
            ("View Operations", ""),
            ("Ctrl + +", "Zoom In"),
            ("Ctrl + -", "Zoom Out"),
            ("Ctrl + 0", "Fit to Window"),
        ]
        
        for i, (shortcut, description) in enumerate(shortcuts):
            if shortcut == "" and description == "":
                continue
            elif description == "":
                # Section header
                tk.Label(shortcuts_frame, text=shortcut, bg='#34495e', fg='#3498db', 
                        font=('Arial', 11, 'bold'), anchor=tk.W).grid(row=i, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
            else:
                tk.Label(shortcuts_frame, text=shortcut, bg='#34495e', fg='#bdc3c7', 
                        font=('Arial', 10), anchor=tk.W).grid(row=i, column=0, sticky=tk.W, pady=2)
                tk.Label(shortcuts_frame, text=description, bg='#34495e', fg='white', 
                        font=('Arial', 10), anchor=tk.W).grid(row=i, column=1, sticky=tk.W, padx=(20, 0), pady=2)
                        
    def show_about(self):
        """Show about dialog"""
        about_window = tk.Toplevel(self.root)
        about_window.title("About Ignora Pro")
        about_window.geometry("350x300")
        about_window.configure(bg='#34495e')
        
        # Title
        title_label = tk.Label(about_window, text="Ignora Pro", 
                              bg='#34495e', fg='white', font=('Arial', 18, 'bold'))
        title_label.pack(pady=20)
        
        # Version
        version_label = tk.Label(about_window, text="Version 2.0", 
                                bg='#34495e', fg='#bdc3c7', font=('Arial', 12))
        version_label.pack(pady=5)
        
        # Description
        desc_label = tk.Label(about_window, 
                             text="A modern, feature-rich image editor\nbuilt with Python and Tkinter",
                             bg='#34495e', fg='white', font=('Arial', 11), justify=tk.CENTER)
        desc_label.pack(pady=20)
        
        # Features
        features_label = tk.Label(about_window, 
                                 text="Features:\n• Image editing and filters\n• Drawing tools\n• Crop and rotate\n• Undo/Redo support\n• Modern UI",
                                 bg='#34495e', fg='#bdc3c7', font=('Arial', 10), justify=tk.LEFT)
        features_label.pack(pady=20)
        
        # Close button
        tk.Button(about_window, text="Close", command=about_window.destroy,
                 bg='#3498db', fg='white', font=('Arial', 10), padx=20).pack(pady=20)


# Main execution
if __name__ == "__main__":
    try:
        app = ImageEditor()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()