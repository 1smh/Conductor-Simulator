# One-Armed Band

A conductor game where you synchronize musicians in an orchestra. Made for a 2-day game jam with the theme "Sacrifices Must Be Made."

## Game Concept

You play as a conductor trying to keep an orchestra synchronized. Different groups of musicians play different instruments, and some randomly become "bad actors" who disrupt the performance. You must:

- **Space**: Synchronize the orchestra to keep everyone in time
- **Q**: Remove bad musicians who are disrupting the performance
- **Arrow Keys/WASD**: Move the conductor for better positioning

## Installation

1. Install Python 3.7 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Game

```bash
python main.py
```

## Game Controls

- **Space**: Synchronize the orchestra (reduces sync offset)
- **Q**: Remove bad musicians (click on red pulsing musicians)
- **Arrow Keys/WASD**: Move conductor (limited range)
- **Escape**: Pause game
- **R**: Restart from victory/defeat screen

## Gameplay

- The game lasts 60 seconds
- Keep the orchestra synchronized (sync level below 5.0)
- Remove bad actors but don't remove too many musicians
- Each group needs at least 1 musician to continue
- Win by maintaining sync until time runs out

## Asset Requirements

### Images (Optional)
Place in `images/` directory:
- `conductor.png` - Conductor character
- `stage.png` - Stage texture
- `background.png` - Background image
- `musician_A.png`, `musician_B.png`, `musician_C.png` - Musician images

### Audio (Optional)
Place in `audios/` directory:
- `drums.mp3` - Drum track
- `trumpet.mp3` - Trumpet track
- `bass.mp3` - Bass track

The game will run with fallback graphics (colored cubes) and silent audio if assets are missing.

## Technical Details

- Built with Ursina Engine (Python 3D game framework)
- Uses pygame for audio management
- Modular design with separate classes for each game component
- Extensible architecture for future modifications

## File Structure

```
One-Armed-Band/
├── main.py              # Entry point and title screen
├── level.py             # Main game level logic
├── musician.py          # Individual musician entities
├── group.py             # Musician group management
├── player.py            # Conductor character and controls
├── imageManager.py      # Image asset management
├── audioManager.py      # Audio track management
├── requirements.txt     # Python dependencies
├── plan.txt            # Updated implementation plan
├── plan_original.txt   # Original game plan
├── images/             # Image assets directory
└── audios/             # Audio assets directory
```

## Development

The game is designed for easy modification:
- Add new instrument groups in `level.py`
- Modify musician behavior in `musician.py`
- Adjust game balance in `level.py` constants
- Add new audio tracks in `audios/` directory
- Customize visuals with images in `images/` directory
