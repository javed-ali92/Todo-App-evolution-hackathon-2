/*
 * Script to test and start the frontend properly
 */

const fs = require('fs');
const path = require('path');
const { exec, spawn } = require('child_process');

const frontendDir = path.join(__dirname, 'frontend');

console.log('=== Frontend Setup and Start Script ===');
console.log('Directory:', frontendDir);

// Check if package.json exists
const pkgPath = path.join(frontendDir, 'package.json');
if (!fs.existsSync(pkgPath)) {
    console.error('ERROR: package.json not found in frontend directory');
    process.exit(1);
}

console.log('✓ package.json found');

// Check Next.js app structure
const srcAppDir = path.join(frontendDir, 'src', 'app');
const appDir = path.join(frontendDir, 'app');

let appLocation = '';
if (fs.existsSync(srcAppDir)) {
    appLocation = srcAppDir;
    console.log('✓ App Router found in src/app');
} else if (fs.existsSync(appDir)) {
    appLocation = appDir;
    console.log('✓ App Router found in app');
} else {
    console.error('ERROR: No app directory found (either src/app or app)');
    process.exit(1);
}

// Check for main page file
const pageFiles = ['page.tsx', 'page.jsx', 'page.js'];
let mainPageFound = false;
for (const pageFile of pageFiles) {
    const pagePath = path.join(appLocation, pageFile);
    if (fs.existsSync(pagePath)) {
        console.log(`✓ Main page found: ${pageFile}`);
        mainPageFound = true;
        break;
    }
}

if (!mainPageFound) {
    console.error('ERROR: No main page file found (page.tsx, page.jsx, or page.js)');
    console.error('Available files in app directory:', fs.readdirSync(appLocation));
    process.exit(1);
}

console.log('\nAttempting to start Next.js development server on port 3000...');
console.log('Make sure backend is running on port 8000');

// Try to start the server
const child = spawn('npx', ['next', 'dev', '-p', '3000'], {
    cwd: frontendDir,
    stdio: 'pipe',
    shell: true
});

child.stdout.on('data', (data) => {
    console.log(`STDOUT: ${data}`);
});

child.stderr.on('data', (data) => {
    console.error(`STDERR: ${data}`);
});

child.on('close', (code) => {
    console.log(`Next.js process exited with code ${code}`);
});

// Keep the script running
setTimeout(() => {
    console.log('\nNext.js server should be running on http://localhost:3000');
    console.log('Check your browser or use curl to test the connection');
}, 3000);