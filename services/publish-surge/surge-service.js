const os             = require("os");
const express        = require('express');
const formData       = require("express-form-data");

const app            = express();
const port           = 8001;

const options = {
    uploadDir: os.tmpdir(),
    autoClean: true
  };
   
// parse data with connect-multiparty. 
app.use(formData.parse(options));
// clear from the request and delete all empty files (size == 0)
app.use(formData.format());
// change file objects to stream.Readable 
app.use(formData.stream());
// union body and files
app.use(formData.union());

require('./app/routes')(app, {});
app.listen(port, () => {
  console.log('express server is live on :' + port);
});