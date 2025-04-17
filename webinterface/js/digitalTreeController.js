// Anwenden eines Farbfelds auf die Lichter
function applyColorsToLights(colorArray) {
    //console.log("FarbenArray", colorArray)
    const lights = document.querySelectorAll('.light');
    lights.forEach((light, index) => {
        if (index < colorArray.length) {
            light.style.backgroundColor = colorArray[index];
            light.style.boxShadow = `0 0 5px ${colorArray[index]}`;
        }
    });
}

function randomHexColor() {
    return "#" + Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0');
}