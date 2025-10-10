import os
import time
from ursina import Audio


track1 = {
    "groupA": "drumsA.wav",
    "groupB": "trumpetB.wav",
    "groupC": "bassC.wav",
    "groupD": "trumpetB.wav"
}
alltracks = {
    "track1": track1
}
audioFolder = "audio"

order = ["groupA", "groupB", "groupC", "groupD"]

audio_cache = {}
active_tracks = {}

master_volume = 1.0  # Global master volume
"""Note: audio folder REQUIRED"""

# How long a beat is, in seconds. Can be changed by the game if needed.
beat_duration = 1.0

# pitch transition map: group -> {start_time, duration, start_pitch, target_pitch}
pitch_transitions = {}

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
            # scale each track's volume relative to master
            active_tracks[track].volume = active_tracks[track].volume * master_volume
def determineAudio(audioList):
    """Apply desired volume and pitch per-group.

    audioList is expected to be an array of [volume, offset] per group.
    We interpret offset as a desired pitch (0.0 - 1.0). If a pitch drop
    occurs (new pitch < 1.0), we schedule a catch-up transition that will
    bring the track back into sync within 2 beats.
    """
    for i in range(len(order)):
        group_key = order[i]
        vol, desired_pitch = audioList[i][0], audioList[i][1]

        # clamp
        try:
            desired_pitch = float(desired_pitch)
        except Exception:
            desired_pitch = 1.0
        desired_pitch = max(0.0, min(2.0, desired_pitch))

        # set the requested volume (relative)
        change_track_volume(group_key, vol)

        # set the immediate pitch to the desired value
        change_track_speed(group_key, desired_pitch)

        # if the pitch dropped below normal, schedule a timed catch-up so
        # the track will be able to re-align to normal speed/time within 2 beats
        if desired_pitch < 1.0:
            schedule_catchup(group_key, from_pitch=desired_pitch)

        print("group", group_key, "requested_pitch", desired_pitch, "current_pitch", active_tracks[group_key].pitch)

    

def load_audio(track, group):
    audio_file = alltracks[track][group]
    audio_path = os.path.join(audioFolder, audio_file)
    print("loading")
    audio = Audio(audio_path, loop=True, autoplay=False)
    # initialize sensible defaults
    audio.pitch = 1.0
    audio.volume = 1.0
    audio_cache[group] = audio
    print(f"Loaded audio for {group} from {audio_path}")
    return audio #failsafes are for losers


def change_track_volume(group, factor = 1.0):
    """Set track volume as a multiplier (0..1). Keeps existing volume as base.
    If factor is a relative (0..1), set volume = base * factor. If factor >1, allow it.
    """
    if group not in active_tracks:
        return
    try:
        active_tracks[group].volume = float(factor)
    except Exception:
        pass


def change_track_speed(group, factor=1.0):
    """Set absolute pitch for a track. This replaces the old multiplicative
    behaviour and makes pitch transitions deterministic.
    """
    if group not in active_tracks:
        return
    try:
        active_tracks[group].pitch = float(factor)
    except Exception:
        pass


def schedule_catchup(group, from_pitch=None, beats=2):
    """When a track's pitch drops, schedule a transition that will bring it
    back into sync (pitch=1.0) within `beats` beats. We create a brief
    overshoot above 1.0 so the track can catch up in time as well as speed.
    """
    if group not in active_tracks:
        return
    if from_pitch is None:
        from_pitch = getattr(active_tracks[group], 'pitch', 1.0)

    from_pitch = float(from_pitch)
    duration = beats * beat_duration

    # compute a target pitch that overshoots normal speed proportional to the deficit
    deficit = max(0.0, 1.0 - from_pitch)
    overshoot = 1.0 + deficit * 2.0
    target_pitch = max(1.02, overshoot)

    pitch_transitions[group] = {
        'start_time': time.time(),
        'duration': duration,
        'start_pitch': from_pitch,
        'target_pitch': target_pitch
    }


def update(dt=0.0):
    """Call this every frame with delta time. Progresses any scheduled pitch
    transitions and cleans up finished transitions."""
    now = time.time()
    to_remove = []
    for group, info in pitch_transitions.items():
        if group not in active_tracks:
            to_remove.append(group)
            continue
        elapsed = now - info['start_time']
        t = min(1.0, elapsed / max(1e-6, info['duration']))
        # linear interpolation from start_pitch -> target_pitch
        new_pitch = info['start_pitch'] + (info['target_pitch'] - info['start_pitch']) * t
        active_tracks[group].pitch = new_pitch

        # when transition completes, ensure we settle at normal pitch=1.0
        if t >= 1.0:
            # gently return to normal 1.0 if overshot
            active_tracks[group].pitch = 1.0
            to_remove.append(group)

    for g in to_remove:
        pitch_transitions.pop(g, None)


def set_beat_duration(seconds_per_beat: float):
    """Set the beat duration in seconds (used to compute transition durations)."""
    global beat_duration
    try:
        beat_duration = float(seconds_per_beat)
    except Exception:
        pass



    
  
