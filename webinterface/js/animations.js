const manualColors = [];
for (let i = 0; i < 10; i++){
    manualColors.push("#0000ff");
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
let currentMode = "live";
let intervalId = null;


//Blink-Random Modus: alle Lichter blinken in zufälligen Farben
function startRandomBlink() {
    stopConnection();
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

//Receive Modus: empfängt Daten von Python mittels receiver.js
function startReceive(bitArray) {
    clearInterval(intervalId);
    let colorArray = [];
    let color = "#";
    for(let i = 1; i < NUM_LIGHTS*3+1; i++){
        let hexDigit = bitArray[i-1].toString(16);
        if (hexDigit.length < 2){
            color = color + "0" + hexDigit
        }else{
            color = color + hexDigit
        }
        
        if(i%3 == 0){
            let newColor = convertRGBsimulation(color)
            colorArray.push(newColor)
            color = "#";
        }
    }
    //console.log("Farben-Größe", colorArray.length)
    //console.log("Farben", colorArray)
    applyColorsToLights(colorArray);
}

//Snake Modus: eine Farbe läuft als Schlange durch
function startSnake(color = "#00ffcc", speed = 100) {
    stopConnection();
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

//Blink Modus: alle Lichter blinken in definierten Farben
function startBlink(colors = ["#ff0000", "#0000ff"], interval = 500) {
    stopConnection();
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