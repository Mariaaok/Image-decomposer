from model import ImageProcessingModel
from chain_handlers import ProcessingPipeline


class ImageSegmentationController:
    """
    Controller layer that coordinates between Model and View.
    Handles user actions and updates the view accordingly.
    """
    
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.pipeline = ProcessingPipeline()
        
        # Set controller reference in view
        self.view.set_controller(self)
    
    def load_image(self, file_path):
        """Load an image from file path"""
        try:
            self.model.load_image(file_path)
            original_image = self.model.get_original_image()
            self.view.display_original_image(original_image)
        except Exception as e:
            self.view.show_message("Error", f"Failed to load image: {str(e)}", "error")
    
    def add_background_point(self, x, y):
        """Add a background point"""
        self.model.add_background_point(x, y)
    
    def add_object_point(self, x, y):
        """Add an object point"""
        self.model.add_object_point(x, y)
    
    def clear_points(self):
        """Clear all selected points"""
        self.model.clear_points()
    
    def process_image(self):
        """Process the image using the Chain of Responsibility pipeline"""
        result = self.pipeline.process(self.model)
        
        if result['success']:
            # Display results
            self.view.display_results(
                result['object'],
                result['background'],
                result['eroded']
            )
            self.view.show_message("Success", "Image processing completed successfully!")
        else:
            # Show error message
            self.view.show_message("Error", result.get('error', 'Processing failed'), "error")
    
    def save_image(self, image_type, file_path):
        """Save a processed image"""
        try:
            success = self.model.save_image(image_type, file_path)
            if success:
                self.view.show_message("Success", f"Image saved successfully to {file_path}")
            else:
                self.view.show_message("Error", "Failed to save image", "error")
        except Exception as e:
            self.view.show_message("Error", f"Failed to save image: {str(e)}", "error")
