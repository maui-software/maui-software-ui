
import sys
import os

# Para PyInstaller: configurar caminho correto
if getattr(sys, 'frozen', False):
    ac_dir = os.path.join(sys._MEIPASS, 'acoustic_indices')
    if ac_dir not in sys.path:
        sys.path.insert(0, ac_dir)

# Imports explícitos dos módulos
try:
    from . import acoustic_indices_calculation
except ImportError:
    import acoustic_indices_calculation


# Disponibilizar no namespace
__all__ = ['acoustic_indices_calculation']
