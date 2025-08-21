from flask import Flask
from routes.channels import channels_bp

app = Flask(__name__)
app.register_blueprint(channels_bp)

@app.route('/')
def home():
    return "Welcome to the Flask App!"

if __name__ == '__main__':
    app.run(debug=True)
