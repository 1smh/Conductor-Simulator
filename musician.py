<<<<<<< Updated upstream
<<<<<<< Updated upstream
"""
Musician class - Individual musician entities that can become bad actors.
"""

from ursina import *
import random
from imageManager import ImageManager

class Musician(Entity):
    def __init__(self, position=(0, 0, 0), group_id="", musician_id=0):
        super().__init__()
        
        # Basic properties
        self.position = position
        self.group_id = group_id
        self.musician_id = musician_id
        
        # Musician state
=======
=======
>>>>>>> Stashed changes
from ursina import *
from ursina.prefabs.health_bar import HealthBar
from ursina.prefabs.first_person_controller import FirstPersonController


shootables_parent = Entity()
mouse.traverse_target = shootables_parent

class Musician(Entity):
    
    def __init__(self,  **kwargs ):
        super().__init__(parent=shootables_parent, model='cube', scale_y=2, origin_y=-.5, color=color.light_gray, collider='box', **kwargs)
        self.health_bar = Entity(parent=self, y=1.2, model='cube', color=color.red, world_scale=(1.5,.1,.1))
        self.max_hp = 1
        self.hp = self.max_hp
        self.instrument = Entity(parent=self, model='violinprefab', position=(-0.4,0.8,1), scale=0.05, rotation=(-80,90,-60))
        #chris
         # Musician state
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
        self.bad_actor = False
        self.active = True
        self.performance_quality = 1.0  # 1.0 = perfect, 0.0 = terrible
        
        # Bad actor timing - check every 5 seconds instead of every frame
        self.bad_actor_probability = 0.2  # 20% chance every 5 seconds
        self.last_bad_actor_check = 0
        self.bad_actor_check_interval = 5.0  # Check every 5 seconds
        
        # Performance drift (how much they can drift from perfect timing)
        self.drift_factor = 0.0  # Will be modified by bad actor status
<<<<<<< Updated upstream
<<<<<<< Updated upstream
        
        # Image manager for fallback graphics
        self.image_manager = ImageManager()
        
        # Visual representation
        self.setup_visual()
        
    def setup_visual(self):
        """Set up the visual representation of the musician"""
        # Try to load a musician image, fallback to colored cube
        try:
            self.model = 'cube'
            self.texture = self.image_manager.get_image(f"musician_{self.group_id}")
            self.color = color.white
        except:
            # Fallback to colored cube based on group
            self.model = 'cube'
            self.color = self.get_group_color()
            
        # Scale and positioning
        self.scale = (0.5, 0.5, 0.5)
        
        # Add collider for interaction
        self.collider = 'box'
        
        # Add hover effect
        self.hover_color = color.red
        self.original_color = self.color
        
    def get_group_color(self):
        """Get color based on group ID"""
        colors = {
            'A': color.blue,
            'B': color.green, 
            'C': color.orange,
            'D': color.rgb(128, 0, 128),  # Purple using RGB
            'E': color.yellow
        }
        return colors.get(self.group_id, color.white)
    
    def update(self):
        """Update musician state each frame"""
        if not self.active:
=======
=======
>>>>>>> Stashed changes

    # def update(self):
    #     self.look_at_2d(player.position, 'y')

    def update(self):
        self.player = Entity( position=(0,100,-10), origin_y=-.5, speed=0)

        self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)
        self.look_at_2d(self.player.position, 'y')
        # hit_info = raycast(self.world_position + Vec3(0,1,0), self.forward, 30, ignore=(self,))
        # print(hit_info.entity)

        if not self.active:
            print("im dead")
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
            return
            
        # Check for bad actor status every 5 seconds instead of every frame
        current_time = time.time()
        if current_time - self.last_bad_actor_check >= self.bad_actor_check_interval:
            if random.random() < self.bad_actor_probability and not self.bad_actor:
                self.become_bad_actor()
            self.last_bad_actor_check = current_time
            
        # Visual feedback for bad actors
        if self.bad_actor:
            # Make bad actors more visually obvious
            self.color = color.red
<<<<<<< Updated upstream
<<<<<<< Updated upstream
            # Add slight pulsing effect
            self.scale = (0.6, 0.6, 0.6) + (sin(time.time() * 10) * 0.1, 
                                           sin(time.time() * 10) * 0.1, 
                                           sin(time.time() * 10) * 0.1)
        else:
            self.color = self.original_color
            self.scale = (0.5, 0.5, 0.5)
            
    def become_bad_actor(self):
        """Make this musician a bad actor"""
=======
    def become_bad_actor(self):
>>>>>>> Stashed changes
=======
    def become_bad_actor(self):
>>>>>>> Stashed changes
        self.bad_actor = True
        self.performance_quality = random.uniform(0.1, 0.5)  # Poor performance
        self.drift_factor = random.uniform(0.5, 2.0)  # High drift from perfect timing
        #print(f"Musician {self.group_id}-{self.musician_id} became a bad actor!")
<<<<<<< Updated upstream
<<<<<<< Updated upstream
        
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
    def improve_performance(self):
        """Improve musician performance (called when conductor intervenes)"""
        self.performance_quality = min(1.0, self.performance_quality + 0.2)
        self.drift_factor = max(0.0, self.drift_factor - 0.1)
        
    def get_audio_offset(self):
        """Calculate how much this musician's audio should be offset"""
        if not self.active:
            return 0.0
            
        # Bad actors create more offset
        if self.bad_actor:
            # Random offset based on drift factor
            offset = random.uniform(-self.drift_factor, self.drift_factor)
            return offset * (1.0 - self.performance_quality)
        else:
            # Good musicians have minimal offset
            return random.uniform(-0.1, 0.1) * (1.0 - self.performance_quality)
    
    def get_volume_multiplier(self):
        """Get volume multiplier based on performance"""
        if not self.active:
            return 0.0
        return self.performance_quality
    
<<<<<<< Updated upstream
<<<<<<< Updated upstream
    def remove_from_orchestra(self):
        """Remove this musician from the orchestra"""
        self.active = False
        self.bad_actor = False
        self.color = color.black
        self.scale = (0.5, 0.5, 0.5)
        #print(f"Musician {self.group_id}-{self.musician_id} removed from orchestra")
        
    def on_mouse_enter(self):
        """Handle mouse hover"""
        if self.active:
            self.color = self.hover_color
            
    def on_mouse_exit(self):
        """Handle mouse exit"""
        if self.active:
            self.color = self.original_color if not self.bad_actor else color.red
=======
=======
>>>>>>> Stashed changes
        #print(f"Musician {self.group_id}-{self.musician_id} removed from orchestra")
        



    @property
    def hp(self):
        return self._hp

    #upon setting hp anytime it appears this would run
    @hp.setter
    def hp(self, value):
        self._hp = value
        if value <= 0:

            self.active = False
            self.bad_actor = False
            self.color = color.black
            self.scale = (0.5, 0.5, 0.5)
            print("dead")
            return

        self.health_bar.world_scale_x = self.hp / self.max_hp * 1.5
        self.health_bar.alpha = 1
<<<<<<< Updated upstream
    
>>>>>>> Stashed changes
=======
    
>>>>>>> Stashed changes
