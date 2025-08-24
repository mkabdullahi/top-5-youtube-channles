from flask import Flask, render_template
from routes.channels import channels_bp
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
application = app  # WSGI entry point for PythonAnywhere
app.register_blueprint(channels_bp)


# Template reload controlled by environment variable
app.config['TEMPLATES_AUTO_RELOAD'] = os.getenv('TEMPLATES_AUTO_RELOAD', 'False').lower() in ('true', '1', 't')


@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    # Read FLASK_DEBUG from environment (.env) to control reloader/debug behavior
    flask_debug = os.getenv('FLASK_DEBUG', '1')
    try:
        debug_mode = bool(int(flask_debug))
    except Exception:
        debug_mode = str(flask_debug).lower() in ('true', '1', 'yes', 'on')

    # Explicitly control the reloader using the debug flag
    app.run(debug=debug_mode, use_reloader=debug_mode)
