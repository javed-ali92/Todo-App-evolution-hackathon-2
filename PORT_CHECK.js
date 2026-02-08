const net = require('net');

function checkPort(port, host = 'localhost') {
    return new Promise((resolve) => {
        const socket = new net.Socket();

        setTimeout(() => {
            socket.destroy();
            resolve(false);
        }, 3000); // 3 second timeout

        socket.connect(port, host, () => {
            socket.end();
            resolve(true);
        });

        socket.on('error', () => {
            socket.destroy();
            resolve(false);
        });
    });
}

async function main() {
    console.log('Checking ports...');

    const backendOpen = await checkPort(8000);
    const frontendOpen = await checkPort(3000);

    console.log(`Backend (8000): ${backendOpen ? 'OPEN' : 'CLOSED'}`);
    console.log(`Frontend (3000): ${frontendOpen ? 'OPEN' : 'CLOSED'}`);

    if (frontendOpen) {
        console.log('\nThe frontend should be accessible at http://localhost:3000');
        console.log('The backend is accessible at http://localhost:8000');
        console.log('\nBoth servers are now running correctly!');
    } else {
        console.log('\nFrontend server might still be starting up or there might be an issue.');
        console.log('Try refreshing or waiting a bit longer.');
    }
}

main();