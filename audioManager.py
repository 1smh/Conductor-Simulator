"""
AudioManager - Manages audio tracks for different instrument groups.
"""

import os
import pygame
from ursina import Audio
import random

class AudioManager:
    def __init__(self, audios_folder="audios"):
        self.audios_folder = audios_folder
        self.audio_cache = {}
        self.active_tracks = {}
        
        # Initialize pygame mixer for audio control
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Create audios directory if it doesn't exist
        if not os.path.exists(self.audios_folder):
            os.makedirs(self.audios_folder)
            # print(f"Created audios directory: {self.audios_folder}")
            
        # Default audio settings
        self.base_bpm = 120.0
        self.master_volume = 0.7
        
        # Audio track configurations for the 3 groups
        self.track_configs = {
            'A': {'volume': 0.8, 'pitch_range': (0.8, 1.2), 'file': 'drums_A.mp3'},
            'B': {'volume': 0.6, 'pitch_range': (0.9, 1.1), 'file': 'trumpet_B.mp3'},
            'C': {'volume': 0.7, 'pitch_range': (0.85, 1.15), 'file': 'bass_C.mp3'}
        }
        
    def load_audio(self, group_id):
        """Load the specific music file for a group"""
        if group_id not in self.track_configs:
            # print(f"Invalid group ID: {group_id}")
            return self.create_silent_audio()
            
        audio_file = self.track_configs[group_id]['file']
        audio_path = os.path.join(self.audios_folder, audio_file)
        
        if os.path.exists(audio_path):
            try:
                # Use Ursina's Audio class
                audio = Audio(audio_path, loop=True, autoplay=False)
                self.audio_cache[group_id] = audio
                return audio
            except Exception as e:
                print(f"Failed to load audio {audio_path}: {e}")

        # Create silent audio as fallback
        #print(f"No audio file found for group {group_id} ({audio_file}), using silent fallback")
        return self.create_silent_audio()
    
    def create_silent_audio(self):
        """Create a silent audio track as fallback"""
        # Return a dummy audio object that does nothing
        class SilentAudio:
            def __init__(self):
                self.volume = 0
                self.pitch = 1.0
                self.playing = False
                
            def play(self):
                self.playing = True
                
            def stop(self):
                self.playing = False
                
            def pause(self):
                self.playing = False
                
            def resume(self):
                self.playing = True
                
        return SilentAudio()
    
    def get_track_for_group(self, group_id):
        """Get the audio track for a specific group"""
        if group_id in self.audio_cache:
            return self.audio_cache[group_id]
            
        # Load the specific music file for this group
        audio = self.load_audio(group_id)
        return audio
    
    def start_track(self, group_id, volume=1.0, pitch=1.0):
        """Start playing an audio track for a group"""
        track = self.get_track_for_group(group_id)
        
        # Set audio properties
        track.volume = volume * self.master_volume
        track.pitch = pitch
        
        # Start playing
        track.play()
        
        # Store active track info
        self.active_tracks[group_id] = {
            'track': track,
            'base_volume': volume,
            'base_pitch': pitch
        }
        
    def stop_track(self, group_id):
        """Stop playing an audio track for a group"""
        if group_id in self.active_tracks:
            self.active_tracks[group_id]['track'].stop()
            del self.active_tracks[group_id]
            
    def pause_track(self, group_id):
        """Pause an audio track"""
        if group_id in self.active_tracks:
            self.active_tracks[group_id]['track'].pause()
            
    def resume_track(self, group_id):
        """Resume a paused audio track"""
        if group_id in self.active_tracks:
            self.active_tracks[group_id]['track'].resume()
            
    def update_track_properties(self, group_id, volume_multiplier=1.0, pitch_multiplier=1.0, 
                               offset_factor=0.0):
        """Update track properties based on group performance"""
        if group_id not in self.active_tracks:
            return
            
        track_info = self.active_tracks[group_id]
        track = track_info['track']
        
        # Apply volume changes
        base_volume = track_info['base_volume']
        track.volume = (base_volume * volume_multiplier * self.master_volume)
        
        # Apply pitch/tempo changes based on offset
        base_pitch = track_info['base_pitch']
        pitch_variation = offset_factor * 0.2  # Scale offset to pitch variation
        track.pitch = base_pitch + pitch_variation
        
    def slow_down_track(self, group_id, factor=0.9):
        """Slow down a track (reduce pitch)"""
        if group_id in self.active_tracks:
            current_pitch = self.active_tracks[group_id]['base_pitch']
            new_pitch = max(0.5, current_pitch * factor)
            self.active_tracks[group_id]['track'].pitch = new_pitch
            self.active_tracks[group_id]['base_pitch'] = new_pitch
            
    def speed_up_track(self, group_id, factor=1.1):
        """Speed up a track (increase pitch)"""
        if group_id in self.active_tracks:
            current_pitch = self.active_tracks[group_id]['base_pitch']
            new_pitch = min(2.0, current_pitch * factor)
            self.active_tracks[group_id]['track'].pitch = new_pitch
            self.active_tracks[group_id]['base_pitch'] = new_pitch
            
    def set_master_volume(self, volume):
        """Set master volume for all tracks"""
        self.master_volume = max(0.0, min(1.0, volume))
        
        # Update all active tracks
        for group_id, track_info in self.active_tracks.items():
            track = track_info['track']
            track.volume = track_info['base_volume'] * self.master_volume
            
    def stop_all_tracks(self):
        """Stop all active tracks"""
        for group_id in list(self.active_tracks.keys()):
            self.stop_track(group_id)
            
    def pause_all_tracks(self):
        """Pause all active tracks"""
        for track_info in self.active_tracks.values():
            track_info['track'].pause()
            
    def resume_all_tracks(self):
        """Resume all active tracks"""
        for track_info in self.active_tracks.values():
            track_info['track'].resume()
            
    def get_active_track_count(self):
        """Get number of currently active tracks"""
        return len(self.active_tracks)
        
    def list_available_audio(self):
        """List all available audio files"""
        if not os.path.exists(self.audios_folder):
            return []
            
        audio_files = []
        for file in os.listdir(self.audios_folder):
            if file.lower().endswith(('.mp3', '.wav', '.ogg', '.m4a')):
                audio_files.append(file)
                
        return audio_files
        
    def cleanup(self):
        """Clean up audio resources"""
        self.stop_all_tracks()
        pygame.mixer.quit()
        
