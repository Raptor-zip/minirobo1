let inputElem;
let currentValueElement;
let fps = 0;

var socket = io();

var ping_pong_times = [];
var start_time;

let json_received = {};
namespace = '/test';

// 接続者数の更新
socket.on('count_update', function (msg) {
    console.log(9);
    $('#user_count').html(msg.user_count);
});

// テキストエリアの更新
socket.on('text_update', function (msg) {
    console.log(14);
    $('#text').val(msg.text);
});

socket.on('connect', function () {
    console.log(31);
    socket.emit('my event', { data: 'I\'m connected!' });
});

socket.on('json', function () {
});

window.setInterval(function () {
    start_time = (new Date).getTime();
    socket.emit('json_request');
}, 16);

socket.on('json_receive', function (json) {
    console.log(json);
    // text = {
    //     "state": self.state,
    //     "ubuntu_ssid": wifi_ssid,
    //     "ubuntu_ip": ipget.ipget().ipaddr("wlp2s0"),
    //     "esp32_ip": esp32_ip,
    //     "battery_voltage": reception_json["battery_voltage"],
    //     "wifi_signal_strength": reception_json["wifi_signal_strength"],
    //     "motor1_speed": self.motor1_speed,
    //     "motor2_speed": self.motor2_speed,
    //     "motor3_speed": self.motor3_speed,
    //     "distance": reception_json["raw_distance"] + self.distance_adjust,
    //     "angle": a,
    //     "raw_angle": 0,
    //     "start_time": self.start_time
    // }
    if ("state" in json) {
        // console.log("あた");
    }
    if ("ubuntu_ssid" in json) {
        document.getElementById("ubuntu_ssid_value").innerText = json["ubuntu_ssid"];
    }
    if ("ubuntu_ip" in json) {
        document.getElementById("ubuntu_id_value").innerText = json["ubuntu_id"];
    }
    if ("esp32_ip" in json) {
        document.getElementById("esp32_id_value").innerText = json["esp32_id"];
    }
    if ("battery_voltage" in json) {
        document.getElementById("battery_voltage_value").innerText = json["battery_voltage"];
    }
    if ("wifi_signal_strength" in json) {
        document.getElementById("wifi_signal_strength_value").innerText = json["wifi_signal_strength"];
    }
    if ("motor1_speed" in json) {
        document.getElementById("motor1_speed_value").innerText = json["motor1_speed"];
        document.getElementById("motor1_speed_range").value = json["motor1_speed"];
    }
    if ("motor2_speed" in json) {
        document.getElementById("motor2_speed_value").innerText = json["motor2_speed"];
        document.getElementById("motor2_speed_range").value = json["motor2_speed"];
    }
    if ("motor3_speed" in json) {
        document.getElementById("motor3_speed_value").innerText = json["motor3_speed"];
        document.getElementById("motor3_speed_range").value = json["motor3_speed"];
    }
    if ("distance_value" in json) {
        document.getElementById("distance_value").innerText = json["distance"];
    }
    if ("angle_value" in json) {
        document.getElementById("angle_value").innerText = json["angle"];
    }


    // if ()
    // console.log(json_received);
});

window.setInterval(function () {
    start_time = (new Date).getTime();
    socket.emit('my ping');
}, 1000);

socket.on('my pong', function () {
    var latency = (new Date).getTime() - start_time;
    ping_pong_times.push(latency);
    ping_pong_times = ping_pong_times.slice(-10); // keep last 30 samples
    var sum = 0;
    for (var i = 0; i < ping_pong_times.length; i++)
        sum += ping_pong_times[i];
    $('#ping').text(Math.round(10 * sum / ping_pong_times.length) / 10 + "ms");
});

var log = function () {
    document.getElementById("fps").innerText = "fps:" + fps;
    fps = 0;
};
setInterval(log, 1000);

// 現在の値を埋め込む関数
const setCurrentValue = (val) => {
    console.log(val);
    if (document.getElementById("motor1_checkbox").checked) {
        currentValueElem.value = val;
        data_send_to_python();
    }
}

// inputイベント時に値をセットする関数
const rangeOnChange = (e) => {
    setCurrentValue(e.target.value);
}


function reset() {

}