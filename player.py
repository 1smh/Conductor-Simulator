"""
Player class - The conductor character with camera controls and interaction abilities.
Uses FirstPersonController prefab with static y level for conductor positioning.
"""

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from imageManager import ImageManager

class Player(FirstPersonController):
    def __init__(self, position=(0,0,0)):  # Position behind the orchestra
        # Initialize FirstPersonController with conductor-specific settings
        super().__init__(gravity=0, mouse_sensitivity=Vec2(40, 40))
        # Store original y position for static y level
        # self.static_y = position[1]
        
        # Visual representation
        self.setup_visual()
        
        # Interaction properties
        self.interaction_range = 10.0
        self.last_click_time = 0
        self.click_cooldown = 0.5  # Seconds between clicks
        
        # Image manager for fallback graphics
        self.image_manager = ImageManager()
        
        # Conductor baton (visual feedback)
        self.setup_baton()
        
        # Set window title
        window.title = "One-Armed Band - Conductor"
        
        # Track window size for resize detection
        self._last_window_size = window.size if hasattr(window, 'size') else None
        
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
        self.position = (0, 5, -20)  # Start position behind orchestra
        # Add collider
        self.collider = 'box'
        
        
    def setup_baton(self):
        """Set up conductor baton for visual feedback"""
        self.baton = Entity(
            parent=self,
            model='cube',
            scale=(0.1, 0.1, 1.0),
            position=self.position,
            color=color.white,
            rotation=(0, 0, 45)
        )
        
        # Baton animation properties
        self.baton_base_rotation = 45
        self.baton_animation_time = 0
        
    def input(self, key):
        # Handle escape key to exit cursor (unlock mouse)
        if key == 'escape':
            mouse.locked = not mouse.locked
            return  # Don't call super().input() to prevent other escape handling
        
        # Handle left mouse click to re-lock cursor when unlocked
        if key == 'left mouse down' and not mouse.locked:
            mouse.locked = True
            mouse.position = (0, 0)  # Reset mouse to center
            return
        
        # Let parent FirstPersonController handle other keys
        super().input(key)
                
    
    def update(self):
        # Call parent update for standard FirstPersonController behavior
        super().update()
        
        # Keep y position static (override any gravity or movement)
        self.y = 5  # Keep at fixed height
        
        # Keep conductor in front of stage area (movement constraints)
        self.x = max(-32, min(32, self.x))
        self.z = max(-24, min(24, self.z))
        
        # Handle window resize detection (continuous monitoring)
        self.handle_window_resize()
        
        # Handle interactions
        self.handle_interactions()
        
        # Animate baton
        self.animate_baton()
        
    def handle_window_resize(self):
        """Handle window resize events"""
        if hasattr(window, 'size') and hasattr(self, '_last_window_size'):
            if window.size != self._last_window_size:
                if mouse.locked:
                    mouse.position = (0, 0)
                    mouse.velocity = Vec2(0, 0)
                # Update the tracking variable to prevent repeated resize detection
                self._last_window_size = window.size
                print("Window resized - mouse position reset")
        
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
        # Use FirstPersonController's camera for targeting
        # Create a raycast from camera forward
        if mouse.hovered_entity:
            target = mouse.hovered_entity
            if hasattr(target, 'bad_actor'):
                self.remove_musician(target)
                self.show_removal_effect(target.world_position)
            else:
                print("No bad musician targeted!")
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
        self.baton.position = self.position
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
