"""
Player class - The conductor character with camera controls and interaction abilities.
"""

from ursina import *
from imageManager import ImageManager
import math

class Player(Entity):
    def __init__(self, position=(0, 2, -12)):  # Lowered position, behind the orchestra
        super().__init__()
        
        # Player properties
        self.position = position
        self.speed = 5.0
        
        # Camera properties
        self.camera_height = 8  # Lowered camera height
        self.camera_distance = 15  # Distance from player
        self.mouse_sensitivity = 100  # Mouse sensitivity for rotation
        self.camera_rotation_x = 0
        self.camera_rotation_y = 0
        
        # Visual representation
        self.setup_visual()
        
        # Camera setup (third-person view)
        self.setup_camera()
        
        # Interaction properties
        self.interaction_range = 10.0
        self.last_click_time = 0
        self.click_cooldown = 0.5  # Seconds between clicks
        
        # Image manager for fallback graphics
        self.image_manager = ImageManager()
        
        # Conductor baton (visual feedback)
        self.setup_baton()
        
        # Mouse capture for camera control
        self.mouse_captured = False
        
    def setup_visual(self):
        """Set up the visual representation of the conductor"""
        try:
            self.model = 'cube'
            self.texture = self.image_manager.get_image("conductor")
            self.color = color.white
        except:
            # Fallback to colored cube
            self.model = 'cube'
            self.color = color.gold
            
        self.scale = (0.8, 0.8, 0.8)
        
        # Add collider
        self.collider = 'box'
        
    def setup_camera(self):
        """Set up the camera for third-person view"""
        # Position camera behind and above the player
        camera.position = (self.position.x, self.position.y + self.camera_height, self.position.z + self.camera_distance)
        camera.rotation_x = -20  # Slight downward angle to see the orchestra
        
        # Don't parent camera to player - we'll control it manually
        camera.parent = None
        
    def setup_baton(self):
        """Set up conductor baton for visual feedback"""
        self.baton = Entity(
            parent=self,
            model='cube',
            scale=(0.1, 0.1, 1.0),
            position=(0.5, 0.5, 0),
            color=color.white,
            rotation=(0, 0, 45)
        )
        
        # Baton animation properties
        self.baton_base_rotation = 45
        self.baton_animation_time = 0
        
    def update(self):
        """Update player state each frame"""
        # Handle mouse capture for camera control
        self.handle_mouse_capture()
        
        # Handle camera rotation with mouse
        self.handle_camera_rotation()
        
        # Handle movement (limited in conductor role)
        self.handle_movement()
        
        # Handle interactions
        self.handle_interactions()
        
        # Animate baton
        self.animate_baton()
        
        # Update camera position
        self.update_camera()
        
    def handle_mouse_capture(self):
        """Handle mouse capture for camera control"""
        # Toggle mouse capture with right mouse button
        if mouse.right:
            if not self.mouse_captured:
                self.mouse_captured = True
                mouse.locked = True
        else:
            if self.mouse_captured:
                self.mouse_captured = False
                mouse.locked = False
                
    def handle_camera_rotation(self):
        """Handle camera rotation with mouse input"""
        if self.mouse_captured:
            # Get mouse movement
            mouse_movement = mouse.velocity
            
            # Apply rotation based on mouse movement
            self.camera_rotation_y += mouse_movement[0] * self.mouse_sensitivity * time.dt
            self.camera_rotation_x -= mouse_movement[1] * self.mouse_sensitivity * time.dt
            
            # Clamp vertical rotation
            self.camera_rotation_x = max(-80, min(80, self.camera_rotation_x))
            
    def handle_movement(self):
        """Handle player movement (limited movement for conductor)"""
        # Conductor moves slightly to get better view/position
        if held_keys['a'] or held_keys['left arrow']:
            self.x -= self.speed * time.dt
        if held_keys['d'] or held_keys['right arrow']:
            self.x += self.speed * time.dt
        if held_keys['w'] or held_keys['up arrow']:
            self.z += self.speed * time.dt
        if held_keys['s'] or held_keys['down arrow']:
            self.z -= self.speed * time.dt
            
        # Keep player in front of stage area
        self.x = max(-32, min(32, self.x))
        self.z = max(-24, min(24, self.z))
        
    def handle_interactions(self):
        """Handle player interactions"""
        current_time = time.time()
        
        # Handle Q key for removing bad musicians
        if held_keys['q'] and current_time - self.last_click_time > self.click_cooldown:
            self.kill()
            self.last_click_time = current_time
            
        # Handle space for synchronization
        if held_keys['space']:
            self.synchronize()
            
    def kill(self):
        """Fire a raycast and remove bad musicians"""
        # Use raycast from camera through mouse position for targeting
        if mouse.world_point:
            # Find entities near the mouse world point
            hit_entities = []
            
            # Check all entities in scene
            for entity in scene.entities:
                if hasattr(entity, 'bad_actor') and entity.bad_actor and entity.active:
                    # Check if entity is within interaction range of the mouse cursor
                    distance = distance_2d(entity.world_position, mouse.world_point)
                    if distance < 3.0:  # Within range for targeting
                        hit_entities.append(entity)
            
            # Remove the closest bad actor
            if hit_entities:
                closest = min(hit_entities, key=lambda e: distance_2d(e.world_position, mouse.world_point))
                self.remove_musician(closest)
                
                # Visual feedback
                self.show_removal_effect(closest.world_position)
        else:
            # Fallback: if no mouse world point, try to find bad actors in front of camera
            # Create a raycast from camera forward
            camera_forward = Vec3(0, 0, 1) * camera.rotation
            hit_entities = []
            
            for entity in scene.entities:
                if hasattr(entity, 'bad_actor') and entity.bad_actor and entity.active:
                    # Check if entity is in front of camera and within range
                    entity_direction = (entity.world_position - camera.world_position).normalized()
                    dot_product = entity_direction.dot(camera_forward)
                    
                    if dot_product > 0.7:  # Entity is roughly in front of camera
                        distance = distance_3d(entity.world_position, camera.world_position)
                        if distance < 20.0:  # Within range
                            hit_entities.append((entity, distance))
            
            # Remove the closest bad actor
            if hit_entities:
                closest = min(hit_entities, key=lambda e: e[1])[0]
                self.remove_musician(closest)
                self.show_removal_effect(closest.world_position)
                
    def remove_musician(self, musician):
        """Remove a musician from the orchestra"""
        if hasattr(musician, 'remove_from_orchestra'):
            musician.remove_from_orchestra()
            print(f"Conductor removed bad musician!")
            
            # Trigger baton animation
            self.trigger_baton_animation()
            
    def show_removal_effect(self, position):
        """Show visual effect when removing a musician"""
        # Create temporary particle effect
        for i in range(10):
            particle = Entity(
                model='cube',
                scale=0.1,
                position=position,
                color=color.red,
                billboard=True
            )
            
            # Animate particle
            particle.animate_position(
                (position[0] + random.uniform(-2, 2), 
                 position[1] + random.uniform(0, 3), 
                 position[2] + random.uniform(-2, 2)),
                duration=1.0
            )
            
            # Fade out and destroy
            particle.animate_color(color.clear, duration=1.0)
            destroy(particle, delay=1.0)
            
    def synchronize(self):
        """Conductor synchronizes the orchestra"""
        # Visual feedback
        self.trigger_baton_animation()
        
        # Color feedback
        self.color = color.lime
        invoke(setattr, self, 'color', color.gold, delay=0.2)
        
        # Sound feedback (could add conductor audio here)
        print("Conductor synchronizing orchestra!")
        
    def trigger_baton_animation(self):
        """Trigger baton animation for conductor actions"""
        self.baton_animation_time = 1.0
        
    def animate_baton(self):
        """Animate the conductor baton"""
        if self.baton_animation_time > 0:
            # Animate baton during conductor actions
            self.baton_animation_time -= time.dt * 2
            
            # Rotate baton
            rotation_amplitude = 30 * self.baton_animation_time
            self.baton.rotation_z = self.baton_base_rotation + sin(time.time() * 20) * rotation_amplitude
            
            # Scale baton
            scale_multiplier = 1.0 + 0.3 * self.baton_animation_time
            self.baton.scale = (0.1 * scale_multiplier, 0.1 * scale_multiplier, 1.0 * scale_multiplier)
        else:
            # Return to normal state
            self.baton.rotation_z = self.baton_base_rotation
            self.baton.scale = (0.1, 0.1, 1.0)
            
    def update_camera(self):
        """Update camera position and rotation"""
        # Calculate camera position based on player position and rotation
        # Convert rotation to radians
        rotation_y_rad = math.radians(self.camera_rotation_y)
        rotation_x_rad = math.radians(self.camera_rotation_x)
        
        # Calculate camera offset based on rotation
        offset_x = math.sin(rotation_y_rad) * self.camera_distance
        offset_z = math.cos(rotation_y_rad) * self.camera_distance
        offset_y = self.camera_height + math.sin(rotation_x_rad) * self.camera_distance * 0.3
        
        # Set camera position
        target_position = (
            self.position.x - offset_x,
            self.position.y + offset_y,
            self.position.z - offset_z
        )
        
        camera.world_position = lerp(camera.world_position, target_position, time.dt * 5)
        
        # Set camera rotation to look at the player
        camera.rotation_y = self.camera_rotation_y
        camera.rotation_x = self.camera_rotation_x
        
    def get_interaction_targets(self):
        """Get all interactable entities within range"""
        targets = []
        
        for entity in scene.entities:
            if hasattr(entity, 'bad_actor') and entity.bad_actor:
                distance = distance_2d(self.world_position, entity.world_position)
                if distance <= self.interaction_range:
                    targets.append(entity)
                    
        return targets
        
    def show_interaction_hint(self):
        """Show visual hint for available interactions"""
        targets = self.get_interaction_targets()
        
        if targets:
            # Show hint text
            hint_text = Text(
                text="Q: Remove bad musician",
                position=(0, -0.4),
                scale=1.2,
                color=color.red,
                background=True
            )
            
            # Remove hint after short time
            destroy(hint_text, delay=2.0)
            
    def cleanup(self):
        """Clean up player resources"""
        if hasattr(self, 'baton'):
            self.baton.disable()
        self.disable()
