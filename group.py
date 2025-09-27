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
        
        # Group properties
        self.group_id = group_id
        self.num_musicians = num_musicians
        self.position = position
        self.width = width
        self.length = length
        
        # Musician management
        self.musicians = []
        self.active_musicians = []
        
        # Audio properties
        self.base_volume = 1.0
        self.current_volume = 1.0
        self.audio_offset = 0.0
        self.target_bpm = 90.0  # Beats per minute
        self.current_bpm = 90.0
        
        # Group area visualization
        self.setup_group_area()
        
        # Initialize musicians
        self.create_musicians()
        
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
            text=f"Group {self.group_id}",
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
            
    def determine_audio(self, beat_align):
        """Calculate audio settings for the group based on musician performance"""
        if not self.active_musicians:
            self.current_volume = 0.0
            self.audio_offset = 0.0
            return 0.0
            
        # Calculate volume based on number of active musicians
        active_count = len(self.active_musicians)
        total_count = len(self.musicians)
        volume_ratio = active_count / total_count if total_count > 0 else 0
        self.current_volume = self.base_volume * volume_ratio
        
        # Calculate standard deviation of offsets from target BPM instead of average
        offsets = []
        bad_actor_count = 0
        
        for musician in self.active_musicians:
            if musician.active:
                offset = musician.get_audio_offset(self.target_bpm, beat_align)
                offsets.append(offset)
                
                if musician.bad_actor:
                    bad_actor_count += 1
        
        # Calculate standard deviation of offsets from target BPM
        if len(offsets) > 1:
            self.audio_offset = statistics.stdev(offsets)
            #print(f"Group {self.group_id} audio offset (std dev): {self.audio_offset:.2f}")
        elif len(offsets) == 1:
            self.audio_offset = abs(offsets[0])
        else:
            self.audio_offset = 0.0
        
        # Calculate BPM variation based on bad actors
        bad_actor_ratio = bad_actor_count / len(self.active_musicians) if self.active_musicians else 0
        bpm_variation = bad_actor_ratio * 20  # Up to 20 BPM variation
        self.current_bpm = self.target_bpm + random.uniform(-bpm_variation, bpm_variation)
        
        # Apply beat alignment (conductor's intervention)
        if beat_align > 0:
            self.audio_offset *= (1.0 - beat_align)
            self.current_bpm = lerp(self.current_bpm, self.target_bpm, beat_align)
            
        return abs(self.audio_offset)
    
    def remove_musician(self, musician):
        """Remove a musician from the group"""
        if musician in self.active_musicians:
            musician.remove_from_orchestra()
            self.active_musicians.remove(musician)
            #print(f"Removed musician from Group {self.group_id}")
            
    def get_active_count(self):
        """Get number of active musicians"""
        return len(self.active_musicians)
    
    def get_total_count(self):
        """Get total number of musicians"""
        return len(self.musicians)
    
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
            
    def cleanup(self):
        """Clean up group resources"""
        for musician in self.musicians:
            if hasattr(musician, 'disable'):
                musician.disable()
        if hasattr(self, 'platform'):
            self.platform.disable()
        if hasattr(self, 'label'):
            self.label.disable()
