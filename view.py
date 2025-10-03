import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk


class ImageSegmentationView:
    """
    View layer for the Image Segmentation application.
    Handles all GUI elements and user interactions.
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("Image Segmentation with K-Means Clustering")
        self.root.geometry("1400x800")
        
        # Controller reference (set by controller)
        self.controller = None
        
        # Display variables
        self.display_image = None
        self.display_photo = None
        self.original_size = None
        self.scale_factor = 1.0
        
        # Point selection mode
        self.selection_mode = "background"  # "background" or "object"
        
        # Image display references
        self.result_photos = {}
        
        self._create_widgets()
    
    def set_controller(self, controller):
        """Set the controller reference"""
        self.controller = controller
    
    def _create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Upload section
        upload_frame = ttk.LabelFrame(main_frame, text="Upload Image", padding="10")
        upload_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(upload_frame, text="Browse Image", 
                   command=self._browse_image).pack(side=tk.LEFT, padx=5)
        
        self.drop_label = ttk.Label(upload_frame, 
                                     text="Or drag and drop an image here",
                                     relief=tk.SUNKEN, padding=10)
        self.drop_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        # Register drag and drop
        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind('<<Drop>>', self._on_drop)
        
        # Point selection section
        selection_frame = ttk.LabelFrame(main_frame, text="Point Selection", padding="10")
        selection_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=5)
        
        self.mode_var = tk.StringVar(value="background")
        ttk.Radiobutton(selection_frame, text="Background Points (Red)", 
                       variable=self.mode_var, value="background",
                       command=self._change_mode).pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(selection_frame, text="Object Points (Blue)", 
                       variable=self.mode_var, value="object",
                       command=self._change_mode).pack(anchor=tk.W, pady=2)
        
        ttk.Button(selection_frame, text="Clear All Points", 
                   command=self._clear_points).pack(pady=10, fill=tk.X)
        
        ttk.Button(selection_frame, text="Process Image", 
                   command=self._process_image).pack(pady=5, fill=tk.X)
        
        # Original image display
        left_frame = ttk.LabelFrame(main_frame, text="Original Image", padding="10")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(0, weight=1)
        
        self.canvas = tk.Canvas(left_frame, bg="white", width=600, height=600)
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        
        # Results section
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        results_frame.columnconfigure(0, weight=1)
        results_frame.columnconfigure(1, weight=1)
        results_frame.columnconfigure(2, weight=1)
        
        # Object result
        obj_frame = ttk.Frame(results_frame)
        obj_frame.grid(row=0, column=0, padx=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        ttk.Label(obj_frame, text="Object Only").pack()
        self.object_canvas = tk.Canvas(obj_frame, bg="white", width=350, height=350)
        self.object_canvas.pack(pady=5)
        ttk.Button(obj_frame, text="Download", 
                   command=lambda: self._download_image("object")).pack()
        
        # Background result
        bg_frame = ttk.Frame(results_frame)
        bg_frame.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        ttk.Label(bg_frame, text="Background Only").pack()
        self.background_canvas = tk.Canvas(bg_frame, bg="white", width=350, height=350)
        self.background_canvas.pack(pady=5)
        ttk.Button(bg_frame, text="Download", 
                   command=lambda: self._download_image("background")).pack()
        
        # Eroded result
        eroded_frame = ttk.Frame(results_frame)
        eroded_frame.grid(row=0, column=2, padx=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        ttk.Label(eroded_frame, text="Eroded Object (Serrated Edges)").pack()
        self.eroded_canvas = tk.Canvas(eroded_frame, bg="white", width=350, height=350)
        self.eroded_canvas.pack(pady=5)
        ttk.Button(eroded_frame, text="Download", 
                   command=lambda: self._download_image("eroded")).pack()
    
    def _browse_image(self):
        """Open file dialog to browse for image"""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff"), 
                      ("All files", "*.*")]
        )
        if file_path and self.controller:
            self.controller.load_image(file_path)
    
    def _on_drop(self, event):
        """Handle drag and drop event"""
        file_path = event.data
        # Remove curly braces if present
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]
        if self.controller:
            self.controller.load_image(file_path)
    
    def _change_mode(self):
        """Change point selection mode"""
        self.selection_mode = self.mode_var.get()
    
    def _on_canvas_click(self, event):
        """Handle canvas click for point selection"""
        if self.controller and self.display_image:
            # Convert display coordinates to original image coordinates
            x = int(event.x / self.scale_factor)
            y = int(event.y / self.scale_factor)
            
            if self.selection_mode == "background":
                self.controller.add_background_point(x, y)
                # Draw red point
                self.canvas.create_oval(event.x-3, event.y-3, event.x+3, event.y+3, 
                                       fill="red", outline="red")
            else:
                self.controller.add_object_point(x, y)
                # Draw blue point
                self.canvas.create_oval(event.x-3, event.y-3, event.x+3, event.y+3, 
                                       fill="blue", outline="blue")
    
    def _clear_points(self):
        """Clear all selected points"""
        if self.controller:
            self.controller.clear_points()
            self.display_original_image(self.display_image)
    
    def _process_image(self):
        """Process the image with selected points"""
        if self.controller:
            self.controller.process_image()
    
    def _download_image(self, image_type):
        """Download a result image"""
        if self.controller:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), 
                          ("All files", "*.*")]
            )
            if file_path:
                self.controller.save_image(image_type, file_path)
    
    def display_original_image(self, image):
        """Display the original image on canvas"""
        if not image:
            return
        
        self.display_image = image
        self.original_size = image.size
        
        # Calculate scale factor to fit canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1:
            canvas_width = 600
        if canvas_height <= 1:
            canvas_height = 600
        
        width_scale = canvas_width / image.size[0]
        height_scale = canvas_height / image.size[1]
        self.scale_factor = min(width_scale, height_scale, 1.0)
        
        # Resize image for display
        new_size = (int(image.size[0] * self.scale_factor), 
                   int(image.size[1] * self.scale_factor))
        display_img = image.resize(new_size, Image.Resampling.LANCZOS)
        
        self.display_photo = ImageTk.PhotoImage(display_img)
        
        # Clear canvas and display image
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.display_photo)
    
    def display_results(self, object_img, background_img, eroded_img):
        """Display the three result images"""
        # Object image
        obj_display = self._resize_for_display(object_img, 350, 350)
        self.result_photos['object'] = ImageTk.PhotoImage(obj_display)
        self.object_canvas.delete("all")
        self.object_canvas.create_image(175, 175, image=self.result_photos['object'])
        
        # Background image
        bg_display = self._resize_for_display(background_img, 350, 350)
        self.result_photos['background'] = ImageTk.PhotoImage(bg_display)
        self.background_canvas.delete("all")
        self.background_canvas.create_image(175, 175, image=self.result_photos['background'])
        
        # Eroded image
        eroded_display = self._resize_for_display(eroded_img, 350, 350)
        self.result_photos['eroded'] = ImageTk.PhotoImage(eroded_display)
        self.eroded_canvas.delete("all")
        self.eroded_canvas.create_image(175, 175, image=self.result_photos['eroded'])
    
    def _resize_for_display(self, image, max_width, max_height):
        """Resize image to fit display area"""
        width_scale = max_width / image.size[0]
        height_scale = max_height / image.size[1]
        scale = min(width_scale, height_scale, 1.0)
        
        new_size = (int(image.size[0] * scale), int(image.size[1] * scale))
        return image.resize(new_size, Image.Resampling.LANCZOS)
    
    def show_message(self, title, message, msg_type="info"):
        """Show a message dialog"""
        if msg_type == "error":
            messagebox.showerror(title, message)
        elif msg_type == "warning":
            messagebox.showwarning(title, message)
        else:
            messagebox.showinfo(title, message)
