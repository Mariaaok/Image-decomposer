from tkinterdnd2 import TkinterDnD
from model import ImageProcessingModel
from view import ImageSegmentationView
from controller import ImageSegmentationController


def main():
    """Main entry point for the application"""
    # Create root window with drag-and-drop support
    root = TkinterDnD.Tk()
    
    # Create MVC components
    model = ImageProcessingModel()
    view = ImageSegmentationView(root)
    controller = ImageSegmentationController(model, view)
    
    # Start the application
    root.mainloop()


if __name__ == "__main__":
    main()
