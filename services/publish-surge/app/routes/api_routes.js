module.exports = function(app, db) {

    app.get('/:id', (req, res) => {
        const id = req.params.id;
        // process get request
        res.send(id);
    });
    app.post('/', (req, res) => {
      // process post request with system call (to use surge)
      const util = require('util');
      const exec = util.promisify(require('child_process').exec);

      async function ls() {
          const { stdout, stderr } = await exec('ls ./tmp');
          console.log('stdout:', stdout);
          console.log('stderr:', stderr);
          res.send({"stdout": stdout})
        }
      ls();
    });
  };