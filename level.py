"""
Level class - Main game level with orchestra management and victory conditions.
"""

from ursina import *
from group import Group
from audioManager import AudioManager
from imageManager import ImageManager
import random
import statistics

class Level(Entity):
    def __init__(self, game_duration=60):
        super().__init__()
        
        # Level properties
        self.game_duration = game_duration
        self.time_remaining = game_duration
        self.level_start_time = time.time()
        
        # Game balance settings
        self.beat_align = 0.3  # How much conductor intervention helps
        self.offsetness_threshold = 5.0  # Maximum allowed offset
        self.min_musicians = 3  # Minimum musicians per group to continue
        
        # Orchestra setup
        self.concert = []
        self.offsetness = 0.0
        
        # Managers
        self.audio_manager = AudioManager()
        self.image_manager = ImageManager()
        
        # UI elements
        self.ui_elements = []
        
        # Initialize the level
        self.init_level()
        
    def init_level(self):
        """Initialize the level with stage, orchestra, and UI"""
        # Create stage
        self.setup_stage()
        
        # Create orchestra groups
        self.setup_orchestra()
        
        # Setup audio tracks
        self.setup_audio()
        
        # Setup UI
        self.setup_ui()
        
        # Start the level
        self.start_level()
        
    def setup_stage(self):
        """Create the stage environment"""
        # Main stage platform
        self.stage = Entity(
            model='cube',
            position=(0, -0.5, 0),
            scale=(15, 0.5, 10),
            color=color.brown,
            texture=self.image_manager.get_image("stage")
        )
        
        # Stage backdrop
        self.backdrop = Entity(
            model='cube',
            position=(0, 2, 5),
            scale=(20, 8, 1),
            color=color.dark_gray,
            texture=self.image_manager.get_image("background")
        )
        
    def setup_orchestra(self):
        """Create the orchestra groups in semicircle formation"""
        # Group configurations - position doesn't matter much since musicians are arranged in semicircle
        group_configs = [
            {'id': 'A', 'musicians': 6, 'instrument': 'drums'},
            {'id': 'B', 'musicians': 5, 'instrument': 'trumpet'},
            {'id': 'C', 'musicians': 4, 'instrument': 'bass'},
        ]
        
        self.concert = []
        
        for config in group_configs:
            group = Group(
                group_id=config['id'],
                num_musicians=config['musicians'],
                width=3,
                length=2,
                position=(0, 0, 0)  # All groups use same center point for semicircle calculation
            )
            self.concert.append(group)
            
    def setup_audio(self):
        """Setup audio tracks for each group"""
        for group in self.concert:
            self.audio_manager.start_track(
                group_id=group.group_id,
                volume=0.6,
                pitch=1.0
            )
            
    def setup_ui(self):
        """Setup game UI elements"""
        # Timer display
        self.timer_text = Text(
            text="",
            position=(-0.8, 0.4),
            scale=2,
            color=color.white,
            background=True
        )
        self.ui_elements.append(self.timer_text)
        
        # Offset display
        self.offset_text = Text(
            text="",
            position=(-0.8, 0.3),
            scale=1.5,
            color=color.yellow,
            background=True
        )
        self.ui_elements.append(self.offset_text)
        
        # Group status display
        self.group_status_text = Text(
            text="",
            position=(0.6, 0.4),
            scale=1.2,
            color=color.white,
            background=True,
            multiline=True
        )
        self.ui_elements.append(self.group_status_text)
        
        # Instructions
        self.instructions_text = Text(
            text="SPACE: Synchronize | Q: Remove bad musicians | Right Mouse: Look around",
            position=(0, -0.45),
            scale=1,
            color=color.light_gray,
            background=True
        )
        self.ui_elements.append(self.instructions_text)
        
    def start_level(self):
        """Start the level"""
        print(f"Level started! Duration: {self.game_duration} seconds")
        
    def update(self):
        """Main level update loop"""
        # Update timer
        self.update_timer()
        
        # Update orchestra
        self.update_orchestra()
        
        # Handle synchronization input
        self.handle_synchronization()
        
        # Update audio
        self.update_audio()
        
        # Update UI
        self.update_ui()
        
        # Check victory conditions
        self.check_victory_conditions()
        
    def update_timer(self):
        """Update game timer"""
        elapsed_time = time.time() - self.level_start_time
        self.time_remaining = max(0, self.game_duration - elapsed_time)
        
    def update_orchestra(self):
        """Update all orchestra groups"""
        group_offsets = []
        
        for group in self.concert:
            group.update()
            
            # Calculate audio settings for this group
            group_offset = group.determine_audio(self.beat_align)
            group_offsets.append(group_offset)
            
        # Calculate overall offsetness as standard deviation instead of average
        if len(group_offsets) > 1:
            self.offsetness = statistics.stdev(group_offsets)
        elif len(group_offsets) == 1:
            self.offsetness = group_offsets[0]
        else:
            self.offsetness = 0.0
        
    def handle_synchronization(self):
        """Handle space key for synchronization"""
        if held_keys['space']:
            # Apply beat alignment to reduce offsetness
            self.offsetness *= (1.0 - self.beat_align)
            
            # Visual feedback
            self.show_synchronization_effect()
            
    def show_synchronization_effect(self):
        """Show visual effect for synchronization"""
        # Create wave effect from conductor position
        for i in range(5):
            wave = Entity(
                model='circle',
                scale=0.1,
                position=(0, 0, -3),
                color=color.white33,
                billboard=True
            )
            
            # Animate wave
            wave.animate_scale((3, 3, 1), duration=1.0)
            wave.animate_color(color.clear, duration=1.0)
            destroy(wave, delay=1.0)
            
    def update_audio(self):
        """Update audio based on group performance"""
        for group in self.concert:
            # Get group performance metrics
            volume_multiplier = len(group.active_musicians) / len(group.musicians)
            offset_factor = group.audio_offset
            
            # Update audio track
            self.audio_manager.update_track_properties(
                group_id=group.group_id,
                volume_multiplier=volume_multiplier,
                pitch_multiplier=1.0,
                offset_factor=offset_factor
            )
            
    def update_ui(self):
        """Update UI elements"""
        # Timer
        minutes = int(self.time_remaining // 60)
        seconds = int(self.time_remaining % 60)
        self.timer_text.text = f"Time: {minutes:02d}:{seconds:02d}"
        
        # Offset indicator
        offset_color = color.green if self.offsetness < 2.0 else color.orange if self.offsetness < 4.0 else color.red
        self.offset_text.text = f"Sync: {self.offsetness:.1f}"
        self.offset_text.color = offset_color
        
        # Group status
        status_lines = []
        for group in self.concert:
            active = group.get_active_count()
            total = group.get_total_count()
            bad_actors = group.get_bad_actor_count()
            status_lines.append(f"Group {group.group_id}: {active}/{total} ({bad_actors} bad)")
            
        self.group_status_text.text = "\n".join(status_lines)
        
    def check_victory_conditions(self):
        """Check win/lose conditions"""
        # Check if time is up
        if self.time_remaining <= 0:
            if self.offsetness <= self.offsetness_threshold:
                self.victory()
            else:
                self.defeat("Orchestra out of sync!")
            return
            
        # Check if too many musicians removed
        total_active = sum(group.get_active_count() for group in self.concert)
        total_musicians = sum(group.get_total_count() for group in self.concert)
        
        if total_active < self.min_musicians * len(self.concert):
            self.defeat("Too many musicians removed!")
            return
            
        # Check if any group has too few musicians
        for group in self.concert:
            if group.get_active_count() < 1:
                self.defeat(f"Group {group.group_id} has no musicians left!")
                return
                
        # Check if everyone is a bad actor
        total_active = sum(group.get_active_count() for group in self.concert)
        total_bad_actors = sum(group.get_bad_actor_count() for group in self.concert)
        
        if total_active > 0 and total_bad_actors == total_active:
            self.defeat("All musicians became bad actors! Concert failed!")
            return
                
    def victory(self):
        """Handle victory condition"""
        #print("Victory! Concert was successful!")
        
        # Stop all audio
        self.audio_manager.stop_all_tracks()
        
        # Show victory message
        victory_text = Text(
            text="CONCERT SUCCESS!",
            scale=4,
            color=color.gold,
            background=True
        )
        
        # Notify main game
        if hasattr(self.parent, 'show_victory'):
            self.parent.show_victory()
            
    def defeat(self, reason):
        """Handle defeat condition"""
        print(f"Defeat! {reason}")
        
        # Stop all audio
        self.audio_manager.stop_all_tracks()
        
        # Show defeat message
        defeat_text = Text(
            text=f"CONCERT FAILED!\n{reason}",
            scale=3,
            color=color.red,
            background=True
        )
        
        # Notify main game
        if hasattr(self.parent, 'show_defeat'):
            self.parent.show_defeat()
            
    def get_orchestra_performance(self):
        """Get overall orchestra performance score"""
        if not self.concert:
            return 0.0
            
        total_performance = sum(group.get_group_performance() for group in self.concert)
        return total_performance / len(self.concert)
        
    def cleanup(self):
        """Clean up level resources"""
        # Clean up groups
        for group in self.concert:
            group.cleanup()
            
        # Clean up UI
        for ui_element in self.ui_elements:
            ui_element.disable()
            
        # Clean up stage
        if hasattr(self, 'stage'):
            self.stage.disable()
        if hasattr(self, 'backdrop'):
            self.backdrop.disable()
            
        # Clean up audio
        self.audio_manager.cleanup()
        
        # Clean up level entity
        self.disable()
