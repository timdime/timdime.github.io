// --- Game Initialization ---
const gameCanvas = document.getElementById('gameCanvas');
const ctx = gameCanvas.getContext('2d');
const startGameBtn = document.getElementById('startGameBtn');
const restartGameBtn = document.getElementById('restartGameBtn');
const gameOverlay = document.getElementById('gameOverlay');
const finalScoreDisplay = document.getElementById('finalScore');
const timerDisplay = document.getElementById('timer');
const scoreDisplay = document.getElementById('score');
const levelDisplay = document.getElementById('level');

let gameRunning = false;
let score = 0;
let level = 1;
let timer = 0;
let countdownInterval;
let selectedPort = null; // Stores { type: 'server'|'switch', obj: serverObj|switchObj, portIndex: 0 }

// Game configuration (adjust these values for difficulty)
const GRID_SIZE = 50; // Size of each grid cell
const RACK_WIDTH = 12; // Number of columns in the rack
const RACK_HEIGHT = 10; // Number of rows in the rack
const CABLE_COLORS = ['#e74c3c', '#2ecc71', '#3498db', '#f1c40f', '#9b59b6']; // Red, Green, Blue, Yellow, Purple

// Game entities (servers, switches, cables)
let servers = [];
let switches = [];
let cables = [];

// --- Game Objects (Classes/Constructors for better organization) ---

class Device {
    constructor(x, y, type, id) {
        this.x = x; // Grid x position
        this.y = y; // Grid y position
        this.pixelX = x * GRID_SIZE + GRID_SIZE / 2; // Center pixel x
        this.pixelY = y * GRID_SIZE + GRID_SIZE / 2; // Center pixel y
        this.type = type; // 'server' or 'switch'
        this.id = id;
        this.ports = []; // Array of port objects
        this.width = GRID_SIZE * 2; // Devices might take more than one grid cell
        this.height = GRID_SIZE * 1.5;
    }

    draw(ctx) {
        // Draw basic device shape
        ctx.fillStyle = this.type === 'server' ? '#95a5a6' : '#7f8c8d'; // Server: silver, Switch: dark gray
        ctx.fillRect(this.pixelX - this.width / 2, this.pixelY - this.height / 2, this.width, this.height);

        // Draw ports
        this.ports.forEach(port => {
            ctx.fillStyle = port.connected ? '#c0392b' : '#27ae60'; // Red if connected, Green if available
            ctx.beginPath();
            ctx.arc(port.pixelX, port.pixelY, 5, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = '#2c3e50';
            ctx.lineWidth = 1;
            ctx.stroke();
        });

        // Draw text ID
        ctx.fillStyle = '#ecf0f1';
        ctx.font = '10px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(`${this.type.toUpperCase()} ${this.id}`, this.pixelX, this.pixelY + this.height / 2 - 5);
    }

    getPortsInPixelRange(px, py) {
        return this.ports.find(port =>
            Math.sqrt((port.pixelX - px) ** 2 + (port.pixelY - py) ** 2) < 10 // Click radius
        );
    }
}

class Server extends Device {
    constructor(x, y, id, dataType) {
        super(x, y, 'server', id);
        this.dataType = dataType; // e.g., 'web', 'database', 'storage'
        // Define specific port positions relative to device center
        this.ports = [
            { id: 0, pixelX: this.pixelX - 20, pixelY: this.pixelY + this.height / 2 - 10, connected: false, cable: null },
            { id: 1, pixelX: this.pixelX + 20, pixelY: this.pixelY + this.height / 2 - 10, connected: false, cable: null }
        ];
    }
}

class Switch extends Device {
    constructor(x, y, id, capacity, functionType) {
        super(x, y, 'switch', id);
        this.capacity = capacity; // Max number of connections
        this.functionType = functionType; // e.g., 'L2', 'L3', 'core'
        this.connections = 0;
        // Define ports dynamically based on capacity, or pre-defined for visual appeal
        for (let i = 0; i < capacity; i++) {
            // Distribute ports around the switch
            const angle = (Math.PI * 2 / capacity) * i;
            const radius = 30; // Distance from center
            this.ports.push({
                id: i,
                pixelX: this.pixelX + radius * Math.cos(angle),
                pixelY: this.pixelY + radius * Math.sin(angle),
                connected: false,
                cable: null,
                expectedDataType: null // What kind of data this switch port expects
            });
        }
    }
}

class Cable {
    constructor(startPort, endPort, color, serverId, switchId, dataType) {
        this.startPort = startPort; // {device, portIndex}
        this.endPort = endPort;     // {device, portIndex}
        this.color = color;         // Matches data type or network segment
        this.serverId = serverId;
        this.switchId = switchId;
        this.dataType = dataType; // e.g., 'web', 'database'
    }

    draw(ctx) {
        ctx.strokeStyle = this.color;
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(this.startPort.pixelX, this.startPort.pixelY);
        ctx.lineTo(this.endPort.pixelX, this.endPort.pixelY);
        ctx.stroke();
    }
}

// --- Game Logic Functions ---

function initializeGame() {
    gameOverlay.classList.add('hidden');
    score = 0;
    timer = 0;
    level = 1; // Always start at level 1
    servers = [];
    switches = [];
    cables = [];
    selectedPort = null;
    timerDisplay.textContent = 'Time: 0:00';
    scoreDisplay.textContent = 'Score: 0';
    levelDisplay.textContent = `Level: ${level}`;

    setupLevel(level); // Setup initial level elements
    gameRunning = true;
    startTimer();
    gameLoop(); // Start the game loop for rendering
}

function setupLevel(currentLevel) {
    // Clear previous elements
    servers = [];
    switches = [];

    // Define level-specific configurations
    // Example: Level 1 - simple connections
    if (currentLevel === 1) {
        servers.push(new Server(2, 2, 1, 'web'));
        servers.push(new Server(2, 4, 2, 'database'));
        servers.push(new Server(2, 6, 3, 'storage'));

        switches.push(new Switch(9, 3, 1, 3, 'L2')); // Capacity 3
        switches.push(new Switch(9, 7, 2, 2, 'L2')); // Capacity 2

        // Assign expected data types to switch ports (simplified for this example)
        switches[0].ports[0].expectedDataType = 'web';
        switches[0].ports[1].expectedDataType = 'database';
        switches[0].ports[2].expectedDataType = 'storage';

        // Add some random "rats' nests" (non-interactive for now, just visual)
        // You'd implement these as separate objects with collision detection for scoring penalties
    } else if (currentLevel === 2) {
        // More servers, more switches, perhaps specific routing rules
        servers.push(new Server(1, 2, 1, 'web'));
        servers.push(new Server(1, 4, 2, 'database'));
        servers.push(new Server(1, 6, 3, 'storage'));
        servers.push(new Server(1, 8, 4, 'backup'));

        switches.push(new Switch(10, 2, 1, 4, 'L3')); // L3 switch
        switches.push(new Switch(10, 6, 2, 2, 'L2')); // L2 switch

        switches[0].ports[0].expectedDataType = 'web';
        switches[0].ports[1].expectedDataType = 'database';
        switches[0].ports[2].expectedDataType = 'storage';
        switches[0].ports[3].expectedDataType = 'backup';
    }
    // Add more levels here with increasing complexity
}

function startTimer() {
    clearInterval(countdownInterval); // Clear any existing timer
    countdownInterval = setInterval(() => {
        timer++;
        const minutes = Math.floor(timer / 60);
        const seconds = timer % 60;
        timerDisplay.textContent = `Time: ${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;

        // Example game over condition (e.g., time limit)
        // if (timer >= 120 && level === 1) { // 2 minutes for level 1
        //     endGame();
        // }
    }, 1000);
}

function endGame(win = false) {
    gameRunning = false;
    clearInterval(countdownInterval);
    gameOverlay.classList.remove('hidden');
    if (win) {
        gameOverlay.querySelector('h3').textContent = 'Level Complete!';
        finalScoreDisplay.textContent = `You scored ${score} points in ${timer} seconds.`;
        // Potentially offer to go to next level
    } else {
        gameOverlay.querySelector('h3').textContent = 'Game Over!';
        finalScoreDisplay.textContent = `You scored ${score} points. Try again!`;
    }
}

function checkWinCondition() {
    // Win condition: All servers are connected correctly and efficiently
    // This is the tricky part and defines the game's core logic.
    // For simplicity, let's say all server ports must be connected.
    // And each connection must match the `dataType` of the server to the `expectedDataType` of the switch port.

    if (servers.every(server => server.ports.every(port => port.connected))) {
        let allCorrect = true;
        for (const cable of cables) {
            const server = servers.find(s => s.id === cable.serverId);
            const sw = switches.find(s => s.id === cable.switchId);

            if (server && sw) {
                // Find the connected port on the switch
                const connectedSwitchPort = sw.ports.find(p => p.cable === cable);
                if (connectedSwitchPort && connectedSwitchPort.expectedDataType !== server.dataType) {
                    allCorrect = false;
                    break;
                }
            } else {
                allCorrect = false; // Should not happen if cables are well-formed
                break;
            }
        }

        if (allCorrect) {
            // Calculate bonus score for time and efficiency (e.g., fewer crossed cables)
            score += Math.max(0, 1000 - timer * 5); // Time bonus
            // Add bonus for minimal cable crossing (requires collision detection for cables)

            endGame(true);
            // If you have multiple levels, you might proceed to the next level here
            // level++;
            // setTimeout(() => initializeGame(), 2000); // Small delay before next level
        }
    }
}

function handleClick(event) {
    if (!gameRunning) return;

    const rect = gameCanvas.getBoundingClientRect();
    const pixelX = event.clientX - rect.left;
    const pixelY = event.clientY - rect.top;

    // Check for clicks on servers
    for (const server of servers) {
        const port = server.getPortsInPixelRange(pixelX, pixelY);
        if (port && !port.connected) {
            if (selectedPort) {
                // Deselect if clicking the same port again
                if (selectedPort.obj === server && selectedPort.portIndex === port.id) {
                    selectedPort = null;
                } else {
                    // Start a new selection if a different port is clicked
                    selectedPort = { type: 'server', obj: server, portIndex: port.id, pixelX: port.pixelX, pixelY: port.pixelY };
                }
            } else {
                selectedPort = { type: 'server', obj: server, portIndex: port.id, pixelX: port.pixelX, pixelY: port.pixelY };
            }
            return; // Exit after handling
        }
    }

    // Check for clicks on switches
    for (const sw of switches) {
        const port = sw.getPortsInPixelRange(pixelX, pixelY);
        if (port && !port.connected) {
            if (selectedPort && selectedPort.type === 'server') {
                // We have a server port selected, now connect to this switch port
                const serverPort = selectedPort.obj.ports[selectedPort.portIndex];

                // Check for capacity
                if (sw.connections < sw.capacity) {
                    // Create a new cable
                    const newCable = new Cable(
                        { pixelX: serverPort.pixelX, pixelY: serverPort.pixelY },
                        { pixelX: port.pixelX, pixelY: port.pixelY },
                        CABLE_COLORS[Math.floor(Math.random() * CABLE_COLORS.length)], // Assign random color for now
                        selectedPort.obj.id, // Server ID
                        sw.id,               // Switch ID
                        selectedPort.obj.dataType // Data type from the server
                    );
                    cables.push(newCable);

                    // Mark ports as connected and link cable
                    serverPort.connected = true;
                    serverPort.cable = newCable;
                    port.connected = true;
                    port.cable = newCable;
                    sw.connections++;

                    score += 100; // Award points for connecting
                    scoreDisplay.textContent = `Score: ${score}`;

                    selectedPort = null; // Clear selection
                    checkWinCondition(); // Check if game is won
                } else {
                    console.log('Switch port capacity reached!');
                    // Provide visual feedback to the user (e.g., flash red)
                }
            } else if (selectedPort && selectedPort.type === 'switch') {
                // Deselect if clicking the same port again
                if (selectedPort.obj === sw && selectedPort.portIndex === port.id) {
                    selectedPort = null;
                } else {
                    // Start a new selection if a different switch port is clicked
                    selectedPort = { type: 'switch', obj: sw, portIndex: port.id, pixelX: port.pixelX, pixelY: port.pixelY };
                }
            } else {
                // First click, select this switch port
                selectedPort = { type: 'switch', obj: sw, portIndex: port.id, pixelX: port.pixelX, pixelY: port.pixelY };
            }
            return;
        }
    }

    // If click was on empty space, deselect
    selectedPort = null;
}

// --- Drawing Functions ---
function drawGrid() {
    ctx.strokeStyle = '#34495e'; // Darker grid lines
    ctx.lineWidth = 0.5;
    for (let x = 0; x <= gameCanvas.width; x += GRID_SIZE) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, gameCanvas.height);
        ctx.stroke();
    }
    for (let y = 0; y <= gameCanvas.height; y += GRID_SIZE) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(gameCanvas.width, y);
        ctx.stroke();
    }
}

function drawGame() {
    ctx.clearRect(0, 0, gameCanvas.width, gameCanvas.height);
    // Draw background elements if any (e.g., rack lines)
    ctx.fillStyle = '#2c3e50'; // Background of the rack area
    ctx.fillRect(0, 0, gameCanvas.width, gameCanvas.height);

    drawGrid();

    // Draw servers
    servers.forEach(server => server.draw(ctx));

    // Draw switches
    switches.forEach(sw => sw.draw(ctx));

    // Draw existing cables
    cables.forEach(cable => cable.draw(ctx));

    // Draw temporary cable if a port is selected
    if (selectedPort) {
        ctx.strokeStyle = '#c0392b'; // Red for the current selection
        ctx.lineWidth = 3;
        ctx.setLineDash([5, 5]); // Dashed line for temporary cable
        ctx.beginPath();
        ctx.moveTo(selectedPort.pixelX, selectedPort.pixelY);
        // Draw to mouse position or a placeholder for now.
        // For actual implementation, you'd track mouse position for the line end.
        // For now, we'll draw to the center of the canvas if nothing else is selected.
        ctx.lineTo(gameCanvas.width / 2, gameCanvas.height / 2); // Placeholder line
        ctx.stroke();
        ctx.setLineDash([]); // Reset line dash
    }
}

function gameLoop() {
    if (!gameRunning) return;
    drawGame();
    requestAnimationFrame(gameLoop); // Keep redrawing
}


// --- Event Listeners ---
startGameBtn.addEventListener('click', initializeGame);
restartGameBtn.addEventListener('click', initializeGame);
gameCanvas.addEventListener('click', handleClick);


// Initial setup (set canvas size)
function resizeCanvas() {
    // Set canvas dimensions relative to its container or a fixed size
    gameCanvas.width = gameContainer.offsetWidth; // Make it fit its container
    gameCanvas.height = Math.min(600, gameContainer.offsetWidth * 0.75); // Maintain aspect ratio roughly
}
window.addEventListener('resize', resizeCanvas);
resizeCanvas(); // Call once on load

// You might need to set gameCanvas.style.width and height in CSS to manage its responsiveness.
// The actual game logic for collision detection, scoring based on cable length/crossings,
// and advanced win conditions will be the most complex part to implement.
// You'll also need visual assets for servers, switches, or create more complex shapes with `ctx.beginPath()` etc.
