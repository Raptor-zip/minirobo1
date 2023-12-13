let inputElem;
let currentValueElement;
let fps = 0;

var socket = io();

var ping_pong_times = [];
var start_time;
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
    console.log(29);
});

window.setInterval(function () {
    console.log(34);
    start_time = (new Date).getTime();
    socket.emit('my ping');
}, 1000);

socket.on('my pong', function () {
    var latency = (new Date).getTime() - start_time;
    ping_pong_times.push(latency);
    ping_pong_times = ping_pong_times.slice(-30); // keep last 30 samples
    var sum = 0;
    for (var i = 0; i < ping_pong_times.length; i++)
        sum += ping_pong_times[i];
    $('#ping').text(Math.round(10 * sum / ping_pong_times.length) / 10 + "ms");
});

var log = function () {
    console.log(50);
    document.getElementById("fps").innerText = "fps:" + fps;
    fps = 0;
};
setInterval(log, 1000);


// function stream_send_to_python() {
//     // console.log("送信リク");
//     $.ajax("/stream_call_from_ajax", {
//         type: "POST",
//     }).done(function (received_data) {                   // 戻ってきたのはJSON（文字列）
//         var received_dict = JSON.parse(received_data);  // JSONを連想配列にする
//         // console.log(received_dict); // JSON
//         if ("data" in received_dict) {
//             let text = "";
//             for (let i = 0; i < received_dict["data"].length; i++) {
//                 text += received_dict["data"][i];
//                 text += "<br>";
//             }
//             document.getElementById("result").innerHTML = text;
//         }
//         document.getElementById("image").src = "data:image/jpeg;base64," + received_dict["image"];
//         fps++;
//     }).fail(function () {
//         console.log("失敗");
//     });
// };


// function data_send_to_python() {
//     let send_data = document.getElementById("motor1_inputnumber").value;
//     $.ajax("/data_call_from_ajax", {
//         type: "post",
//         data: { data: send_data }, // 連想配列をPOSTする
//     })
//         .done(function (received_data) {
//             // 戻ってきたのはJSON（文字列）
//             var dict = JSON.parse(received_data); // JSONを連想配列にする
//             document.getElementById("result2").innerHTML = dict["data"];
//         })
//         .fail(function () {
//             console.log("失敗");
//             document.getElementById("result2").innerHTML = "失敗";
//         });
// }

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