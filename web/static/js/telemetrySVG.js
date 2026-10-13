/////////////////////////////
// Connect to RabbitMQ
// Track Map is defined by first record hitting MQ 
// New Session Detected, triggers new map
// calls newSession API (Returns, Track, Version & Fastest Lap Time)
// Call reflap wih Track and Version to get Reference for that Specific Track
// 
// Uses referenceLap function to return track map
//
// Uses SVG instead of PLOTLY to render dashboard and Map
//
/////////////////////////////

// Create a client instance
const clientID = "livelapsMQ" + parseInt(Math.random() * 100);
var wsbroker = location.hostname;  // mqtt websocket enabled broker
var wsport = 15675; // port for above

client = new Paho.MQTT.Client(wsbroker, wsport, '/ws', clientID);
client.onConnectionLost = onConnectionLost;
client.onMessageArrived = onMessageArrived;

var keepS1 = 0;
var keepS2 = 0;
var f_s1 = 0;
var f_s2 = 0;
var f_lt = 0;
var bestLap = 0;
var c_session = "";
var turndata=[];
var inlap =0;
var dsq = false;
var got_track =false;

//TO DO get this from YAML Config
var apiurl = "https://apigw.withoracle.cloud/livelaps";

console.log("Go Go Go!");

var options = {
  timeout: 3,
  keepAliveInterval: 30,
  userName: rmqusername,
  password: rmqpassword,
  onSuccess: onConnect,  
  onFailure: onFailure,
};

const svgns = 'http://www.w3.org/2000/svg';

let svg_track = document.createElementNS(svgns, 'path');
let svg_trackS1 = document.createElementNS(svgns, 'path');
let svg_trackS2 = document.createElementNS(svgns, 'path');
let svg_trackS3 = document.createElementNS(svgns, 'path');
let svg_car = document.createElementNS(svgns, 'circle');
let svg_flag = document.createElementNS(svgns, 'circle');

function onConnect() {
  console.log("RMQ Connect");
  document.getElementById("message").innerHTML = "Connected to F1Sim";
  client.subscribe('', {qos: 1});
}

function onFailure(message) {
  console.log("RMQ Failed: ", message);
}

// called when the client loses its connection
function onConnectionLost(responseObject) {
  if (responseObject.errorCode !== 0) {
    console.log("RMQ Connection Lost: "+responseObject.errorMessage);
  }
};

// Console Switch to turn Data Connector (to MQ) on and off
function consoleSwitch() {
  // Get the checkbox
  var checkBox = document.getElementById("sw_console");
  // Get the output text
  var text = document.getElementById("message");
  // Turn on Spinner
  document.getElementById("loader").style.visibility = "visible";

  // If the checkbox is checked, display the output text
  if (checkBox.checked == true){
    
    // connect to RabbitMQ 
    message.innerHTML = "Connecting to F1Sim";
    console.log("Connect to ", wsbroker);
    // connect the client
    client.connect(options);

    acc = document.getElementById("s1_acc");
    brk = document.getElementById("s1_br");

  } else {
  // Disconnect RabbitMQ
    document.getElementById("loader").style.visibility = "hidden";
    client.disconnect();
    message.innerHTML = "Disconnected";
    document.getElementById("info").innerHTML = 'BOX BOX';
    document.getElementById("info_data").innerHTML = '&nbsp;';
    document.getElementById("carSpot").style.visibility="hidden";
    document.getElementById("bw_flag").style.visibility="hidden";
    document.getElementById("s1_speed").textContent="---";
    document.getElementById("carFlag").style.visibility="hidden";
  }
}

// Called when a message arrives from MQ
function onMessageArrived(message) {

  //payload = message.payloadString.replace(/'/g, '"').replace(/^"(.+(?="$))"$/, '$1');
  // extract SESSION ID as a string from payload
  payload =  message.payloadString.replace(/"m_session": (\d*),/, '"m_session": "$1",');
  const telemetry = JSON.parse(payload);
  //console.log(telemetry);

  // Fetch Session data if never seen session before
  if (typeof telemetry.m_session !== 'undefined' && c_session !== telemetry.m_session) fetchSession(telemetry.m_session);

  if (typeof telemetry.m_speed !== 'undefined' ) {
    // TELEMETRY DATA Packet
    speedkm = telemetry.m_speed;
    acc_pc = (telemetry.m_throttle *100);
    brk_pc = (telemetry.m_brake * 100);
    rev_pc = ((telemetry.m_engineRPM / 15000) *100);
    drs= telemetry.m_drs;


    if (telemetry.m_gear == 0 ) {
      gear = "N";
    } else if (telemetry.m_gear <0 ) {
      gear = "R";
    } else {
      gear = telemetry.m_gear.toFixed(0);
    }
     
    set_meter(document.getElementById("acc"), acc_pc);
    set_meter(document.getElementById("br"), brk_pc);
    set_meter(document.getElementById("rev"), rev_pc);

    document.getElementById("s1_speed").textContent = speedkm.toFixed(0);
    if (drs =1 ) { // DRS = Green, <200km = White > 200 = Red
      document.getElementById("s1_speed").style.color = "var(--f1-timing-green)";
    } else if (speedkm < 200 ){
      document.getElementById("s1_speed").style.color = "var(--f1-timing-white)";
    } else if (speedkm >= 200) {
      document.getElementById("s1_speed").style.color = "var(--f1-timing-red)";
    }

    //document.getElementById("s1_rpm").innerHTML = telemetry.m_engineRPM.toFixed(0);
    document.getElementById("s1_gear").innerHTML = gear;

    // rotate Wheel Image
    wheel_rot = 180 * telemetry.m_steer;
    wheel = document.getElementById("wheel");
    wheel.style.transform = `rotate(${wheel_rot}deg`;
  }

  if (typeof telemetry.m_current_lap_num !=='undefined') {
    // LAP DATA Packet
    //console.log(telemetry);

    // if (typeof xOffset !== 'undefined' && telemetry.m_current_lap_invalid == 1 && !dsq && got_track) {
    if (telemetry.m_current_lap_invalid == 1 && !dsq && got_track) {
      document.getElementById("bw_flag").style.visibility="visible"; 
      // put marker where flag was issued
      document.getElementById("carFlag").setAttribute('cx',xOffset );
      document.getElementById("carFlag").setAttribute('cy',yOffset );
      document.getElementById("carFlag").style.visibility="visible";
      dsq = true;
    }

    // If lap is 0, then technically sitting in pits
    if (telemetry.m_lap_distance >0) {
      inlap = 1;
      document.getElementById("s1_lap").innerHTML = telemetry.m_current_lap_num;
    } else {
      inlap = 0;
      dsq = false;
      document.getElementById("s1_lap").innerHTML = 'OUT';
      document.getElementById("s1_sec").innerHTML = '-';
      if (got_track) {
        document.getElementById("bw_flag").style.visibility="hidden";
        document.getElementById("carFlag").style.visibility="hidden";
      }
    }

    if (telemetry.m_sector == 0 && telemetry.m_current_lap_num > 1) {
      // Keep Sector Times for last lap on until first sector is complete
      s3time = telemetry.m_last_lap_time_in_ms - keepS1 - keepS2;
    
      document.getElementById("s1_s1").innerHTML = convertTime(keepS1).shortlap;
      document.getElementById("s1_s2").innerHTML = convertTime(keepS2).shortlap;
      document.getElementById("s1_s3").innerHTML = convertTime(s3time).shortlap;
      document.getElementById("s1_s1").style.color = "var(--f1-timing-green)";
      document.getElementById("s1_s2").style.color = "var(--f1-timing-green)";
      document.getElementById("s1_s3").style.color = "var(--f1-timing-green)";
      // New Lap so turn Invalid OFF
      if (telemetry.m_current_lap_invalid == 0 && dsq ) {
        document.getElementById("bw_flag").style.visibility="hidden";
        document.getElementById("carFlag").style.visibility="hidden";
        dsq = false;
      }

    } else {
      document.getElementById("s1_s1").innerHTML = convertTime(telemetry.m_sector1_time_in_ms).shortlap;
      document.getElementById("s1_s2").innerHTML = convertTime(telemetry.m_sector2_time_in_ms).shortlap;
      document.getElementById("s1_s3").innerHTML = convertTime(0).shortlap;
      document.getElementById("s1_s1").style.color = "var(--f1-timing-yellow)";
      document.getElementById("s1_s2").style.color = "var(--f1-timing-yellow)";
      document.getElementById("s1_s3").style.color = "var(--f1-timing-yellow)";
      keepS1 = telemetry.m_sector1_time_in_ms;
      keepS2 = telemetry.m_sector2_time_in_ms;
    }
   
    if (bestLap == 0 || (bestLap > 0 && telemetry.m_last_lap_time_in_ms != 0 && telemetry.m_last_lap_time_in_ms < bestLap)) 
    {
      bestLap = telemetry.m_last_lap_time_in_ms;
      document.getElementById("s1_blap").innerHTML = convertTime(bestLap).lap;
      document.getElementById("s1_blap").style.color = "var(--f1-timing-green)";
    }

    document.getElementById("s1_sec").innerHTML = telemetry.m_sector+1;
    document.getElementById("s1_clap").innerHTML = convertTime(telemetry.m_current_lap_time_in_ms).lap;
    document.getElementById("s1_llap").innerHTML = convertTime(telemetry.m_last_lap_time_in_ms).lap;
  }

  if (typeof telemetry.m_worldPosX !== 'undefined' && got_track) {
    // MOTION DATA Packet
    // Detect Turn
    var turn = inTurn(telemetry.m_worldPosX, telemetry.m_worldPosY)
    if (inlap && turn <100) {
      document.getElementById("info").innerHTML = "Turn " + turn;
      document.getElementById("info_data").innerHTML = ordinal_suffix_of(gear) + " Gear";
    } else if (inlap) {
      document.getElementById("info").innerHTML = "&nbsp;";
      document.getElementById("info_data").innerHTML = "&nbsp;";
    }
   
    // Rotate car worldX,worldY position based on Map Rotation
    xOffset = rot(telemetry.m_worldPosX, telemetry.m_worldPosY)[0];
    yOffset = (rot(telemetry.m_worldPosX, telemetry.m_worldPosY)[1])*-1;

    document.getElementById("carSpot").setAttribute('cx',xOffset );
    document.getElementById("carSpot").setAttribute('cy',yOffset );
  }
}

// New Session is Identified...
function fetchSession(sessionid) {
  //console.log("New Session: " + sessionid);
  c_session = sessionid; // Store so we don't keep fetching API data
  document.getElementById("info_data").innerHTML =c_session;
  document.getElementById("info").innerHTML = "Session";
  document.getElementById("track_info").innerHTML = "Fetching Track Info";
  var sessionapi = apiurl + "/newSession/"+ c_session
  document.getElementById("message").innerHTML = "Receiving Data";

  console.log("Fetching Session: "+ sessionapi);
  // go Get Session Details
  fetch(sessionapi,{cache: "no-cache"})
    .then((response) => response.json())
    .then((data) => sessionData(data))
}

// Fetch Session Details (to get Track and Fastest Lap details)
function sessionData(data) {

  var lapi = apiurl + "/trackmap/";

  if (typeof data.SESSIONDATA != "undefined" && data.SESSIONDATA !=null) {
    var newTrack = encodeURIComponent(data.SESSIONDATA.M_TRACKID);
    var trackVer = data.SESSIONDATA.M_PACKET_FORMAT;
    lapi = lapi + newTrack + "/" + trackVer;
    bestLap = data.SESSIONDATA.TRACK_FASTEST_IN_MS;
    document.getElementById("s1_blap").innerHTML = convertTime(bestLap).lap;
  } else {
    // Default to Home Track
    lapi = lapi + hometrack + "/" + gameversion;
    bestLap = 0;
  }

  //xconsole.log("Fetching track details: "+ lapi);
  // Now get Lap details and Draw Cicuit
  fetch(lapi,{cache: "no-cache"})
  .then((response) => response.json())
  .then((data) => trackData(data))
}

// Get Track Map & Turn data
function trackData(data) {

  document.getElementById("loader").style.visibility = "hidden";
  
  mapdata = data.TRACK_DETAIL;
  turndata = data.TURNDATA;
  ang = mapdata.ROTATION;

  // targeting the svg itself
  const map = document.getElementById("s2");
  got_track = true;
  document.getElementById("track_detail").style.visibility = "visible";
  document.getElementById("track_info").innerHTML = data.TRACK_DETAIL.TITLE;
  document.getElementById("lap_record").innerHTML = data.TRACK_DETAIL.LAPRECORD_DRIVER;
  document.getElementById("track_len").innerHTML = (data.TRACK_DETAIL.TRACK_LENGTH/1000) + "km";

  map.setAttribute('viewBox', data.TRACK_DETAIL.SVG_VIEWBOX);
  map.setAttribute('height',data.TRACK_DETAIL.MAP_HEIGHT*0.5);
  map.setAttribute('width', data.TRACK_DETAIL.MAP_WIDTH *0.5);

  trackPath = data.TRACK_SVG;

  svg_track.setAttribute('d',trackPath);
  svg_track.setAttribute('stroke-width', '24');
  svg_track.setAttribute('stroke', 'black');
  svg_track.setAttribute('fill', 'none');
  svg_track.setAttribute("id", "Track");  

  trackPath = data.TRACK_S1;
  svg_trackS1.setAttribute('d',trackPath);
  svg_trackS1.setAttribute('stroke-width', '12');
  svg_trackS1.setAttribute('stroke', '#e73323');
  svg_trackS1.setAttribute('fill', 'none');
  svg_trackS1.setAttribute("id", "S1");  

  trackPath = data.TRACK_S2;
  svg_trackS2.setAttribute('d',trackPath);
  svg_trackS2.setAttribute('stroke-width', '12');
  svg_trackS2.setAttribute('stroke', '#4fafdf');
  svg_trackS2.setAttribute('fill', 'none');
  svg_trackS2.setAttribute("id", "S2");

  trackPath = data.TRACK_S3;
  svg_trackS3.setAttribute('d',trackPath);
  svg_trackS3.setAttribute('stroke-width', '12');
  svg_trackS3.setAttribute('stroke', '#f7d347');
  svg_trackS3.setAttribute('fill', 'none');
  svg_trackS3.setAttribute("id", "S3");  

  svg_car.setAttribute('visibility', 'visible');
  svg_car.setAttribute('cx', 250);
  svg_car.setAttribute('cy', 410);
  svg_car.setAttribute('r', '30px');
  svg_car.setAttribute('id', 'carSpot');
  svg_car.setAttribute('fill', '#fff');

  svg_flag.setAttribute('visibility', 'hidden');
  svg_flag.setAttribute('cx', 250);
  svg_flag.setAttribute('cy', 410);
  svg_flag.setAttribute('r', '30px');
  svg_flag.setAttribute('id', 'carFlag');
  svg_flag.setAttribute('fill', 'url(#flag_bw)');

  // append the new rectangle to the svg
  map.appendChild(svg_track);
  map.appendChild(svg_trackS1);
  map.appendChild(svg_trackS2);
  map.appendChild(svg_trackS3);
  map.appendChild(svg_car); 
  map.appendChild(svg_flag); 

  // Add Turn indicators

  for(var i =0;i < turndata.length;i++) {
    svg_turn = document.createElementNS(svgns, 'circle');
    svg_turn.setAttribute('cx', turndata[i].APEX_X1);
    svg_turn.setAttribute('cy', turndata[i].APEX_Y1);
    svg_turn.setAttribute('r', '30px');
    svg_turn.setAttribute('id', 'Turn'+(i+1));
    svg_turn.setAttribute('class', 'turn');
    map.appendChild(svg_turn);
    // Labels
    svg_turn_indicator = document.createElementNS(svgns, 'text');
    svg_turn_indicator.setAttribute('x', turndata[i].APEX_X1-23);
    svg_turn_indicator.setAttribute('y', turndata[i].APEX_Y1+10);
    svg_turn_indicator.setAttribute('class', 'turn-label');
    svg_turn_indicator.textContent = (i+1).toString().padStart(2, '0');
    map.appendChild(svg_turn_indicator);
  }

  trackPath = null;
  data = null;
}

function inTurn(x,y) {

  var turn=999;

  for(var ct =0; ct < turndata.length; ct++)
  {
    if (turn == 999 && x > turndata[ct].CX1 && x < turndata[ct].CX2 && y > turndata[ct].CY1 && y < turndata[ct].CY2) {
      turn = ct;
    }
  }

  //if (turn != 999 ) console.log("In turn " + turn);
  return turn+1;
}

function set_meter(path, value) {
  let length = path.getTotalLength();
  let to = length * ((100 - value) / 100);
  path.style.strokeDashoffset = Math.max(0, to);  
}

function setChart() {
  var svg = document.getElementById('chart');
  var point = svg.createSVGPoint();
  point.x = 10;
  point.y = 20;
  var polyline= document.getElementById('polyline-id');
  polyline.points.appendItem(point);
}
