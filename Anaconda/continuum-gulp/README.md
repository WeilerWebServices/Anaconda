# continuum-gulp
[Continuum Analytics'][cio] internal gulp utilities.

This is a collection of utilities for creating and working with [gulp.js][]
files internally at [Continuum][cio].  This is provided under a BSD license in
the hope that it might be useful as a starting point for someone else, but is
meant solely as an internal tool.


## Installation and Configuration

These instructions assume you are using `conda`.  First, install `node`:

    conda install -c javascript nodejs

Next, if you don't already have a `package.json` in your repository, create that
using `npm init` and follow the directions.  After you have a valid
`package.json` file created, add `continuum-gulp` with this command:

    npm install --save gulp continuum-gulp

Note: it's *important* that you install your own version of `gulp` in order for
the tasks to be recongized.

Next, you need to create a `gulpfile.js` file.  All you need to do is add the
following to the file:

```javascript
require("continuum-gulp").registerAllTasks();
```

You can let continuum-gulp do this for you with the following command:

    npm run-script continuum-gulp init


## Usage
Once installed, you can run `gulp help` to see a list of all of the tasks
that are registered and available:

    $ gulp help
    [14:07:09] Using gulpfile ~/work/some-site/gulpfile.js
    [14:07:09] Starting 'help'...

    Main Tasks
    ------------------------------
        build
        clean
        copy
        default
        help
        sass
        scripts
        templates

    Sub Tasks
    ------------------------------
        copy:bower
        copy:fonts
        copy:html
        copy:images

For normal usage, you simply need to run `gulp` which compiles all of your
assets via the `gulp build`, then starts a flask server.

[cio]: http://continuum.io
[gulp.js]: http://gulpjs.com
