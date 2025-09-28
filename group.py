"""
Group class - Manages a group of musicians with shared audio and positioning.
"""

from ursina import *
from musician import Musician
import random
import statistics
import math

class Group(Entity):
    def __init__(self, group_id, num_musicians=5, width=3, length=2, position=(0, 0, 0)):
        super().__init__()
        self.group_id = group_id
        self.num_musicians = num_musicians
        self.position = position
        self.width = width
        self.length = length
        self.active_musicians = []
        # Musician management
        # self.target_bpm = audioManager.alltracks[track]["bpm"]
        # self.current_bpm = self.target_bpm
        
        # Group area visualization
        self.setup_group_area()
        
        # Initialize musicians
        self.create_musicians()
        self
        
    def setup_group_area(self):
        """Set up visual representation of the group area"""
        # Create a semi-transparent platform for the group
        self.platform = Entity(
            model='cube',
            position=self.position,
            scale=(self.width, 0.1, self.length),
            color=color.white33,  # Semi-transparent
            texture='white_cube'
        )
        
        # Add group label
        self.label = Text(
            text=f"Group",
            position=(self.position.x, self.position.y + 1, self.position.z),
            scale=2,
            color=color.white
        )
        
    def create_musicians(self):
        """Create and position musicians in semicircle formation"""
        self.musicians = []
        
        # Semicircle parameters
        semicircle_radius = 8  # Radius of the semicircle
        semicircle_center = (0, 0, 0)  # Center of the semicircle
        
        # Calculate the pie cut angle for this group
        # Each group gets a portion of the semicircle (180 degrees)
        group_index = ord(self.group_id) - ord('A')  # Convert A=0, B=1, C=2, etc.
        total_groups = 3  # We have 3 groups (A, B, C)
        
        # Calculate start and end angles for this group's pie cut
        pie_cut_angle = 180 / total_groups  # Each group gets 60 degrees
        start_angle = -90 + (group_index * pie_cut_angle)  # Start from -90 degrees (left side)
        end_angle = start_angle + pie_cut_angle
        
        for i in range(self.num_musicians):
            # Calculate angle within this group's pie cut
            # Distribute musicians evenly within the pie cut
            angle_ratio = i / (self.num_musicians - 1) if self.num_musicians > 1 else 0.5
            angle = start_angle + (end_angle - start_angle) * angle_ratio
            angle_rad = math.radians(angle)
            
            # Calculate position on semicircle
            x = semicircle_center[0] + semicircle_radius * math.cos(angle_rad)
            z = semicircle_center[2] + semicircle_radius * math.sin(angle_rad)
            
            # Add some variation in radius for depth
            radius_variation = 0.3 * (i % 2)  # Alternate between rows
            x = x + radius_variation * math.cos(angle_rad)
            z = z + radius_variation * math.sin(angle_rad)
            
            # Create musician
            musician = Musician(
                position=(x, self.position.y + 0.5, z),
                group_id=self.group_id,
                musician_id=i
            )
            
            self.musicians.append(musician)
            self.active_musicians.append(musician)
            
    def determineAudio(self, beat_align):
        if not self.active_musicians:
            return [0.0, 0.0]
        active_count = len(self.active_musicians)
        total_count = len(self.musicians)

        current_volume = active_count / total_count 
        
        offsets = 0
        bad_actor_count = 0
        
        for musician in self.active_musicians:
            if musician.active:
                offsets += musician.get_audio_offset()
                
                if musician.bad_actor:
                    bad_actor_count += 1
        offsets = min(((1 - offsets/max(1, bad_actor_count)) + beat_align), 1) # maximum 1 = no alignment / speed diff
        print("Offsets:", offsets, "Bad Actors:", bad_actor_count, "Active:", active_count, "Total:", total_count, "Volume:", current_volume)
        
        return [current_volume, offsets]
    
    def get_bad_actor_count(self):
        """Get number of bad actors in the group"""
        return sum(1 for musician in self.active_musicians if musician.bad_actor)
    
    def get_group_performance(self):
        """Get overall group performance score (0.0 to 1.0)"""
        if not self.active_musicians:
            return 0.0
            
        total_performance = sum(musician.performance_quality for musician in self.active_musicians)
        return total_performance / len(self.active_musicians)
    
    def update(self):
        """Update group state"""
        # Update all active musicians
        for musician in self.active_musicians:
            musician.update()
        # Update visual feedback based on performance
        performance = self.get_group_performance()
        if performance < 0.5:
            self.platform.color = color.red
        elif performance < 0.8:
            self.platform.color = color.orange
        else:
            self.platform.color = color.green
        
        for musician in self.active_musicians:
            if not musician.active:
                self.active_musicians.remove(musician)
            
    def cleanup(self):
        """Clean up group resources"""
        for musician in self.musicians:
            if hasattr(musician, 'disable'):
                musician.disable()
        if hasattr(self, 'platform'):
            self.platform.disable()
        if hasattr(self, 'label'):
            self.label.disable()
