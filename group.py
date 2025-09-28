"""
Group class - Manages a group of musicians with shared audio and positioning.
"""
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
from ursina.prefabs.ursfx import ursfx

from musician import Musician
import random
import statistics
import math

class Group():

    def __init__(self, radius, height, count, group):
        center = Vec3(0,height,-10)
        start_angle = math.radians(20)
        end_angle = math.radians(160)
        self.musicians = []
        self.active_musicians = []

        for i in range(count):
            angle = start_angle + (end_angle - start_angle) * i / (count - 1)
            x = center.x + radius * math.cos(angle)
            z = center.z + radius * math.sin(angle)
            newMusician = Musician(x=x, z=z, y=center.y)
            self.musicians.append(newMusician)
            self.active_musicians.append(newMusician)
        
        self.group_id = group
        self.num_musicians = count
        
        # Musician management
        # self.target_bpm = audioManager.alltracks[track]["bpm"]
        # self.current_bpm = self.target_bpm
        
        
            
    def determineAudio(self, beat_align):
        if not self.active_musicians:
            print("group dead")
            return [0.0, 0.0]
        active_count = len(self.active_musicians)
        for musician in self.active_musicians:
            if not musician.active:
                self.active_musicians.remove(musician)
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
        # print("Offsets:", offsets, "Bad Actors:", bad_actor_count, "Active:", active_count, "Total:", total_count, "Volume:", current_volume)
        
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
        # Update all active musicians
        for musician in self.active_musicians:
            musician.update()
        
            
    def cleanup(self):
        """Clean up group resources"""
        for musician in self.musicians:
            if hasattr(musician, 'disable'):
                musician.disable()
        if hasattr(self, 'platform'):
            self.platform.disable()
        if hasattr(self, 'label'):
            self.label.disable()