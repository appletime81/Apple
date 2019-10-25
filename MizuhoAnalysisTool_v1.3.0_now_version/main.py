from wx import App
from src.python.main.tabs import TabbedFrame
import sklearn.utils._cython_blas
import importlib_metadata

if __name__ == '__main__':
    app = App(False)
    frame = TabbedFrame()
    app.MainLoop()