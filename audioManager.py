import os
from ursina import Audio


track1 = {
    "groupA": "drumsA.wav",
    "groupB": "trumpetB.wav",
<<<<<<< Updated upstream
    "groupC": "bassC.wav"
=======
    "groupC": "bassC.wav",
    "groupD": "trumpetB.wav"
>>>>>>> Stashed changes
}
alltracks = {
    "track1": track1
}
audioFolder = "audio"

<<<<<<< Updated upstream
order = ["groupA", "groupB", "groupC"]
=======
order = ["groupA", "groupB", "groupC", "groupD"]
>>>>>>> Stashed changes

audio_cache = {}
active_tracks = {}

master_volume = 1.0  # Global master volume
"""Note: audio folder REQUIRED"""



def start():
    for i in order:
        load_audio("track1", i)

    for group in order:
        track = audio_cache.get(group)
        # track.volume = volume * master_volume
        # track.pitch = pitch
        track.play()
        active_tracks[group] = track
def pause():
    for track in list(active_tracks.values()):
        track.pause()
def resume():
    for track in list(active_tracks.values()):
        track.resume()
def stop():
    for track in list(active_tracks.values()):
        track.stop() 
def setVolume(volume):
        """Set master volume for all tracks"""
        global master_volume
        master_volume = max(0.0, min(1.0, volume))
        
        for track in list(active_tracks.keys()):
            track.volume = track.volume * master_volume
def determineAudio(audioList): # [[volume, offset], [volume, offset]]
    for i in range(3):
        change_track_speed(order[i], audioList[i][1])
        change_track_volume(order[i], audioList[i][0])



def load_audio(track, group):
    audio_file = alltracks[track][group]
    audio_path = os.path.join(audioFolder, audio_file)
    print("loading")
    audio = Audio(audio_path, loop=True, autoplay=False)
    audio_cache[group] = audio
    print(f"Loaded audio for {group} from {audio_path}")
    return audio #failsafes are for losers


def change_track_volume(group, factor = 1.0):
    active_tracks[group].volume = active_tracks[group].volume * factor
def change_track_speed(group, factor=1.0):
    active_tracks[group].pitch = active_tracks[group].pitch * factor



    
  
