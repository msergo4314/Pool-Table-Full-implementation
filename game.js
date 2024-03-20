// start of script
const cueBall = document.getElementById('00'); // the cueball has an ID (ball number) of 0
let isDragging = false;
let shotIndicator; // Define shotIndicator variable outside of event listeners
let x_vel, y_vel;
let text; // Define text variable outside of event listeners
let DocumentFragment;
const table = document.getElementById("poolTable");
const svgLayer = document.getElementById("svgLayer"); // hidden layer that goes above the pool table
const shotWidth  = '10'; // how big to make the shot line
const INDICATOR_FONT_SIZE = '16px';

const DRAG = 150.0;
const MAX_VEL = 4000.0; // max velocity of a shot
// const MAX_SINGLE_VEL = Math.sqrt((MAX_VEL ** 2)/2);

cueBall.addEventListener('mousedown', function (event) {
    console.log("cueball mousedown")
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
            console.log("adjusted pos:" + cueBallMouseCoord.x, cueBallMouseCoord.y)

            shotIndicator.setAttribute('x1', cueBallMouseCoord.x);
            shotIndicator.setAttribute('y1', cueBallMouseCoord.y);
            // console.log(initialMousePosition.x, initialMousePosition.y);
            // console.log("CUE BALL:" + initialCueBallPosition.x, initialCueBallPosition.y);

            shotIndicator.setAttribute('x2', newMousePosition.x);
            shotIndicator.setAttribute('y2', newMousePosition.y);
            console.log("made the line");
            // Create text element for velocity
            text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', newMousePosition.x - 40);
            text.setAttribute('y', newMousePosition.y - 20);
            text.setAttribute('fill', 'red');
            text.setAttribute('font-size', INDICATOR_FONT_SIZE);
            x_vel = dx * 7;
            y_vel = dy * 7;
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
                acceleration = getAccelerationFromVelocity(x_vel, y_vel);
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
                        acceleration: acceleration
                    };
                    sendShotData(shotData);
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
});

cueBall.addEventListener("mouseover", function(event) {
    this.style.cursor = "pointer";
});

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

function getAccelerationFromVelocity(xvel, yvel) {
    const rollingBallSpeed = Math.hypot(xvel, yvel);
    xacc = 0.0, yacc = 0.0;
    if (rollingBallSpeed > DRAG) {
        xacc = -xvel * DRAG / rollingBallSpeed;
        yacc = -yvel * DRAG / rollingBallSpeed;
    }
    return {
        xacc,
        yacc
    };
}

function sendShotData(shotData) {
    // Send a POST request to the server
    console.log("sending shot data: " + x_vel + ' ' + y_vel);
    fetch('/new_shot', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(shotData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        // Handle successful response
        return response.json();
    })
    .then(data => {
        // Handle response data
        console.log(data);
    })
    .catch(error => {
        // Handle errors
        console.error('There was a problem with the request:', error);
    });
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
