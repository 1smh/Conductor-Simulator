"""
ImageManager - Manages all image assets with fallback support.
"""

import os
from ursina import load_texture, color

class ImageManager:
    def __init__(self, images_folder="images"):
        self.images_folder = images_folder
        self.texture_cache = {}
        self.fallback_textures = {}
        
        # Create images directory if it doesn't exist
        if not os.path.exists(self.images_folder):
            os.makedirs(self.images_folder)
            print(f"Created images directory: {self.images_folder}")
            
        # Create fallback textures
        self.create_fallback_textures()
        
    def create_fallback_textures(self):
        """Create simple fallback textures for when images are missing"""
        # Create a simple white texture as base
        self.fallback_textures['default'] = 'white_cube'
        
        # Create colored textures for different groups
        self.fallback_textures['musician_A'] = 'white_cube'
        self.fallback_textures['musician_B'] = 'white_cube'
        self.fallback_textures['musician_C'] = 'white_cube'
        self.fallback_textures['musician_D'] = 'white_cube'
        self.fallback_textures['musician_E'] = 'white_cube'
        
        # Stage and UI elements
        self.fallback_textures['stage'] = 'white_cube'
        self.fallback_textures['conductor'] = 'white_cube'
        self.fallback_textures['background'] = 'white_cube'
        
    def get_image(self, image_name, fallback_name=None):
        """Load an image with fallback support"""
        # Check cache first
        if image_name in self.texture_cache:
            return self.texture_cache[image_name]
            
        # Try to load the actual image
        image_path = os.path.join(self.images_folder, f"{image_name}.png")
        if os.path.exists(image_path):
            try:
                texture = load_texture(image_path)
                self.texture_cache[image_name] = texture
                return texture
            except Exception as e:
                print(f"Failed to load texture {image_path}: {e}")
        
        # Try alternative formats
        for ext in ['.jpg', '.jpeg', '.bmp', '.tga']:
            alt_path = os.path.join(self.images_folder, f"{image_name}{ext}")
            if os.path.exists(alt_path):
                try:
                    texture = load_texture(alt_path)
                    self.texture_cache[image_name] = texture
                    return texture
                except Exception as e:
                    print(f"Failed to load texture {alt_path}: {e}")
        
        # Use fallback
        fallback = fallback_name or image_name
        if fallback in self.fallback_textures:
            return self.fallback_textures[fallback]
        else:
            return self.fallback_textures['default']
    
    def get_texture(self, texture_name):
        """Alias for get_image for consistency"""
        return self.get_image(texture_name)
    
    def create_simple_texture(self, name, color_value, size=(64, 64)):
        """Create a simple colored texture programmatically"""
        # This would create a simple colored texture
        # For now, we'll use Ursina's built-in textures
        color_map = {
            'red': 'red_cube',
            'green': 'green_cube',
            'blue': 'blue_cube',
            'yellow': 'yellow_cube',
            'orange': 'orange_cube',
            'purple': 'purple_cube',
            'white': 'white_cube',
            'black': 'black_cube'
        }
        
        return color_map.get(color_value.lower(), 'white_cube')
    
    def list_available_images(self):
        """List all available images in the images folder"""
        if not os.path.exists(self.images_folder):
            return []
            
        images = []
        for file in os.listdir(self.images_folder):
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tga')):
                images.append(file)
                
        return images
    
    def preload_images(self, image_list):
        """Preload a list of images into cache"""
        for image_name in image_list:
            self.get_image(image_name)
    
    def clear_cache(self):
        """Clear the texture cache"""
        self.texture_cache.clear()
        
    def get_image_info(self, image_name):
        """Get information about an image file"""
        image_path = os.path.join(self.images_folder, f"{image_name}.png")
        if os.path.exists(image_path):
            try:
                stat = os.stat(image_path)
                return {
                    'exists': True,
                    'path': image_path,
                    'size': stat.st_size,
                    'modified': stat.st_mtime
                }
            except:
                pass
                
        return {'exists': False}
