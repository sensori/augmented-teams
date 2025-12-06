function helloWorld() {
    const randomNum = Math.floor(Math.random() * 1000) + 1;
    const timestamp = new Date().toISOString();
    const message = `Hello, World! Random number: ${randomNum} | Timestamp: ${timestamp}`;
    const fs = require('fs');
    const path = require('path');
    
    // Write output to file
    try {
        const outputFile = 'c:\\dev\\augmented-teams\\hello_js_output.txt';
        const fullPath = outputFile;
        console.log(`Writing to: ${fullPath}`);
        fs.writeFileSync(outputFile, message + '\n');
        console.log(`File written successfully to: ${fullPath}`);
        if (fs.existsSync(outputFile)) {
            console.log(`File exists: ${fs.existsSync(outputFile)}`);
        } else {
            console.log('ERROR: File does not exist after write!');
        }
    } catch (error) {
        console.log(`ERROR writing file: ${error.message}`);
    }
    
    console.log(message);
}

helloWorld();
