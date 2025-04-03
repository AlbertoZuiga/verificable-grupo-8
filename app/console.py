import os
import subprocess

# Establece la variable FLASK_APP
os.environ["FLASK_APP"] = "your_app.py"  # Cambia 'your_app.py' por tu aplicación

# Abre la consola de Flask
subprocess.call("flask shell", shell=True)
