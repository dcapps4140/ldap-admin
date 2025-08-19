
# Flask-Limiter patch for testing
from unittest.mock import patch
import sys
import importlib

# Try to import Flask-Limiter
try:
    import flask_limiter
    
    # Save original Limiter class
    original_limiter = flask_limiter.Limiter
    
    # Create a patched Limiter class
    class PatchedLimiter(original_limiter):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.enabled = False
        
        def limit(self, *args, **kwargs):
            # Return a no-op decorator when disabled
            if not self.enabled:
                return lambda f: f
            return super().limit(*args, **kwargs)
    
    # Replace the original Limiter with our patched version
    flask_limiter.Limiter = PatchedLimiter
    
    # Reload any modules that might have imported the original
    for module_name in list(sys.modules.keys()):
        if module_name.startswith('flask_limiter'):
            importlib.reload(sys.modules[module_name])
    
    print("Flask-Limiter patched for testing")
except ImportError:
    print("Flask-Limiter not found, no patching needed")
