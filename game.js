// start of script
const cueBall = document.getElementById('00'); // the cueball has an ID (ball number) of 0
let isDragging = false;
let shotIndicator; // Define shotIndicator variable outside of event listeners
let x_vel, y_vel;
let text; // Define text variable outside of event listeners
let DocumentFragment;
const table = document.getElementById("poolTable");

const shotWidth  = '25'; // how big to make the shot line
const INDICATOR_FONT_SIZE = '50px';

const DRAG = 150.0;
const MAX_VEL = 4000.0; // max velocity of a shot
// const MAX_SINGLE_VEL = Math.sqrt((MAX_VEL ** 2)/2);

cueBall.addEventListener('mousedown', function (event) {
    isDragging = true;
    const initialCueBallPosition = {
        x: cueBall.cx.baseVal.value,
        y: cueBall.cy.baseVal.value
    };

    const initialMousePosition = getMousePositionSVG(event);

    // Update the mouse position as the mouse moves
    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);

    function onMouseMove(event) {
        if (isDragging) {
            const newMousePosition = getMousePositionSVG(event);
            // Calculate the movement of the mouse relative to the initial mouse position
            const dx = newMousePosition.x - initialMousePosition.x;
            const dy = newMousePosition.y - initialMousePosition.y;
            
            // console.log("dx:", dx);
            // console.log("dy:", dy);
            if (shotIndicator) {
                shotIndicator.remove();
            }
            if (text) {
                text.remove(); // Remove previous text element
            }
            // Create a new shotIndicator line
            shotIndicator = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            shotIndicator.setAttribute('stroke', 'white');
            shotIndicator.setAttribute('stroke-width', shotWidth);
            shotIndicator.setAttribute('stroke-dasharray', shotWidth * 2, shotWidth); // Set stroke-dasharray for dashed line
            // Set the starting point of the line to the initial position of the cue ball
            shotIndicator.setAttribute('x1', initialCueBallPosition.x);
            shotIndicator.setAttribute('y1', initialCueBallPosition.y);
            // Set the ending point of the line based on the scaled mouse movement
            shotIndicator.setAttribute('x2', initialCueBallPosition.x + dx);
            shotIndicator.setAttribute('y2', initialCueBallPosition.y + dy);

            // Create text element for velocity
            text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', initialCueBallPosition.x + dx + 10);
            text.setAttribute('y', initialCueBallPosition.y + dy - 10);
            text.setAttribute('fill', 'red');
            text.setAttribute('font-size', INDICATOR_FONT_SIZE);
            x_vel = dx * 2.25;
            y_vel = dy * 2.25;
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
            table.appendChild(text);
            table.appendChild(shotIndicator);
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
                    const shotData = {
                        initialPosition: initialCueBallPosition,
                        velocity: {
                            x_vel: x_vel,
                            y_vel: y_vel
                        },
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

function getMousePositionSVG(event) {
    // converts mouse position to svg position via black magic
    const point = document.createElementNS('http://www.w3.org/2000/svg', 'svg').createSVGPoint();
    point.x = event.clientX;
    point.y = event.clientY;
    const svg = document.getElementById('poolTable');
    return point.matrixTransform(svg.getScreenCTM().inverse());
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
