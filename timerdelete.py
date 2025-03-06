from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def timer():
    if request.method == 'POST':
        timer_length = int(request.form['timer_length'])
        return render_template('timerdelete.html', time=timer_length)
    return render_template('inputdelete.html')
if __name__ == '__main__':
    app.run(debug=True, port=8080)
