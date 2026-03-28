
import asyncio
import edge_tts
import pygame
import os
import time
import logging

logger = logging.getLogger("ORMA_VOICE")

class OrmaVoice:
    def __init__(self, voice="en-US-GuyNeural", rate="+0%", volume="+0%"):
        self.voice = voice
        self.rate = rate
        self.volume = volume
        self.temp_file = "orma_speech.mp3"
        
        # Initialize pygame mixer
        if not pygame.mixer.get_init():
            pygame.mixer.init()

    async def generate_audio(self, text):
        """Generates MP3 from text using edge-tts."""
        try:
            communicate = edge_tts.Communicate(text, self.voice, rate=self.rate, volume=self.volume)
            await communicate.save(self.temp_file)
            return True
        except Exception as e:
            logger.error(f"TTS Generation Error: {e}")
            return False

    def play_audio(self):
        """Plays the generated MP3 file."""
        try:
            if os.path.exists(self.temp_file):
                pygame.mixer.music.load(self.temp_file)
                pygame.mixer.music.play()
                
                # Wait for playback to finish
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                
                pygame.mixer.music.unload()
                os.remove(self.temp_file)
        except Exception as e:
            logger.error(f"Audio Playback Error: {e}")

    async def speak(self, text):
        """One-stop shop for generating and playing speech."""
        if not text: return
        
        # Strip code blocks or common markdown artifacts for cleaner speech
        clean_text = text.replace("`", "").replace("*", "").strip()
        
        success = await self.generate_audio(clean_text)
        if success:
            # We run the blocking playback in a thread to keep the event loop alive
            # But for simple scripts, we can just block here since Orma waits anyway
            self.play_audio()
