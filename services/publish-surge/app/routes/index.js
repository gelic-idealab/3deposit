const apiRoutes = require('./api_routes');

module.exports = function(app, db) {
  apiRoutes(app, db);
  // Other route groups could go here, in the future
};