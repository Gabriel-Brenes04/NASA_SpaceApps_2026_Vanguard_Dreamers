import numpy as np
import pygame
from ..settings import SAMPLE_RATE, MASTER_VOLUME

class SoundManager:
    def __init__(self):
        # --- VARIABLES DE ENTRADA ---
        self.sample_rate = SAMPLE_RATE
        self.volume = MASTER_VOLUME

        # --- VARIABLES DE SALIDA (Banco de sonidos sintetizados) ---
        self.sounds = {}
        self.saa_alarm_played = False

        # --- LÓGICA DE SÍNTESIS ---
        self._build_sound_bank()

    def _array_to_sound(self, wave_mono):
        """Convierte un arreglo float32 (-1.0 a 1.0) en un objeto pygame.mixer.Sound estéreo."""
        # Aplicar envolvente suave al inicio y final para evitar clics de audio
        fade_len = min(200, len(wave_mono) // 4)
        if fade_len > 0:
            wave_mono[:fade_len] *= np.linspace(0.0, 1.0, fade_len, dtype=np.float32)
            wave_mono[-fade_len:] *= np.linspace(1.0, 0.0, fade_len, dtype=np.float32)

        # Escalar a 16-bit signed integer y duplicar canal para estéreo
        audio_int16 = np.int16(np.clip(wave_mono * self.volume, -1.0, 1.0) * 32767)
        stereo = np.column_stack((audio_int16, audio_int16))
        return pygame.sndarray.make_sound(stereo)

    def _synth_sweep(self, f_start, f_end, duration, wave_type="sine"):
        """Genera un barrido de frecuencia (chirp)."""
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False, dtype=np.float32)
        freqs = np.linspace(f_start, f_end, len(t), dtype=np.float32)
        phase = 2.0 * np.pi * np.cumsum(freqs) / self.sample_rate

        if wave_type == "square":
            wave = np.sign(np.sin(phase))
        else:
            wave = np.sin(phase)

        decay = np.exp(-3.5 * t / duration)
        return self._array_to_sound(wave * decay)

    def _synth_explosion(self, duration=0.35):
        """Genera una explosión grave mezclando ruido blanco filtrado y onda sub-grave."""
        n_samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, n_samples, endpoint=False, dtype=np.float32)

        # Ruido blanco suavizado (filtro paso bajo simple)
        noise = np.random.uniform(-1.0, 1.0, n_samples).astype(np.float32)
        kernel = np.ones(12, dtype=np.float32) / 12.0
        filtered_noise = np.convolve(noise, kernel, mode="same")

        # Golpe sub-grave descendente (140 Hz -> 35 Hz)
        freqs = np.linspace(140, 35, n_samples, dtype=np.float32)
        sub_bass = np.sin(2.0 * np.pi * np.cumsum(freqs) / self.sample_rate)

        envelope = np.exp(-5.0 * t / duration)
        combined = (filtered_noise * 0.65 + sub_bass * 0.55) * envelope
        return self._array_to_sound(combined)

    def _synth_altea_chime(self):
        """Genera un arpegio rápido de 3 notas ascendentes para iones pesados."""
        notes = [523.25, 659.25, 1046.50]  # Do5, Mi5, Do6
        part_dur = 0.065
        segments = []
        for f in notes:
            t = np.linspace(0, part_dur, int(self.sample_rate * part_dur), endpoint=False, dtype=np.float32)
            w = np.sin(2.0 * np.pi * f * t) * np.exp(-3.0 * t / part_dur)
            segments.append(w)
        return self._array_to_sound(np.concatenate(segments))

    def _synth_melody(self, notes, note_dur=0.09, wave_type="square"):
        """Genera una secuencia de notas (para victoria o derrota)."""
        segments = []
        for f in notes:
            t = np.linspace(0, note_dur, int(self.sample_rate * note_dur), endpoint=False, dtype=np.float32)
            phase = 2.0 * np.pi * f * t
            w = np.sign(np.sin(phase)) if wave_type == "square" else np.sin(phase)
            segments.append(w * np.exp(-2.5 * t / note_dur))
        return self._array_to_sound(np.concatenate(segments))

    def _synth_geiger(self):
        """Pulso ultra corto estilo contador Geiger (0.015s)."""
        n = int(self.sample_rate * 0.015)
        pulse = np.random.uniform(-1.0, 1.0, n).astype(np.float32)
        pulse *= np.exp(-8.0 * np.linspace(0, 1, n, dtype=np.float32))
        return self._array_to_sound(pulse * 0.6)

    def _build_sound_bank(self):
        self.sounds["liulin"] = self._synth_sweep(650, 1450, 0.14, wave_type="sine")
        self.sounds["timepix"] = self._synth_sweep(900, 420, 0.16, wave_type="square")
        self.sounds["altea"] = self._synth_altea_chime()
        self.sounds["switch"] = self._synth_sweep(300, 520, 0.06, wave_type="square")
        self.sounds["hit"] = self._synth_explosion(0.35)
        self.sounds["saa_alarm"] = self._synth_sweep(440, 880, 0.45, wave_type="square")
        self.sounds["victory"] = self._synth_melody([523.25, 659.25, 783.99], wave_type="square")  # Do5, Mi5, Sol5
        self.sounds["defeat"] = self._synth_melody([261.63, 329.63, 392.00], wave_type="square")   # Do4, Mi4, Sol4
        self.sounds["geiger_tick"] = self._synth_geiger()
        self.sounds["miss_click"] = self._synth_sweep(190, 110, 0.07, wave_type="sine")
        self.sounds["ui_page"] = self._synth_sweep(700, 920, 0.05, wave_type="sine")
        self.sounds["danger_beep"] = self._synth_sweep(1150, 1150, 0.08, wave_type="square")
        self.sounds["game_over"] = self._synth_melody([392.00, 349.23, 311.13, 261.63], note_dur=0.18)
    def play(self, sound_name):
        # --- SALIDA DE AUDIO ---
        if sound_name in self.sounds:
            self.sounds[sound_name].play()

    def reset(self):
        self.saa_alarm_played = False