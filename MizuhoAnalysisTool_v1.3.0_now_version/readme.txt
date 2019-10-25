[Dev Libraries]

1. Python
 - [Official Site] https://www.python.org/

2. wxPython
 - GUI framework
 - [Official Site] https://wxpython.org/
 - [Download(cmd)]
 -- pip install -U wxPython
 - [API Doc] https://wxpython.org/Phoenix/docs/html/index.html

3. wxmplot
 - Advanced widgets of charts for wxPython
 - [Official Site] https://newville.github.io/wxmplot/
 - [Download(cmd)]
 -- pip install wxmplot

4. NumPy
 - Math-related lib used in wxmplot
 - [Official Site] http://www.numpy.org/
 - [Download(cmd)]
 -- pip install numpy

5. matplotlib
 - Base of wxmplot
 - [Official Size] https://matplotlib.org/index.html
 - [Download(cmd)]
 -- pip install -U matplotlib

6. pandas
 - [Download(cmd)]
 -- pip install pandas

 7. OpenCV
 - [Download(cmd)]
 -- pip install opencv-python



 [Package Libraries]

1. pyinstaller
 - Build project and output an executable.
 - [Download(cmd)]
 -- pip install pyinstaller
 - [Build(cmd)]
 -- Choose one of the following: 
--- pyinstaller -c --icon "icon/launcher.ico" --add-data "icon;icon" --add-data "csv;csv" --add-data "samples;samples" --add-data "src/layout;src/layout" main.py -n "Mizuho Analysis Tool"
--- pyinstaller -w --icon "icon/launcher.ico" --add-data "icon;icon" --add-data "csv;csv" --add-data "samples;samples" --add-data "src/layout;src/layout" main.py -n "Mizuho Analysis Tool_20191018_ver1.2.0"
 --- pyinstaller -w --icon "icon/launcher.ico" --onefile main.py -n "Mizuho Analysis Tool"
 -- Cmd params: 
 --- -w -> (windows & mac) no cmd window at runtime
 --- --icon -> (windows & mac) set display icon of this program
 --- --add-data -> copy non-Python files
 --- -n -> rename executable
 --- --onefile -> build all into one executable, but launch 5~6 secconds slower, and need to copy some folders manually
 ---- csv (folder for exporting)
 ---- src/layout (xrc file)
 ---- samples (initial folder for storing sample images)
 -- [Unofficial Tutorial]
 --- https://itw01.com/F9XN4E4.html
 --- https://itw01.com/F9XNDEM.html
 --- https://itw01.com/FLHZ9EA.html
