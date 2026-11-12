"""
Sound system for Dead Drop Society
Generates procedural sound effects using Pygame's mixer
"""

import pygame
import pygame.mixer
import random
import math
import numpy as np
from io import BytesIO

class SoundGenerator:
    """Generate procedural sound effects"""
    
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        self.sounds = {}
        self.load_sounds()
    
    def load_sounds(self):
        """Generate all sound effects"""
        self.sounds['scan_start'] = self.generate_scan_sound()
        self.sounds['scan_complete'] = self.generate_beep_sound(freq=1000, duration=0.2)
        self.sounds['extract'] = self.generate_beep_sound(freq=800, duration=0.3)
        self.sounds['upload'] = self.generate_upload_sound()
        self.sounds['alert'] = self.generate_alert_sound()
        self.sounds['decay'] = self.generate_decay_sound()
        self.sounds['rival_spawn'] = self.generate_spawn_sound()
        self.sounds['patrol_alert'] = self.generate_patrol_alert()
        self.sounds['stealth_on'] = self.generate_click_sound()
        self.sounds['stealth_off'] = self.generate_click_sound(freq=200)
        self.sounds['menu_select'] = self.generate_click_sound(freq=600)
        self.sounds['game_over'] = self.generate_game_over_sound()
        self.sounds['victory'] = self.generate_victory_sound()
    
    def generate_beep_sound(self, freq=440, duration=0.1, volume=0.5):
        """Generate a simple beep sound"""
        sample_rate = 44100
        num_samples = int(sample_rate * duration)
        
        # Generate sine wave
        t = np.linspace(0, duration, num_samples, False)
        wave = volume * np.sin(2 * np.pi * freq * t)
        
        # Apply envelope
        attack = int(0.05 * sample_rate)
        release = int(0.1 * sample_rate)
        envelope = np.ones(num_samples)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-release:] = np.linspace(1, 0, release)
        wave = wave * envelope
        
        # Convert to bytes
        wave = (wave * 32767).astype(np.int16)
        sound_buffer = pygame.sndarray.make_sound(wave)
        return sound_buffer
    
    def generate_scan_sound(self):
        """Generate scanning sound effect"""
        sample_rate = 44100
        duration = 0.5
        num_samples = int(sample_rate * duration)
        
        t = np.linspace(0, duration, num_samples, False)
        
        # Create a sweep from high to low frequency
        start_freq = 2000
        end_freq = 400
        freq = np.linspace(start_freq, end_freq, num_samples)
        wave = 0.3 * np.sin(2 * np.pi * freq * t)
        
        # Add some noise
        noise = 0.1 * np.random.uniform(-1, 1, num_samples)
        wave = wave + noise
        
        # Apply envelope
        attack = int(0.02 * sample_rate)
        release = int(0.1 * sample_rate)
        envelope = np.ones(num_samples)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-release:] = np.linspace(1, 0, release)
        wave = wave * envelope
        
        # Convert to stereo
        wave = np.column_stack((wave, wave * 0.8))
        wave = (wave * 32767).astype(np.int16)
        sound_buffer = pygame.sndarray.make_sound(wave)
        return sound_buffer
    
    def generate_upload_sound(self):
        """Generate upload completion sound"""
        sample_rate = 44100
        duration = 0.8
        num_samples = int(sample_rate * duration)
        
        t = np.linspace(0, duration, num_samples, False)
        
        # Create ascending tones
        wave = np.zeros(num_samples)
        
        # Three ascending beeps
        for i in range(3):
            start = int(i * 0.2 * sample_rate)
            end = int((i + 1) * 0.2 * sample_rate)
            segment_t = np.linspace(0, 0.2, end - start, False)
            freq = 400 + i * 200
            segment_wave = 0.4 * np.sin(2 * np.pi * freq * segment_t)
            envelope = np.linspace(0, 1, int(0.02 * sample_rate)) + \
                       np.ones(end - start - int(0.04 * sample_rate)) + \
                       np.linspace(1, 0, int(0.02 * sample_rate))
            segment_wave = segment_wave * envelope[:end - start]
            wave[start:end] = segment_wave
        
        # Add a final rising tone
        start = int(0.6 * sample_rate)
        end = num_samples
        segment_t = np.linspace(0, 0.2, end - start, False)
        freq = np.linspace(800, 1200, end - start)
        segment_wave = 0.3 * np.sin(2 * np.pi * freq * segment_t)
        envelope = np.linspace(0, 1, int(0.02 * sample_rate)) + \
                   np.ones(end - start - int(0.04 * sample_rate)) + \
                   np.linspace(1, 0, int(0.02 * sample_rate))
        segment_wave = segment_wave * envelope[:end - start]
        wave[start:end] += segment_wave
        
        # Convert to stereo
        wave = np.column_stack((wave, wave * 0.7))
        wave = (wave * 32767).astype(np.int16)
        sound_buffer = pygame.sndarray.make_sound(wave)
        return sound_buffer
    
    def generate_alert_sound(self):
        """Generate alert/beep sound"""
        sample_rate = 44100
        duration = 0.3
        num_samples = int(sample_rate * duration)
        
        t = np.linspace(0, duration, num_samples, False)
        
        # Create a pulsing alarm sound
        freq = 800
        wave = 0.5 * np.sin(2 * np.pi * freq * t)
        
        # Add amplitude modulation
        mod_freq = 20
        mod = 0.5 + 0.5 * np.sin(2 * np.pi * mod_freq * t)
        wave = wave * mod
        
        # Apply envelope
        attack = int(0.01 * sample_rate)
        release = int(0.05 * sample_rate)
        envelope = np.ones(num_samples)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-release:] = np.linspace(1, 0, release)
        wave = wave * envelope
        
        # Convert to stereo with panning
        left = wave * 0.7
        right = wave * 0.3
        wave = np.column_stack((left, right))
        wave = (wave * 32767).astype(np.int16)
        sound_buffer = pygame.sndarray.make_sound(wave)
        return sound_buffer
    
    def generate_decay_sound(self):
        """Generate decay/loss sound effect"""
        sample_rate = 44100
        duration = 0.5
        num_samples = int(sample_rate * duration)
        
        t = np.linspace(0, duration, num_samples, False)
        
        # Create a descending, glitchy sound
        freq = np.linspace(800, 100, num_samples)
        wave = 0.4 * np.sin(2 * np.pi * freq * t)
        
        # Add distortion
        wave = np.tanh(wave * 2) * 0.5
        
        # Add noise bursts
        for i in range(5):
            pos = int(random.random() * num_samples)
            length = int(0.01 * sample_rate)
            start = max(0, pos - length // 2)
            end = min(num_samples, pos + length // 2)
            noise = 0.3 * np.random.uniform(-1, 1, end - start)
            wave[start:end] = wave[start:end] + noise
        
        # Apply envelope
        attack = int(0.01 * sample_rate)
        release = int(0.1 * sample_rate)
        envelope = np.ones(num_samples)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-release:] = np.linspace(1, 0, release)
        wave = wave * envelope
        
        # Convert to stereo
        wave = np.column_stack((wave, wave * 0.8))
        wave = (wave * 32767).astype(np.int16)
        sound_buffer = pygame.sndarray.make_sound(wave)
        return sound_buffer
    
    def generate_spawn_sound(self):
        """Generate rival spawn sound"""
        sample_rate = 44100
        duration = 0.4
        num_samples = int(sample_rate * duration)
        
        t = np.linspace(0, duration, num_samples, False)
        
        # Create a rising whoosh sound
        freq = np.linspace(50, 400, num_samples)
        wave = 0.3 * np.sin(2 * np.pi * freq * t)
        
        # Add multiple harmonics
        for i in range(2, 6):
            wave += 0.15 / i * np.sin(2 * np.pi * freq * i * t)
        
        # Apply envelope
        attack = int(0.05 * sample_rate)
        release = int(0.1 * sample_rate)
        envelope = np.ones(num_samples)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-release:] = np.linspace(1, 0, release)
        wave = wave * envelope
        
        # Convert to stereo
        wave = np.column_stack((wave, wave * 0.6))
        wave = (wave * 32767).astype(np.int16)
        sound_buffer = pygame.sndarray.make_sound(wave)
        return sound_buffer
    
    def generate_patrol_alert(self):
        """Generate patrol alert sound"""
        sample_rate = 44100
        duration = 0.6
        num_samples = int(sample_rate * duration)
        
        t = np.linspace(0, duration, num_samples, False)
        
        # Create a siren-like sound
        freq1 = 400
        freq2 = 600
        wave = 0.4 * (np.sin(2 * np.pi * freq1 * t) + 0.7 * np.sin(2 * np.pi * freq2 * t))
        
        # Add modulation
        mod_freq = 5
        mod = 0.5 + 0.5 * np.sin(2 * np.pi * mod_freq * t)
        wave = wave * mod
        
        # Apply envelope
        attack = int(0.02 * sample_rate)
        release = int(0.1 * sample_rate)
        envelope = np.ones(num_samples)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-release:] = np.linspace(1, 0, release)
        wave = wave * envelope
        
        # Convert to stereo
        wave = np.column_stack((wave, wave * 0.8))
        wave = (wave * 32767).astype(np.int16)
        sound_buffer = pygame.sndarray.make_sound(wave)
        return sound_buffer
    
    def generate_click_sound(self, freq=400):
        """Generate a click/beep sound"""
        sample_rate = 44100
        duration = 0.05
        num_samples = int(sample_rate * duration)
        
        t = np.linspace(0, duration, num_samples, False)
        
        # Create a short click
        wave = 0.5 * np.sin(2 * np.pi * freq * t)
        
        # Apply sharp envelope
        attack = int(0.005 * sample_rate)
        release = int(0.01 * sample_rate)
        envelope = np.ones(num_samples)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-release:] = np.linspace(1, 0, release)
        wave = wave * envelope
        
        # Convert to stereo
        wave = np.column_stack((wave, wave * 0.7))
        wave = (wave * 32767).astype(np.int16)
        sound_buffer = pygame.sndarray.make_sound(wave)
        return sound_buffer
    
    def generate_game_over_sound(self):
        """Generate game over sound"""
        sample_rate = 44100
        duration = 1.0
        num_samples = int(sample_rate * duration)
        
        t = np.linspace(0, duration, num_samples, False)
        
        # Create a descending, dissonant sound
        wave = np.zeros(num_samples)
        
        for i in range(5):
            freq = 400 - i * 50
            segment = 0.2 * np.sin(2 * np.pi * freq * t)
            wave += segment
        
        # Add distortion
        wave = np.tanh(wave * 3) * 0.4
        
        # Apply envelope
        attack = int(0.05 * sample_rate)
        release = int(0.3 * sample_rate)
        envelope = np.ones(num_samples)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-release:] = np.linspace(1, 0, release)
        wave = wave * envelope
        
        # Convert to stereo
        wave = np.column_stack((wave, wave * 0.9))
        wave = (wave * 32767).astype(np.int16)
        sound_buffer = pygame.sndarray.make_sound(wave)
        return sound_buffer
    
    def generate_victory_sound(self):
        """Generate victory sound"""
        sample_rate = 44100
        duration = 1.2
        num_samples = int(sample_rate * duration)
        
        t = np.linspace(0, duration, num_samples, False)
        
        # Create ascending, harmonic sound
        wave = np.zeros(num_samples)
        
        for i in range(4):
            start_freq = 200 + i * 100
            end_freq = 800 + i * 200
            freq = np.linspace(start_freq, end_freq, num_samples)
            segment = 0.2 * np.sin(2 * np.pi * freq * t)
            wave += segment
        
        # Apply envelope
        attack = int(0.1 * sample_rate)
        sustain = int(0.8 * sample_rate)
        release = int(0.3 * sample_rate)
        envelope = np.ones(num_samples)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-release:] = np.linspace(1, 0, release)
        wave = wave * envelope
        
        # Convert to stereo
        wave = np.column_stack((wave, wave * 0.7))
        wave = (wave * 32767).astype(np.int16)
        sound_buffer = pygame.sndarray.make_sound(wave)
        return sound_buffer
    
    def play(self, sound_name: str, volume=1.0):
        """Play a sound"""
        if sound_name in self.sounds:
            sound = self.sounds[sound_name]
            sound.set_volume(volume)
            sound.play()
    
    def play_at_position(self, sound_name: str, position, listener_position=None):
        """Play a sound at a specific position (simple stereo panning)"""
        if sound_name not in self.sounds:
            return
        
        sound = self.sounds[sound_name]
        
        if listener_position:
            # Calculate distance and panning
            dx = position.x - listener_position.x
            distance = max(1, math.sqrt(dx*dx + (position.y - listener_position.y)**2))
            
            # Simple stereo panning (-1 = left, 1 = right)
            pan = dx / max(1, abs(dx))
            
            # Reduce volume with distance
            max_distance = 1000
            volume = max(0, 1.0 - distance / max_distance)
            
            # Set volume
            sound.set_volume(volume)
        
        sound.play()

# Singleton instance
sound_system = None

def get_sound_system():
    global sound_system
    if sound_system is None:
        sound_system = SoundGenerator()
    return sound_system

def init_sounds():
    global sound_system
    sound_system = SoundGenerator()
    return sound_system
