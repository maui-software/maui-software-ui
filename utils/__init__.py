# utils/__init__.py
"""
utils package - Imports para PyInstaller
"""

import sys
import os

# Para PyInstaller: configurar caminho correto
if getattr(sys, 'frozen', False):
    utils_dir = os.path.join(sys._MEIPASS, 'utils')
    if utils_dir not in sys.path:
        sys.path.insert(0, utils_dir)

# Imports explícitos dos módulos
try:
    from . import io_utils
except ImportError:
    import io_utils

try:
    from . import definitions
except ImportError:
    import definitions

try:
    from . import random_utils
except ImportError:
    import random_utils

# Disponibilizar no namespace
__all__ = ['io_utils', 'definitions', 'random_utils']
