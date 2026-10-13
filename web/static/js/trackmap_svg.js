/////////////////////////////
// Use Home Track from YAML Config
// SVG Map Version
// 
// Pass Track and Version to API References & Rotation is pre-calculated
// 
// Possible issue with Track Size
// /trackmap/svg/Brazil/2022
// 
// Update to use FETCH
/////////////////////////////

//var xmlhttp = new XMLHttpRequest();

var apiurl = "https://apigw.withoracle.cloud/livelaps/";
var trackMap = "trackmap/" + hometrack + "/" + gameversion;
var flagapi = "https://flagsapi.com/";
var flagtype = "/shiny/64.png";

const svgns = 'http://www.w3.org/2000/svg';

let svg_track = document.createElementNS(svgns, 'path');
let svg_trackS1 = document.createElementNS(svgns, 'path');
let svg_trackS2 = document.createElementNS(svgns, 'path');
let svg_trackS3 = document.createElementNS(svgns, 'path');

getMapData();

function getMapData() {
  document.getElementById("loader").style.visibility = "visible";
  var t_api = apiurl + trackMap;
  console.log("API Url:" + t_api);

  fetch(t_api,{cache: "no-cache"})
  .then((response) => response.json())
  .then((data) => processMap(data))
}

function processMap(data) {

  var turns = true;
  if (typeof data.TRACK_DETAIL != "undefined" && data.TRACK_DETAIL !=null) {

    var country = data.TRACK_DETAIL.FLAG_CODE ?? "AU";
    var flagRef = "<img src='" + flagapi + country + flagtype + "'>";

    var turndata = data.TURNDATA;
    var GAMEHOST = data.TRACK_DETAIL.TRACK;

    mapx = data.TRACK_DETAIL.MAP_WIDTH;
    mapy = data.TRACK_DETAIL.MAP_HEIGHT;

    document.getElementById("loader").style.visibility = "hidden";

    // Set Web components
    document.getElementById("track_id").innerHTML = data.TRACK_DETAIL.TRACK;      
    document.getElementById("track_info").innerHTML = data.TRACK_DETAIL.TITLE;
    document.getElementById("track_len").innerHTML = (data.TRACK_DETAIL.TRACK_LENGTH/1000) + "km";
    document.getElementById("track_co").innerHTML = data.TRACK_DETAIL.COUNTRY;
    document.getElementById("flag").insertAdjacentHTML("afterbegin", flagRef);

    // targeting the svg itself
    const map = document.getElementById("s2");

    document.getElementById("track_detail").style.visibility = "visible";
    document.getElementById("track_f1lr").innerHTML = data.TRACK_DETAIL.LAPRECORD_DRIVER;
    //document.getElementById("track_llr").innerHTML = data.TRACK_DETAIL.LAPRECORD_DRIVER;

    map.setAttribute('viewBox', data.TRACK_DETAIL.SVG_VIEWBOX);
    map.setAttribute('height',data.TRACK_DETAIL.MAP_HEIGHT);
    map.setAttribute('width', data.TRACK_DETAIL.MAP_WIDTH);
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

    // append the new rectangle to the svg
    map.appendChild(svg_track);
    map.appendChild(svg_trackS1);
    map.appendChild(svg_trackS2);
    map.appendChild(svg_trackS3);

    // Add Turn indicators
    if (turns) {
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
    }
  } else {
    document.getElementById("loader").style.visibility = "hidden";
    document.getElementById("mapper").style.visibility = "hidden";
  }

  trackPath = null;
  data = null;
}
