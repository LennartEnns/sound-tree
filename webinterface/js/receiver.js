let socket; 
function startConnection(){
    // Create WebSocket connection.
    socket = new WebSocket("ws://localhost:8080");    

    // Connection opened
    socket.addEventListener("open", (event) => {
        console.log("WebSocket verbunden.");
    }); 

    // Listen for messages
    socket.addEventListener("message", async (event) => {
        //console.log("Message from server", event.data);

        // Wandelt den Blob in einen ArrayBuffer um
        const arrayBuffer = await event.data.arrayBuffer();

        // Erstelle ein Int8Array aus dem Buffer
        const uInt8Array = new Uint8Array(arrayBuffer);
        //console.log("blob", event.data.arrayBuffer());
        startReceive(uInt8Array)
        //console.log("uInt8Array:", uInt8Array);
    });
}

function stopConnection() {
    if (socket) {
        socket.close();
    }
}