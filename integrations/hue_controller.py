import os
import time
import threading
from dotenv import load_dotenv
from core.app_state import app_state

load_dotenv()

HUE_BRIDGE_IP = os.getenv("HUE_BRIDGE_IP")
HUE_USERNAME = os.getenv("HUE_USERNAME")

class HueController:
    def __init__(self):
        self.connected = False
        self.bridge = None
        
        if HUE_BRIDGE_IP and HUE_USERNAME:
            try:
                from phue import Bridge
                # We initialize with IP and username to avoid having to press the button
                # if already registered.
                self.bridge = Bridge(HUE_BRIDGE_IP, username=HUE_USERNAME)
                self.connected = True
                print("💡 Connected to Philips Hue Bridge!")
            except Exception as e:
                print(f"⚠️ Failed to connect to Hue Bridge: {e}")
        else:
            print("⚠️ Hue configuration missing in .env, Smart Lighting disabled.")

        self.last_emotion = None
        self.thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.thread.start()

    def _set_color(self, hex_color):
        if not self.connected:
            return
            
        try:
            # Basic Hex to XY approximation or just setting hue/sat
            # For simplicity, let's map emotions to basic hue values
            pass
        except Exception:
            pass
            
    def _poll_loop(self):
        while app_state.is_running():
            current_emotion = app_state.current_emotion
            
            if current_emotion != self.last_emotion:
                self.last_emotion = current_emotion
                
                if self.connected:
                    try:
                        lights = self.bridge.lights
                        
                        # Emotion mapping to hue values
                        hue_val = 10000 # Default neutral
                        if current_emotion.lower() == "happy":
                            hue_val = 25500 # Green
                        elif current_emotion.lower() in ["angry", "sad"]:
                            hue_val = 0 # Red
                        
                        for light in lights:
                            light.hue = hue_val
                            light.saturation = 254
                        print(f"💡 Light changed for emotion: {current_emotion}")
                    except Exception as e:
                        pass
                
            time.sleep(1)

# Singleton
hue_controller = HueController()
