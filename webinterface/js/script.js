const manualColors = [];
for (let i = 0; i < 10; i++){
    manualColors.push("#0000FF");
}
for (let i = 0; i < 10; i++){
    manualColors.push("#00FFFF");
}
for (let i = 0; i < 10; i++){
    manualColors.push("#FF0000");
}
for (let i = 0; i < 12; i++){
    manualColors.push("#00FF00");
}

const NUM_LIGHTS = 44;
let currentMode = "live"; // "live", "snake", "blink"
let intervalId = null;

// Lichter generieren
document.querySelectorAll('.segment').forEach(segment => {
    const count = parseInt(segment.dataset.lights, 10);
    const lightsContainer = segment.querySelector('.lights');

    for (let i = 0; i < count; i++) {
        const light = document.createElement('div');
        light.className = 'light';
        lightsContainer.appendChild(light);
    }
});

// Helfer: Zufällige Farbe generieren
function randomHexColor() {
    return "#" + Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0');
}

// Anwenden eines Farbfelds auf die Lichter
function applyColorsToLights(colorArray) {
    const lights = document.querySelectorAll('.light');
    lights.forEach((light, index) => {
        if (index < colorArray.length) {
            light.style.backgroundColor = colorArray[index];
            light.style.boxShadow = `0 0 5px ${colorArray[index]}`;
        }
    });
}

// Live-Update Modus: Farben aus einem empfangenen Array (simuliert)
function startLiveUpdate() {
    clearInterval(intervalId);
    currentMode = "live";
    intervalId = setInterval(() => {
        const colorArray = [];
        for (let i = 0; i < NUM_LIGHTS; i++) {
            colorArray.push(randomHexColor());
        }
        applyColorsToLights(colorArray);
    }, 1000);
}

// Snake-Modus: Eine Farbe läuft als Schlange durch
function startSnakeAnimation(color = "#00ffcc", speed = 100) {
    clearInterval(intervalId);
    currentMode = "snake";
    const lights = document.querySelectorAll('.light');
    let position = 0;

    intervalId = setInterval(() => {
        lights.forEach((light, index) => {
            light.style.backgroundColor = "#000000"; // Hintergrund aus
            light.style.boxShadow = "none";
        });

        // Nur ein Licht an der aktuellen Position
        lights[position].style.backgroundColor = color;
        lights[position].style.boxShadow = `0 0 5px ${color}`;

        position = (position + 1) % lights.length;
    }, speed);
}

// Blink-Modus: Alle Lichter blinken gleichzeitig
function startBlinkAnimation(colors = ["#ff0000", "#0000ff"], interval = 500) {
    clearInterval(intervalId);
    currentMode = "blink";
    const lights = document.querySelectorAll('.light');
    let colorIndex = 0;

    intervalId = setInterval(() => {
        const currentColor = colors[colorIndex];
        lights.forEach(light => {
            light.style.backgroundColor = currentColor;
            light.style.boxShadow = `0 0 5px ${currentColor}`;
        });
        colorIndex = (colorIndex + 1) % colors.length;
    }, interval);
}

// Optional: Initial starten
window.onload = () => {
    startReceiver();
    startLiveUpdate();
};