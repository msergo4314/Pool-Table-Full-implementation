// start of script
let isDragging, flashing = false;
let shotIndicator, shotIndicator2; // Define shotIndicator variable outside of event listeners
let x_vel, y_vel;
let text; // Define text variable outside of event listeners
let SPEEDUP_FACTOR = 2;
let table = document.getElementById("poolTable");
let cueBall, cueBallBoundingRectangle;
let svgLayer = document.getElementById("svgLayer"); // hidden layer that goes above the pool table 
const shotWidth  = '14'; // how big to make the shot line
const SCALE_FACTOR = 10;
const SIM_RATE = 0.01;
let REFRESH_TIME = 8;
let SPEEDUP = false;
const INDICATOR_FONT_SIZE = '16px';
const MAX_VEL = 1e4; // max velocity of a shot
const maxIndicatorLength = 100;

setup();

function attatchEventListenersToCueBall() {
    function onMouseDown (event) {
        isDragging = true;
        const initialCueBallPosition = {
            x: cueBall.cx.baseVal.value,
            y: cueBall.cy.baseVal.value
        };
        cueBall = table.querySelector('circle[fill="WHITE"]') // the cueball is the only white ball
        cueBallBoundingRectangle = cueBall.getBoundingClientRect();
        const initialMousePosition = getSVGFromMouse(event, svgLayer);
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
    
        function onMouseMove(event) {
            if (isDragging) {
                const newMousePosition = getSVGFromMouse(event, svgLayer);
                // Calculate the movement of the mouse relative to the initial mouse position
                const dx = (newMousePosition.x - initialMousePosition.x);
                const dy = (newMousePosition.y - initialMousePosition.y);

                // cueballpos - endcursorpos.x
                
                if (shotIndicator) {
                    shotIndicator.remove();
                }
                if (shotIndicator2) {
                    shotIndicator2.remove();
                }
                const cueBallMousePos = getMouseFromSVG(svgLayer);

                shotIndicator = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                shotIndicator.setAttribute('class', 'shotIndicator');

                // shotIndicator2 = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                
                // shotIndicator2.setAttribute('x1', cueBallMousePos.x);
                // shotIndicator2.setAttribute('y1', cueBallMousePos.y);
                // shotIndicator2.setAttribute('x2', (newMousePosition.x));
                // shotIndicator2.setAttribute('y2', (newMousePosition.y));

                shotIndicator.setAttribute('x1', cueBallMousePos.x);
                shotIndicator.setAttribute('y1', cueBallMousePos.y);
                shotIndicator.setAttribute('x2', (newMousePosition.x));
                shotIndicator.setAttribute('y2', (newMousePosition.y));

                // Create text element for velocity
                // text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                // text.setAttribute('x', newMousePosition.x - 40);
                // text.setAttribute('y', newMousePosition.y - 20);
                // text.setAttribute('fill', 'red');
                // text.setAttribute('font-size', INDICATOR_FONT_SIZE);
                x_vel = dx * SCALE_FACTOR;
                y_vel = dy * SCALE_FACTOR;
                // console.log("x_vel:", x_vel);
                // console.log("y_vel:", y_vel);
                // Ensure that the velocities don't exceed 4000
                let vel = Math.hypot(x_vel, y_vel);
                if (vel > MAX_VEL) {
                    ratio = MAX_VEL / vel;
                    x_vel *= ratio;
                    y_vel *= ratio;
                }
                const formattedXVel = Math.round(x_vel * 10) / 10;
                const formattedYVel = Math.round(y_vel * 10) / 10;
                document.getElementById("speedBox").innerHTML = `<div class=\"infoBoxLeadingText\" >Shot Speed: </div>\

                (${formattedXVel.toFixed(0)}, ${formattedYVel.toFixed(0)})`;
                svgLayer.appendChild(shotIndicator);
                // svgLayer.appendChild(shotIndicator2);
            }
        }
        function onMouseUp(event) {
            isDragging = false;
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
            if (event.button === 0) { // Only proceed if it's a left click
                if (shotIndicator) {
                    // acceleration = getAccelerationFromVelocity(x_vel, y_vel);
                    // const formattedXVel = Math.round(x_vel * 10) / 10;
                    // const formattedYVel = Math.round(y_vel * 10) / 10;
                    // const formattedXAcc = Math.round(acceleration.xacc * 10) / 10;
                    // const formattedYAcc = Math.round(acceleration.yacc * 10) / 10;
                    
                    // const confirmShot = window.confirm(`Are you sure you want to take this shot?\n` +
                    // `XVEL: ${formattedXVel.toFixed(1)}\nYVEL: ${formattedYVel.toFixed(1)}\n` +
                    // `XACC: ${formattedXAcc.toFixed(1)}\nYACC: ${formattedYAcc.toFixed(1)}`);
                    confirmShot = true;
                    if (confirmShot) {
                        shotVel = {
                            x_vel,
                            y_vel
                        };
                        const shotData = {
                            initialPosition: initialCueBallPosition,
                            velocity: shotVel,
                        };
                        handleShotData(shotData); // will update svg images accordingly
    
                    } else {
                        console.log('Shot canceled by user');
                    }
                    shotIndicator.remove();
                }
            } else { // For other mouse buttons, cancel the shot
                console.log('Shot canceled due to non-left click');
                if (shotIndicator) {
                    shotIndicator.remove();
                }
                if (shotIndicator2) {
                    shotIndicator2.remove();
                }
                document.getElementById("speedBox").innerHTML = `<div class=\"infoBoxLeadingText\" >Shot Speed: </div>N/A`;
            }
        }
    }
    cueBall.addEventListener('mousedown', onMouseDown)
    cueBall.addEventListener("mouseover", function(event) {
        this.style.cursor = "pointer";
    });
}
// Right click event listener to cancel the shot

function setup() {
    table = document.getElementById("poolTable");
    cueBall = table.querySelector('circle[fill="WHITE"]') // the cueball is the only white ball
    cueBallBoundingRectangle = cueBall.getBoundingClientRect();
    document.body.style.cursor = "auto";
    addEventListenersToTable();
    svgLayer = document.getElementById("svgLayer"); // hidden layer that goes above the pool table
    attatchEventListenersToCueBall();
}

function addEventListenersToTable() {
    table.addEventListener('mousedown', function(event) {
        onMouseDownTable(event, table);
    });

    table.addEventListener('mouseup', function(event) {
        onTableMouseUp(event);
    });
    document.addEventListener('contextmenu', function(event) {
        event.preventDefault(); // prevent right click on table
    });
}

function onMouseDownTable(event, table) {
    if (event.button === 2) { // Check for right mouse button
        SPEEDUP = true
        if (flashing) {
            document.body.style.cursor = "url(\"images/fast_cursor.bmp\"), auto";
        }
        console.log(document.body.style.cursor);
    }
}

function onTableMouseUp(event) {
    SPEEDUP = false
    document.body.style.cursor = "auto";
}

function getSVGFromMouse(event, SVGObject) {
    // converts mouse position to svg position via black magic
    const point = document.createElementNS('http://www.w3.org/2000/svg', 'svg').createSVGPoint();
    point.x = event.clientX;
    point.y = event.clientY;
    return point.matrixTransform(SVGObject.getScreenCTM().inverse());
}

function svgRefreshFunction(tableData, timeData) {
    tableDisplay = document.getElementById("svgTableDisplay");
    tableDisplay.innerHTML = tableData;
    table = document.getElementById("poolTable");
    addEventListenersToTable();
    document.getElementById("time").innerHTML = `<div class=\"infoBoxLeadingText\">Table time: </div>${Number(timeData).toFixed(2)}`;
}

function sendShotData(shotData) {
    return new Promise(function(resolve, reject) {
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/new_shot', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.onreadystatechange = function () {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status == 200) {
                    console.log('Shot data sent successfully');
                    resolve(xhr.responseText);
                } else {
                    console.error('Network response was not ok');
                    reject(new Error('Network response was not ok'));
                }
            }
        };
        xhr.send(JSON.stringify(shotData));
        console.log("sent shot data:" + shotData.velocity.x_vel, shotData.velocity.y_vel)
    });
}

async function handleShotData(shotData) {
    try {
        // send the data, wait for request to get response text
        const TextData = await sendShotData(shotData);
        var svgData = TextData.split('\n\n'); // Split by double newline characters
        // console.log(svgData.length)
        flashing = true;
        for (let i = 0; i < svgData.length - 2; i += 2) {
            if (SPEEDUP && (i % (2 * SPEEDUP_FACTOR) == 0)) {
                // skip every other frame
                continue;
            }
            svgRefreshFunction(svgData[i].trim(), svgData[i+1].trim());
            await new Promise(resolve => setTimeout(resolve, REFRESH_TIME)); // wait for period
        }
        if (svgData[svgData.length-1] == "True") {
            console.log("CUE BALL WAS SUNK!");
            // window.alert(`The Cue ball was sunk. Reverting cue ball position to initial spot.\n`);
        }
        flashing = false;
        refreshPage();
        SPEEDUP = false;
    } catch (error) {
        console.error('Error handling shot data:', error);
    }
}

function getAllSVGs(endTime, callback) {
    let time = 0.00;

    function requestSVG(timeOfRequestedSVG) {
        var xhr = new XMLHttpRequest();
        var url = '/single_svg?time=' + encodeURIComponent(timeOfRequestedSVG)
        xhr.open('GET', url, true);
        xhr.setRequestHeader('Content-Type', 'image/svg+xml');
        xhr.onreadystatechange = function () {
            // if the response has been fully received
            if (xhr.readyState == 4) {
                if (xhr.status == 200) {
                    tableDisplay = document.getElementById("svgTableDisplay");
                    if (tableDisplay) {
                        tableDisplay.innerHTML = xhr.responseText;
                    }
                    if (time <= endTime) {
                        time += SIM_RATE;
                        setTimeout(() => requestSVG(parseFloat(time.toFixed(2))), 100);
                    } else if (callback) {
                        callback();
                    }
                } else {
                    console.error('Network failed to send SVGs');
                }
            }
        };
        xhr.send();
        // console.log(`Requested all svgs for time: ${timeOfRequestedSVG}`);
    }

    requestSVG(time);
}

function refreshPage() {
    const xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            // console.log("successful refresh");
            // Replace the current document body with the fetched HTML content
            document.body.innerHTML = this.responseText;
            // reset all the key elements
            setup();
        }
    };
    // Open a GET request
    xhttp.open("GET", "display_game", true);
    xhttp.send();
}

function getMouseFromSVG(screenSVGLayer) {
    // Return absolute mouse coordinates
    // const cueBall_x = cueBallBoundingRectangle.left
    // const cueBall_y = cueBallBoundingRectangle.top
    const cueBall_x = cueBallBoundingRectangle.left + (cueBallBoundingRectangle.width / 2);
    const cueBall_y = cueBallBoundingRectangle.top + (cueBallBoundingRectangle.height / 2);
    
    console.log("CUEBALL X Y:", cueBall_x, cueBall_y);
    console.log("CUEBALL RECT:", cueBallBoundingRectangle);
    const mouseX = cueBall_x - screenSVGLayer.getBoundingClientRect().left;
    const mouseY = cueBall_y - screenSVGLayer.getBoundingClientRect().top;
    return { x: mouseX, y: mouseY };
}
