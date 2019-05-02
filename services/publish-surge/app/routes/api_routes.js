module.exports = function(app, db) {

    app.get('/:id', (req, res) => {
        const id = req.params.id;
        // process get request
        res.send(id);
    });
    app.post('/', (req, res) => {
      // process post request
      console.log(req.body)
      res.send('post request working...')
    });
  };