// Fetch Service Status from PI API
// fetch('/api/services')
//   .then((response) => response.json())
//   .then((data) => web(data))

function web(data) {
    //console.log(data.info);

    // document.getElementById('f1store').innerHTML = 'Store: ' + data.f1store.store + "<br> Forward: " + data.f1store.forward + "<br> using " + data.f1store.db + "<br/>";
    f1store_runtime = 'Store: <span class="txt-gry">' + data.f1store.store + "</span><br/>";
    f1store_runtime = f1store_runtime + 'Forward: <span class="txt-gry">' + data.f1store.forward + '</span> using <span class="txt-gry">' + data.f1store.db + '</span><br/>';
    f1store_runtime = f1store_runtime + 'RMQ Messages<br/>';
    for (let index in data.f1rmqlq) {
      f1store_runtime = f1store_runtime + data.f1rmqlq[index]["name"] + ': <span class="txt-gry">' + data.f1rmqlq[index]["count"] + ' messages</span><br/>';
    }
    document.getElementById('f1store').innerHTML = f1store_runtime;

    if (!data.f1prod.status) {
        content = "F1 Producer not Running<br/>";
    } else {
        content = data.f1prod.service + ": " + data.f1prod.status + "<br/>" + data.f1prod.since + "<br/>";
    }
    content = content + "<textarea style='resize:none; display: block; font-family: monospace; white-space: pre; margin: 1em 0;' readonly='true' rows='10' cols='128'>" + data.f1prod.output + "</textarea>";
    document.getElementById('producer').innerHTML = content;

    if (!data.f1cons.status) {
        content = "F1 Consumer not Running<br/>";
    } else {
        content = data.f1cons.service + ": " + data.f1cons.status + "<br/>" + data.f1cons.since + "<br/>";
    }
    content = content + "<textarea style='resize:none; display: block; font-family: monospace; white-space: pre; margin: 1em 0;' readonly='true' rows='10' cols='128'>" + data.f1cons.output + "</textarea>";
    document.getElementById('consumer').innerHTML = content;

    if (!data.f1rmqs.status) {
        content = "F1 RabbitMQ not Running<br/>";
    } else {
        content = data.f1rmqs.service + ": " + data.f1rmqs.status + "<br/>" + data.f1rmqs.since + "<br/>";
    }
    content = content + "<textarea style='resize:none; display: block; font-family: monospace; white-space: pre; margin: 1em 0;' readonly='true' rows='10' cols='128'>" + data.f1rmqs.output + "</textarea>";
    document.getElementById('rabbitmq').innerHTML = content;

    if (!data.f1webs.status) {
        content = "F1 WebServer not Running<br/>";
    } else {
        content = data.f1webs.service + ": " + data.f1webs.status + "<br/>" + data.f1webs.since + "<br/>";
    }
    content = content + "<textarea style='resize:none; display: block; font-family: monospace; white-space: pre; margin: 1em 0;' readonly='true' rows='10' cols='128'>" + data.f1webs.output + "</textarea>";
    document.getElementById('webserver').innerHTML = content;

    info = data.info.output.replace(/\n/g, '<br>');
    document.getElementById('info').innerHTML = info;

    // extract IP address from INFO
    // console.log(data.info.output);
    var rx = /\nIP Address ->(.*)\n/gm;
    var arr = rx.exec((data.info.output));
    document.getElementById('ipaddr').innerHTML = arr[1]; 
}
