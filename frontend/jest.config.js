console.log("Jest configuration is loaded");

module.exports = {
    transform: {
      '^.+\\.js$': 'babel-jest',  // Use Babel to transform ES modules
    },
    testEnvironment: 'node',
  };