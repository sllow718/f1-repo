/////////////////////////////
// Track Analyser
/////////////////////////////


const apiurl = "https://apigw.withoracle.cloud/livelaps";
var trackMap = "/analyser/" + hometrack + "/" + gameversion;
var sessions = "/laps/" + hometrack + "/" + gameversion + "/" + gamehost;
var lapdata = "/lapdata/";
const flagapi = "https://flagsapi.com/";
const flagtype = "/shiny/64.png";

const svgns = 'http://www.w3.org/2000/svg';

let svg_racing = document.createElementNS(svgns, 'path');
let svg_comp = document.createElementNS(svgns, 'path');
let svg_ref = document.createElementNS(svgns, 'path');
let svg_track = document.createElementNS(svgns, 'path');
let trackf = document.createElementNS(svgns, 'g');

var defaultVB;
var turnAnalyse =0;
var numTurns =0;
var cmax = false;
var czoom = 1;

var turnAnalysis;

// Panning functionality
let isDragging = false;
let previousX = 0;
let previousY = 0;
let viewBoxWidth =0;
let viewBoxHeight =0;
let viewBoxX =0;
let viewBoxY =0;

getBestLaps();

getMapData();

function getBestLaps() {
  console.log("Fetching Best Laps");

  var t_api = apiurl + sessions;
  
  fetch(t_api, {cache: "no-cache"})
  .then((response) => response.json())
  .then((data) => refLaps(data))
}

function refLaps(data) {
  // list of top 10 sessions for track / version / and gamehost
  //  console.log(data);
  // Create Drop Down Selection List
    if (data.laps != null ) {
    var select = document.createElement("select");
    select.name = "laps";
    select.id = "laps";
    select.setAttribute("onchange", "selectlap()");
    
    // Set select list
    var option = document.createElement("option");
    option.value = "";
    option.text = "Comparison Lap >";
    select.appendChild(option);
 
    for (const val of data.laps)
    {
      var option = document.createElement("option");
      option.value = val.SESSIONID;
      option.setAttribute('lap',val.LAP_NUMBER);
      option.text = 'Time: ' + convertTime(val.LAPTIME).lap;
      select.appendChild(option);
    }
    document.getElementById("container").appendChild(select);
  }
}

function getMapData() {
  document.getElementById("loader").style.visibility = "visible";
  var t_api = apiurl + trackMap;
  //console.log(t_api);

  fetch(t_api,  {cache: "no-cache"})
  .then((response) => response.json())
  .then((data) => processMap(data))
}

function selectlap() {
  e = document.getElementById("laps");
  var sessionid = e.value;
  var lap = e.options[e.selectedIndex].getAttribute('lap');
  if (sessionid != "") {
    //console.log(sessionid + ": lap " + lap);
    // fetch selected reference lap
    //var t_api = apiurl + lapdata + sessionid + "/"+lap;
    var t_api = 'https://fortatp.withoracle.cloud/ords/f1sim/f1/trackanalyser/lap/' + sessionid + "/"+lap;
  
    console.log("Fetching Comparison Lap");
    // Turn on Spinner
    document.getElementById("loader").style.visibility = "visible";

    fetch(t_api,  {cache: "no-cache"})
    .then((response) => response.json())
    .then((data) => showLapData(data))
  }
}

function showLapData(data) {
  //console.log(data);
  turnAnalysis = data.turns;
  // Turn off Spinner
  document.getElementById("loader").style.visibility = "hidden";

  document.getElementById("lt").innerHTML = convertTime(data.lap_timing.LAPTIME).lap;
  document.getElementById("sec1").innerHTML = convertTime(data.lap_timing.S1).lap;
  document.getElementById("sec2").innerHTML = convertTime(data.lap_timing.S2).lap;
  document.getElementById("sec3").innerHTML = convertTime(data.lap_timing.S3).lap;
  document.getElementById("complap").style.visibility = "visible";
  document.getElementById("bcomp").style.visibility = "visible";

  if (data.lap_timing.INVALID_LAP == 'true') {
    document.getElementById("invalid").style.visibility = "visible";
  }

  // Build Comparison Lap
  const map = document.getElementById("s2");
  // Comp Lap
  trackPath = data.lap_map;
  svg_comp.setAttribute('d',trackPath);
  svg_comp.setAttribute("id", "comp"); 
  svg_comp.setAttribute("class", "comp_line");
  map.appendChild(svg_comp);
  data = null;
}

function processMap(data) {

  var turns = true;
  if (typeof data.TRACK_DETAIL != "undefined" && data.TRACK_DETAIL !=null) {

    var turndata = data.TURNDATA;

    mapx = data.TRACK_DETAIL.MAP_WIDTH;
    mapy = data.TRACK_DETAIL.MAP_HEIGHT;

    document.getElementById("loader").style.visibility = "hidden";

    // Set Web components
    document.getElementById("track_id").innerHTML = data.TRACK_DETAIL.TRACK;      

    // targeting the svg itself
    const map = document.getElementById("s2");

    defaultVB = data.TRACK_DETAIL.SVG_VIEWBOX;
    map.setAttribute('viewBox', defaultVB);
    map.setAttribute('height',data.TRACK_DETAIL.MAP_HEIGHT);
    map.setAttribute('width', data.TRACK_DETAIL.MAP_WIDTH);
    viewBoxWidth = data.TRACK_DETAIL.MAP_WIDTH;
    viewBoxHeight = data.TRACK_DETAIL.MAP_HEIGHT;

    trackPath = data.TRACK_LEFT + "  " + data.TRACK_RIGHT;
    svg_track.setAttribute('d', trackPath);
    svg_track.setAttribute('id', "whole_track");
    
    // Racing Line
    trackPath = data.TRACK_RACING;
    svg_racing.setAttribute('d',trackPath);
    svg_racing.setAttribute("id", "racing"); 
    svg_racing.setAttribute("class", "racing_line");

    trackf.setAttribute("class", "track_fill");
    trackf.appendChild(svg_track);
    map.appendChild(trackf);
    
    // Add Turn indicators
    numTurns = turndata.length;
    
    if (turns) {
      for(var i =0;i < numTurns;i++) {

        let trackf = document.createElementNS(svgns, 'g');
        svg_turn = document.createElementNS(svgns, 'circle');
        svg_turn.setAttribute('cx', turndata[i].APEX_X1);
        svg_turn.setAttribute('cy', turndata[i].APEX_Y1);
        svg_turn.setAttribute('r', '30px');

        svg_turn.setAttribute('class', 'turn');

        // Labels
        svg_turn_indicator = document.createElementNS(svgns, 'text');
        svg_turn_indicator.setAttribute('x', turndata[i].APEX_X1-22);
        svg_turn_indicator.setAttribute('y', turndata[i].APEX_Y1+11);
        svg_turn_indicator.setAttribute('font-size', '1.9em');
        svg_turn_indicator.setAttribute('stroke', '#fff');
        svg_turn_indicator.textContent = (i+1).toString().padStart(2, '0');
        
        trackf.appendChild(svg_turn);
        trackf.appendChild(svg_turn_indicator);
        trackf.setAttribute('class', 'tlabel');
        trackf.setAttribute('id', 'Turn'+(i+1));
        map.appendChild(trackf);
      }
    }
    
    // append the new path to the svg
    map.appendChild(svg_racing);

    // Is there a Challenge Max Lap?
    if (typeof data.CMAX != "undefined" && data.CMAX !=null && data.CMAX != "err2") {
      cmax=true;
      trackPath = data.CMAX;
      svg_ref.setAttribute('d',trackPath);
      svg_ref.setAttribute("id", "ref"); 
      svg_ref.setAttribute("class", "ref_line");
      map.appendChild(svg_ref);
      document.getElementById("brefl").style.visibility = 'visible';
    } else {
      console.log("No Challenge Max Lap");
    }

  } else {
    document.getElementById("loader").style.visibility = "hidden";
    document.getElementById("mapper").style.visibility = "hidden";
  }

  trackPath = null;
  data = null;

  map.addEventListener('mousedown', (event) => {
    isDragging = true;
    previousX = event.clientX;
    previousY = event.clientY;
  });

  map.addEventListener('mousemove', (event) => {
    if (isDragging) {
      const deltaX = event.clientX - previousX;
      const deltaY = event.clientY - previousY;
  
      //map.style.transform = `scale(${czoom}) translate(${deltaX}px, ${deltaY}px)`;
      viewBoxX -= deltaX * viewBoxWidth / map.clientWidth;
      viewBoxY -= deltaY * viewBoxHeight / map.clientHeight;
  
      applyZoom();
  
      previousX = event.clientX;
      previousY = event.clientY;
    }
  });
  
  map.addEventListener('mouseup', () => {
    isDragging = false;
  });
}

function btn_racing() {
  line = document.getElementById("racing").style.visibility;
  if (line == 'hidden') {
    document.getElementById("racing").style.visibility = 'visible';
  } else {
    document.getElementById("racing").style.visibility = 'hidden';
  }
}

function btn_comp() {
  line = document.getElementById("comp").style.visibility;
  if (line == 'hidden') {
    document.getElementById("comp").style.visibility = 'visible';
  } else {
    document.getElementById("comp").style.visibility = 'hidden';
  }
}

function btn_ref() {
  line = document.getElementById("ref").style.visibility;
  if (line == 'hidden') {
    document.getElementById("ref").style.visibility = 'visible';
  } else {
    document.getElementById("ref").style.visibility = 'hidden';
  }
}

function btn_zoom(scale) {
  if (scale == 1) {
    turnAnalyse++;
    if (turnAnalyse > numTurns) turnAnalyse=1;
  } else {
    turnAnalyse--;
    if (turnAnalyse ==0 ) turnAnalyse = numTurns;
  }
  zoomIntoRegion('s2', turnAnalyse);
}

function zoomOut() {
  czoom += 0.1;
  viewBoxWidth /= 1.2;
  viewBoxHeight /= 1.2;
  applyZoom();
}

function zoomIn() {
  if (czoom > 0.2) {
    czoom -= 0.1;
    viewBoxWidth *= 1.2;
    viewBoxHeight *= 1.2;
    applyZoom();
  }
}

function zoomReset() {
    turnAnalyse =0;
    region = document.getElementById('s2');
    region.setAttribute('viewBox', defaultVB);
    region.transform = `scale(0.5) translate(0px 0px)`;
    region.style = ``;
    document.getElementById("turn").style.visibility="hidden";
}

function applyZoom() {
    var svgMap = document.getElementById('s2');
    svgMap.setAttribute('viewBox', `${viewBoxX} ${viewBoxY} ${viewBoxWidth} ${viewBoxHeight}`)
}

function zoomIntoRegion(svgElement, turn) {
  // Get the SVG element and the region element
  var regionId = 'Turn'+turn;
  document.getElementById('track_co').innerHTML = regionId;
  var svg = document.getElementById(svgElement);
  var region = document.getElementById(regionId);

  // Get the bounding box of the region
  var bbox = region.getBBox();
  viewBoxWidth = 385;
  viewBoxHeight = 230;

  viewBoxX = bbox.x -180;//* viewBoxWidth / map.clientWidth;
  viewBoxY = bbox.y -120;// * viewBoxHeight / map.clientHeight;

  applyZoom();

  previousX = region.clientX;
  previousY = region.clientY;

  // Show Turn Data
  if (typeof turnAnalysis != "undefined" && turnAnalysis != null)  {
    document.getElementById("sect").innerHTML =turnAnalysis.turn[turn-1].SECTOR;
    document.getElementById("turn_title").innerHTML =turnAnalysis.turn[turn-1].TURN;
    document.getElementById("avssp").innerHTML = turnAnalysis.turn[turn-1].AVG_SECTOR_SPEED + " km/h";
    document.getElementById("avsp").innerHTML = turnAnalysis.turn[turn-1].AVG_TURN_SPEED + " km/h";
    document.getElementById("mxsp").innerHTML = turnAnalysis.turn[turn-1].MAX_TURN_SPEED + " km/h";
    document.getElementById("turn").style.visibility="visible";
  }
}