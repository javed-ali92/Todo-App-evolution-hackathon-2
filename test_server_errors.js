// Test script to see actual error
const { spawn } = require('child_process');
const fs = require('fs');

console.log('Starting Next.js server to capture errors...');

const server = spawn('npx', ['next', 'dev', '-p', '3000'], {
  cwd: './frontend',
  stdio: 'inherit',
  shell: true
});

server.on('error', (err) => {
  console.error('Server error:', err);
});

server.on('close', (code) => {
  console.log(`Server closed with code: ${code}`);
});