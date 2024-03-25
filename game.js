// start of script
let cueBall = document.getElementById('00'); // the cueball has an ID (ball number) of 0
let isDragging = false;
let shotIndicator; // Define shotIndicator variable outside of event listeners
let x_vel, y_vel;
let text; // Define text variable outside of event listeners

let table = document.getElementById("poolTable");
let svgLayer = document.getElementById("svgLayer"); // hidden layer that goes above the pool table 
const shotWidth  = '10'; // how big to make the shot line
const SCALE_FACTOR = 10;
const SIM_RATE = 0.01;
const REFESH_TIME = 1 // in milliseconds
const INDICATOR_FONT_SIZE = '16px';
const MAX_VEL = 4000.0; // max velocity of a shot

function attatchEventListenersToCueBall() {
    function onMouseDown (event) {
        isDragging = true;
        const initialCueBallPosition = {
            x: cueBall.cx.baseVal.value,
            y: cueBall.cy.baseVal.value
        };
        const initialMousePosition = getSVGFromMouse(event, svgLayer);
        // Update the mouse position as the mouse moves
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
    
        function onMouseMove(event) {
            if (isDragging) {
                const newMousePosition = getSVGFromMouse(event, svgLayer);
                // Calculate the movement of the mouse relative to the initial mouse position
                const dx = newMousePosition.x - initialMousePosition.x;
                const dy = newMousePosition.y - initialMousePosition.y;
                
                if (shotIndicator) {
                    shotIndicator.remove();
                }
                if (text) {
                    text.remove();
                }
                shotIndicator = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                // shotIndicator.setAttribute('stroke', 'rgb(182, 125, 60)');
                shotIndicator.setAttribute('stroke', 'white');
                shotIndicator.setAttribute('stroke-width', shotWidth);
                shotIndicator.setAttribute('stroke-dasharray', shotWidth * 2, shotWidth); // Set stroke-dasharray for dashed line
                
                cueBallMouseCoord = getMouseFromSVG(initialCueBallPosition, table);
    
                shotIndicator.setAttribute('x1', cueBallMouseCoord.x);
                shotIndicator.setAttribute('y1', cueBallMouseCoord.y);
                // console.log(initialMousePosition.x, initialMousePosition.y);
                // console.log("CUE BALL:" + initialCueBallPosition.x, initialCueBallPosition.y);
    
                shotIndicator.setAttribute('x2', newMousePosition.x);
                shotIndicator.setAttribute('y2', newMousePosition.y);
                // Create text element for velocity
                text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                text.setAttribute('x', newMousePosition.x - 40);
                text.setAttribute('y', newMousePosition.y - 20);
                text.setAttribute('fill', 'red');
                text.setAttribute('font-size', INDICATOR_FONT_SIZE);
                x_vel = dx * SCALE_FACTOR;
                y_vel = dy * SCALE_FACTOR;
                // console.log("x_vel:", x_vel);
                // console.log("y_vel:", y_vel);
                // Ensure that the velocities don't exceed 4000
                if (Math.abs(x_vel) > MAX_VEL) {
                    // console.log("x_vel exceeded 4000");
                    if (x_vel > 0) {
                        x_vel = MAX_VEL;
                    }
                    else {
                        x_vel = -MAX_VEL;
                    }
                }
                if (Math.abs(y_vel) > MAX_VEL) {
                    // console.log("y_vel exceeded 4000");
                    if (y_vel > 0) {
                        y_vel = MAX_VEL;
                    }
                    else {
                        y_vel = -MAX_VEL;
                    }
                }
                const formattedXVel = Math.round(x_vel * 10) / 10;
                const formattedYVel = Math.round(y_vel * 10) / 10;
                // text.textContent = `Velocity: (${formattedXVel.toFixed(1)}, ${formattedYVel.toFixed(1)})`;
                text.textContent = `(${formattedXVel.toFixed(1)}, ${formattedYVel.toFixed(1)})`;
                svgLayer.appendChild(text);
                svgLayer.appendChild(shotIndicator);
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
                    text.remove();
                }
            } else { // For other mouse buttons, cancel the shot
                console.log('Shot canceled due to non-left click');
                if (shotIndicator) {
                    shotIndicator.remove();
                }
                if (text) {
                    text.remove();
                }
            }
        }
    }
    cueBall.addEventListener('mousedown', onMouseDown)
    cueBall.addEventListener("mouseover", function(event) {
        this.style.cursor = "pointer";
    });
}
attatchEventListenersToCueBall();
// Right click event listener to cancel the shot
table.addEventListener('contextmenu', function(event) {
    event.preventDefault(); // prevent right click on table
});

function getSVGFromMouse(event, SVGObject) {
    // converts mouse position to svg position via black magic
    const point = document.createElementNS('http://www.w3.org/2000/svg', 'svg').createSVGPoint();
    point.x = event.clientX;
    point.y = event.clientY;
    // const svg = document.getElementById('poolTable');
    return point.matrixTransform(SVGObject.getScreenCTM().inverse());
}

function svgRefreshFunction(tableData, timeData) {
    tableDisplay = document.getElementById("svgTableDisplay");
    tableDisplay.innerHTML = tableData;
    document.getElementById("time").textContent = "Table time: " + timeData.toFixed(2);
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
                    resolve(JSON.parse(xhr.responseText));
                } else {
                    console.error('Network response was not ok');
                    reject(new Error('Network response was not ok'));
                }
            }
        };
        xhr.send(JSON.stringify(shotData));
        console.log("sent req")
    });
}

async function handleShotData(shotData) {
    try {
        const JSONData = await sendShotData(shotData);
        console.log(JSONData);
        console.log(JSONData.length);
        let num_svgs = Number(JSONData[0].num_svgs)
        console.log("number of svgs: " + num_svgs, typeof(num_svgs));
        for (let i = 1; i < num_svgs; i++) {
            svgRefreshFunction(JSONData[i][`table-${i - 1}`], JSONData[i][`table-${i - 1}_time`]);
            await new Promise(resolve => setTimeout(resolve, REFESH_TIME));
        }
        if (JSONData[num_svgs + 1].cue_ball_sunk) {
            console.log("CUE BALL WAS SUNK!");
            window.alert(`The Cue ball was sunk. Reverting cue ball position to initial spot.\n`);
        }
        refreshPage();
    } catch (error) {
        console.error('Error handling shot data:', error);
    }
}

function getMouseFromSVG(SVGTableCoordinate) {
    const svgRect = table.getBoundingClientRect(); // Get bounding rectangle of SVG element
    // Calculate absolute mouse coordinates

    // console.log("INPUT XY: " + SVGTableCoordinate.x, SVGTableCoordinate.y);
    // console.log("TABLE XY: " + svgRect.x, svgRect.y);

    const base = table.viewBox.baseVal
    // console.log(svgRect);
    // console.log(table.viewBox.baseVal);
    // console.log("WIDTH: ", (base.width + 2 * base.x));
    // console.log("X dISTANCE: ", SVGTableCoordinate.x/((base.width + 2 * base.x)) * (svgRect.right - svgRect.left));
    const mouseX = svgRect.x + SVGTableCoordinate.x/((base.width + 2 * base.x)) * (svgRect.right - svgRect.left);
    const mouseY = svgRect.y + SVGTableCoordinate.y/((base.height + 2 * base.y)) * (svgRect.bottom - svgRect.top);
    // Return absolute mouse coordinates
    return { x: mouseX, y: mouseY };
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
    // Create a new XMLHttpRequest object
    const xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log("successful refresh");
            // Replace the current document body with the fetched HTML content
            document.body.innerHTML = this.responseText;
            // reset all the key elements
            cueBall = document.getElementById("00");
            table = document.getElementById("poolTable");
            table.addEventListener('contextmenu', function(event) {
                event.preventDefault(); // prevent right click on table
            });
            svgLayer = document.getElementById("svgLayer"); // hidden layer that goes above the pool table 
            console.log(cueBall, table, svgLayer);
            attatchEventListenersToCueBall();
        }
    };
    // Open a GET request
    xhttp.open("GET", "display_game", true);
    xhttp.send();
}
