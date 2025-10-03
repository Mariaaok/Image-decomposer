from abc import ABC, abstractmethod


class Handler(ABC):
    """
    Abstract Handler for Chain of Responsibility pattern.
    Each handler processes a request and passes it to the next handler.
    """
    
    def __init__(self):
        self._next_handler = None
    
    def set_next(self, handler):
        """Set the next handler in the chain"""
        self._next_handler = handler
        return handler
    
    @abstractmethod
    def handle(self, request):
        """Process the request"""
        if self._next_handler:
            return self._next_handler.handle(request)
        return request


class ValidationHandler(Handler):
    """Validate that an image has been loaded"""
    
    def handle(self, request):
        model = request.get('model')
        
        if model.original_image is None:
            return {'success': False, 'error': 'No image loaded. Please upload an image first.'}
        
        return super().handle(request)


class PointSelectionHandler(Handler):
    """Validate that sufficient points have been selected"""
    
    def handle(self, request):
        model = request.get('model')
        
        if not model.background_points:
            return {'success': False, 'error': 'No background points selected. Please select at least one background point.'}
        
        if not model.object_points:
            return {'success': False, 'error': 'No object points selected. Please select at least one object point.'}
        
        return super().handle(request)


class SegmentationHandler(Handler):
    """Perform K-Means segmentation"""
    
    def handle(self, request):
        model = request.get('model')
        
        success = model.perform_kmeans_segmentation()
        
        if not success:
            return {'success': False, 'error': 'Segmentation failed. Please ensure points are properly selected.'}
        
        return super().handle(request)


class ResultGenerationHandler(Handler):
    """Generate final results"""
    
    def handle(self, request):
        model = request.get('model')
        
        object_img = model.get_segmented_object()
        background_img = model.get_segmented_background()
        eroded_img = model.get_eroded_object()
        
        if object_img and background_img and eroded_img:
            return {
                'success': True,
                'object': object_img,
                'background': background_img,
                'eroded': eroded_img
            }
        
        return {'success': False, 'error': 'Failed to generate results.'}


class ProcessingPipeline:
    """
    Sets up the Chain of Responsibility for image processing.
    """
    
    def __init__(self):
        # Create handlers
        self.validation = ValidationHandler()
        self.point_selection = PointSelectionHandler()
        self.segmentation = SegmentationHandler()
        self.result_generation = ResultGenerationHandler()
        
        # Chain handlers together
        self.validation.set_next(self.point_selection).set_next(
            self.segmentation).set_next(self.result_generation)
    
    def process(self, model):
        """Execute the processing pipeline"""
        request = {'model': model}
        return self.validation.handle(request)
