from flask import Flask, render_template
from routes.channels import channels_bp

app = Flask(__name__)
app.register_blueprint(channels_bp)


@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
