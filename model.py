import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
import cv2


class ImageProcessingModel:
    """
    Model layer for image processing operations.
    Handles image loading, K-Means clustering, and erosion operations.
    """
    
    def __init__(self):
        self.original_image = None
        self.image_array = None
        self.background_points = []
        self.object_points = []
        self.segmented_object = None
        self.segmented_background = None
        self.eroded_object = None
        
    def load_image(self, image_path):
        """Load an image from file path"""
        self.original_image = Image.open(image_path)
        self.image_array = np.array(self.original_image)
        self.background_points = []
        self.object_points = []
        return True
    
    def add_background_point(self, x, y):
        """Add a point marked as background"""
        if self.image_array is not None:
            self.background_points.append((x, y))
            return True
        return False
    
    def add_object_point(self, x, y):
        """Add a point marked as object"""
        if self.image_array is not None:
            self.object_points.append((x, y))
            return True
        return False
    
    def clear_points(self):
        """Clear all selected points"""
        self.background_points = []
        self.object_points = []
    
    def perform_kmeans_segmentation(self):
        """
        Perform K-Means clustering based on selected points.
        Returns True if successful, False otherwise.
        """
        if not self.background_points or not self.object_points:
            return False
        
        if self.image_array is None:
            return False
        
        h, w = self.image_array.shape[:2]
        
        # Prepare training data from selected points
        background_pixels = []
        for x, y in self.background_points:
            if 0 <= y < h and 0 <= x < w:
                background_pixels.append(self.image_array[y, x])
        
        object_pixels = []
        for x, y in self.object_points:
            if 0 <= y < h and 0 <= x < w:
                object_pixels.append(self.image_array[y, x])
        
        if not background_pixels or not object_pixels:
            return False
        
        # Create training data with labels
        X_train = np.array(background_pixels + object_pixels)
        y_train = np.array([0] * len(background_pixels) + [1] * len(object_pixels))
        
        # Reshape image for clustering
        pixels = self.image_array.reshape(-1, self.image_array.shape[-1])
        
        # Train K-Means with 2 clusters
        kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
        kmeans.fit(X_train)
        
        # Predict labels for all pixels
        labels = kmeans.predict(pixels)
        
        # Determine which cluster is object and which is background
        # Use majority voting from labeled points
        bg_cluster_votes = kmeans.predict(background_pixels)
        bg_cluster = np.bincount(bg_cluster_votes).argmax()
        obj_cluster = 1 - bg_cluster
        
        # Create mask
        mask = labels.reshape(h, w)
        object_mask = (mask == obj_cluster).astype(np.uint8)
        background_mask = (mask == bg_cluster).astype(np.uint8)
        
        # Create segmented images
        self.segmented_object = self.image_array.copy()
        self.segmented_background = self.image_array.copy()
        
        # Set background pixels to white in object image
        self.segmented_object[background_mask == 1] = [255, 255, 255]
        
        # Set object pixels to white in background image
        self.segmented_background[object_mask == 1] = [255, 255, 255]
        
        # Apply erosion to object for serrated edge effect
        self.apply_erosion(object_mask)
        
        return True
    
    def apply_erosion(self, object_mask):
        """Apply erosion to create serrated edge effect"""
        # Create erosion kernel
        kernel = np.ones((3, 3), np.uint8)
        
        # Erode the mask
        eroded_mask = cv2.erode(object_mask, kernel, iterations=1)
        
        # Create eroded object image
        self.eroded_object = self.image_array.copy()
        
        # Find border pixels (pixels that were removed by erosion)
        border_pixels = object_mask - eroded_mask
        
        # Set border pixels to white (background color)
        self.eroded_object[border_pixels == 1] = [255, 255, 255]
        
        # Set background pixels to white
        self.eroded_object[object_mask == 0] = [255, 255, 255]
    
    def get_original_image(self):
        """Get original image as PIL Image"""
        if self.original_image:
            return self.original_image
        return None
    
    def get_segmented_object(self):
        """Get segmented object image as PIL Image"""
        if self.segmented_object is not None:
            return Image.fromarray(self.segmented_object)
        return None
    
    def get_segmented_background(self):
        """Get segmented background image as PIL Image"""
        if self.segmented_background is not None:
            return Image.fromarray(self.segmented_background)
        return None
    
    def get_eroded_object(self):
        """Get eroded object image with serrated edges as PIL Image"""
        if self.eroded_object is not None:
            return Image.fromarray(self.eroded_object)
        return None
    
    def save_image(self, image_type, file_path):
        """Save a specific image type to file"""
        image = None
        if image_type == "object":
            image = self.get_segmented_object()
        elif image_type == "background":
            image = self.get_segmented_background()
        elif image_type == "eroded":
            image = self.get_eroded_object()
        
        if image:
            image.save(file_path)
            return True
        return False
