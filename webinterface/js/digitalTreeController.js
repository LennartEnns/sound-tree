// Anwenden eines Farbfelds auf die Lichter
// function applyColorsToLights(colorArray) {
//     // Umkehren des Farbarrays
//     const reversedColorArray = colorArray.reverse(); // Hier kehren wir das Array um
    
//     const lights = document.querySelectorAll('.light');
//     lights.forEach((light, index) => {
//         if (index < reversedColorArray.length) {
//             light.style.backgroundColor = reversedColorArray[index];
//             light.style.boxShadow = `0 0 5px ${reversedColorArray[index]}`;
//         }
//     });
// }

// function applyColorsToLights(colorArray) {
//     // Umkehren des Farbarrays
//     const reversedColorArray = colorArray; // Hier kehren wir das Array um
    
//     const lights = document.querySelectorAll('.light');
    
//     // Umkehren der Lichter von links nach rechts auf rechts nach links
//     [...lights].reverse().forEach((light, index) => {
//         if (index < reversedColorArray.length) {
//             light.style.backgroundColor = reversedColorArray[index];
//             light.style.boxShadow = `0 0 5px ${reversedColorArray[index]}`;
//         }
//     });
// }

function applyColorsToLights(colorArray) {
    const segments = document.querySelectorAll('.segment');
    const lightsPerSegment = Array.from(segments).map(segment => parseInt(segment.dataset.lights, 10));
    
    let colorIndex = 0; // Wir beginnen bei der ersten Farbe im Array
    
    // Kehr das colorArray um, sodass das oberste Segment den höchsten Ton bekommt
    const reversedColorArray = colorArray.reverse();

    // Iteriere über die Segmente (von oben nach unten)
    segments.forEach((segment, segmentIndex) => {
        const lightCount = lightsPerSegment[segmentIndex];
        const lightsContainer = segment.querySelector('.lights');
        const lights = lightsContainer.querySelectorAll('.light');
        
        // Berechne, wie viele Farben in dieses Segment gehören
        const segmentColors = reversedColorArray.slice(colorIndex, colorIndex + lightCount);
        
        // Wende die Farben im Segment an
        lights.forEach((light, index) => {
            if (index < segmentColors.length) {
                light.style.backgroundColor = segmentColors[index];
                light.style.boxShadow = `0 0 5px ${segmentColors[index]}`;
            }
        });

        // Erhöhe den Farbindex für das nächste Segment
        colorIndex += lightCount;
    });
}


function randomHexColor() {
    return "#" + Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0');
}

function hexToRgb(hex) {
    // Entfernt das '#' und konvertiert den HEX-Wert zu RGB
    let r = parseInt(hex.slice(1, 3), 16);
    let g = parseInt(hex.slice(3, 5), 16);
    let b = parseInt(hex.slice(5, 7), 16);
    return { r, g, b };
}

function rgbToHex(r, g, b) {
    // Konvertiert RGB-Werte zurück in HEX
    return `#${(1 << 24 | r << 16 | g << 8 | b).toString(16).slice(1).toUpperCase()}`;
}

function adjustBrightness(rgb, factor) {
    // Skaliert die RGB-Werte basierend auf einem Helligkeitsfaktor (0-1)
    return {
        r: Math.min(255, Math.max(0, rgb.r * factor)),
        g: Math.min(255, Math.max(0, rgb.g * factor)),
        b: Math.min(255, Math.max(0, rgb.b * factor))
    };
}

function convertRGBsimulation(hexColor){
    const rgb = hexToRgb(hexColor);
    const factor = 1.5; // Helligkeit anpassen (größer als 1 = heller, kleiner als 1 = dunkler)
    const adjustedRgb = adjustBrightness(rgb, factor);
    const adjustedHex = rgbToHex(adjustedRgb.r, adjustedRgb.g, adjustedRgb.b);

    return adjustedHex;
}