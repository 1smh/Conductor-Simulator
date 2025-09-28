"""
One-Armed Band - Conductor Game
Main entry point for the game with title screen and scene management.
"""

from ursina import *
from level import Level
from player import Player

class GameState:
    TITLE = "title"
    GAME = "game"
    VICTORY = "victory"
    DEFEAT = "defeat"

class Game(Entity):
    def __init__(self):
        super().__init__()
        
        # Game state management
        self.state = GameState.TITLE
        self.level = None
        self.player = None
        
        # Title screen setup
        self.setup_title_screen()
        
        # Input handling
        self.input_enabled = True
        
    def setup_title_screen(self):
        """Create the title screen UI"""
        # Title text
        self.title_text = Text(
            "ONE-ARMED BAND",
            scale=3,
            origin=(0, 0),
            color=color.white
        )
        
        # Subtitle
        self.subtitle_text = Text(
            "Sacrifices Must Be Made",
            scale=1.5,
            origin=(0, 0),
            y=-0.5,
            color=color.light_gray
        )
        
        # Start button
        self.start_button = Button(
            text="Start Concert",
            scale=(0.3, 0.1),
            origin=(0, 0),
            y=0.4,
            color=color.green,
            highlight_color=color.lime
        )
        
        # Instructions
        self.instructions = Text(
            "SPACE: Synchronize the orchestra\nQ: Remove bad musicians\nRight Mouse: Look around\nWASD: Move conductor",
            scale=1,
            origin=(0, 0),
            y=-2,
            color=color.gray,
            multiline=True
        )
        
        # Handle button click
        self.start_button.on_click = self.start_game
        
    def start_game(self):
        """Start the main game"""
        # Hide title screen
        self.title_text.disable()
        self.subtitle_text.disable()
        self.start_button.disable()
        self.instructions.disable()
        
        # Change state
        self.state = GameState.GAME
        
        # Create level and player
        self.level = Level()
        self.player = Player()
        
        print("Game started!")
        
    def update(self):
        """Main game update loop"""
        if not self.input_enabled:
            return
            
        # Handle basic GUI interactions (but let player handle escape key)
        # Escape key handling is now managed by the player for cursor control
            
        # Handle game state specific updates
        if self.state == GameState.GAME and self.level:
            # Level handles its own update
            pass
        elif self.state in [GameState.VICTORY, GameState.DEFEAT]:
            # Handle victory/defeat screen input
            if held_keys['r']:  # Restart
                self.restart_game()
                
    def pause_game(self):
        """Pause the game"""
        if self.state == GameState.GAME:
            self.input_enabled = False
            # Could add pause menu here
            print("Game paused - Press ESC again to resume")
            
    def restart_game(self):
        """Restart the game from title screen"""
        # Clean up current game
        if self.level:
            self.level.cleanup()
            self.level = None
        if self.player:
            self.player.disable()
            self.player = None
            
        # Reset to title screen
        self.state = GameState.TITLE
        self.input_enabled = True
        self.setup_title_screen()
        
    def show_victory(self):
        """Show victory screen"""
        self.state = GameState.VICTORY
        self.input_enabled = False
        
        # Victory text
        Text(
            "CONCERT SUCCESS!",
            scale=3,
            origin=(0, 0),
            color=color.gold
        )
        
        Text(
            "Press R to restart",
            scale=1.5,
            origin=(0, 0),
            y=-1,
            color=color.white
        )
        
    def show_defeat(self):
        """Show defeat screen"""
        self.state = GameState.DEFEAT
        self.input_enabled = False
        
        # Defeat text
        Text(
            "CONCERT FAILED!",
            scale=3,
            origin=(0, 0),
            color=color.red
        )
        
        Text(
            "Press R to restart",
            scale=1.5,
            origin=(0, 0),
            y=-1,
            color=color.white
        )

def main():
    """Main entry point"""
    # Configure Panda3D settings to avoid warnings
    from panda3d.core import ConfigVariableManager, ConfigVariableString, ConfigVariableInt, ConfigVariableBool
    
    # Set proper window configuration
    # Note: win-size should be set as a single value or use separate width/height variables
    ConfigVariableBool('undecorated').setValue(False)
    
    # Force lower GLSL version for compatibility
    ConfigVariableString('gl-version').setValue('3.2')
    ConfigVariableString('glsl-version').setValue('150')
    
    # Disable icon loading to avoid missing file warning
    ConfigVariableString('window-icon').setValue('')
    
    # Suppress PNG color profile warnings
    ConfigVariableBool('png-warning-icc').setValue(False)
    
    # Initialize Ursina with proper settings
    app = Ursina(
        title="One-Armed Band", 
        fullscreen=False,  # Explicit window size
        borderless=False   # Explicit window decoration
    )
    
    # Set up camera for title screen
    camera.position = (0, 0, -10)
    
    # Create and start the game
    game = Game()
    
    # Run the application
    app.run()

if __name__ == "__main__":
    main()
