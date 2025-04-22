let socket; 
function startConnection(){
    socket = new WebSocket("ws://localhost:8080");    

    socket.addEventListener("open", (event) => {
        console.log("WebSocket verbunden.");
    }); 

    // Listen for messages
    socket.addEventListener("message", async (event) => {
        //console.log("Message from server", event.data);
        const arrayBuffer = await event.data.arrayBuffer();
        const uInt8Array = new Uint8Array(arrayBuffer);
        startReceive(uInt8Array)
    });
}

function stopConnection() {
    if (socket) {
        socket.close();
    }
}