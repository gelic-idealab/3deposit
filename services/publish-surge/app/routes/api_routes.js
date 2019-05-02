module.exports = function(app, db) {
    app.post('/', (req, res) => {
      // process post request
      console.log(req.body)
      res.send('post request working...')
    });
  };