// Simple script to start Next.js dev server with error handling
const { spawn } = require('child_process');
const fs = require('fs');

console.log('Checking Next.js configuration...');

// Check if src/app directory exists (Next 13+ App Router)
const appDir = './src/app';
const legacyPagesDir = './pages';

if (!fs.existsSync(appDir) && !fs.existsSync(legacyPagesDir)) {
    console.error('ERROR: Neither src/app nor pages directory found!');
    console.error('Make sure your Next.js app has the proper structure.');
    process.exit(1);
}

console.log('Starting Next.js development server on port 3000...');
console.log('Backend should be running on http://localhost:8000');

const nextProcess = spawn('npx', ['next', 'dev', '-p', '3000'], {
    stdio: 'inherit',
    cwd: process.cwd(),
    shell: true
});

nextProcess.on('error', (err) => {
    console.error('Failed to start Next.js server:', err.message);
});

nextProcess.on('close', (code) => {
    console.log(`Next.js server exited with code ${code}`);
});