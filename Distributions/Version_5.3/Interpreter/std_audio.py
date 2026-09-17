# std_audio.py
# Corvus Retro Audio Synthesizer Engine
# Synthesizes sound frequencies, square waves, and retro chiptune notes.

import sys
import time
from typing import List, Union, Any

NOTE_FREQS = {
    "C3": 131, "D3": 147, "E3": 165, "F3": 175, "G3": 196, "A3": 220, "B3": 247,
    "C4": 261, "D4": 294, "E4": 329, "F4": 349, "G4": 392, "A4": 440, "B4": 494,
    "C5": 523, "D5": 587, "E5": 659, "F5": 698, "G5": 784, "A5": 880, "B5": 988,
    "C6": 1047
}

def beep(freq: Union[int, float, str] = 440, duration_ms: int = 200) -> bool:
    """Produce an audio beep at specified frequency (Hz) and duration (ms)."""
    if isinstance(freq, str):
        freq = NOTE_FREQS.get(freq.upper(), 440)
    
    freq_int = int(max(37, min(32767, freq)))
    dur_int = int(max(10, duration_ms))

    if sys.platform.startswith("win"):
        try:
            import winsound
            winsound.Beep(freq_int, dur_int)
            return True
        except Exception:
            pass
    
    time.sleep(dur_int / 1000.0)
    return True

def play_tune(notes: List[Any]) -> bool:
    """Play a list of [frequency_or_note, duration_ms] pairs."""
    for item in notes:
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            beep(item[0], item[1])
        elif isinstance(item, (int, float, str)):
            beep(item, 200)
    return True

class AudioEngine:
    @staticmethod
    def beep(freq=440, duration_ms=200):
        return beep(freq, duration_ms)

    @staticmethod
    def play_tune(notes):
        return play_tune(notes)

_global_audio_engine = AudioEngine()
