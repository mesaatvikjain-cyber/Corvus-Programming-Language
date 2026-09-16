import sys

# Corvus System Audio & Sound Synth Engine (v4.2)

class AudioEngine:
    @staticmethod
    def beep(freq=440, duration_ms=200):
        if sys.platform.startswith("win"):
            try:
                import winsound
                winsound.Beep(int(freq), int(duration_ms))
            except Exception:
                print('\a', end='', flush=True)
        else:
            print('\a', end='', flush=True)

_global_audio_engine = AudioEngine()
