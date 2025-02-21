console.log("Babel configuration is loaded");

module.exports = {
    presets: [
      '@babel/preset-env', // This preset allows Babel to transform modern JavaScript (ES6+) to a version compatible with your Node.js environment.
    ],
    // You can add more options here if needed, such as plugins or specific configurations.
  };