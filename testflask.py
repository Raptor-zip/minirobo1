from flask import Flask, render_template
app = Flask(__name__)

cert_path = '/cert.pem'
key_path = '/key.pem'


@app.route('/')
def hello():
    html = render_template('index.html')
    return html

@app.route("/stream_call_from_ajax", methods = ["POST"])
def streamcallfromajax():
    global serial_reception_text
    global img_str

    if request.method == "POST":
        # ここにPythonの処理を書く
        try:
            message = serial_reception_text
            # message = "aiueo"
        except Exception as e:
            message = str(e)
        dict = {
            # "data": message,
            "image": img_str
                }

        serialCommand = f"{{'motor1':{{'speed':{global_value}}}}}+\n"
        ser.write(serialCommand.encode())

    return json.dumps(dict)             # 辞書をJSONにして返す]

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True,ssl_context=(cert_path, key_path))