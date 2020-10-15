_ = require "underscore"
gulp = require "gulp"
concat = require "gulp-concat"
nunjucks = require "nunjucks"
map = require "vinyl-map"

defaults = require "../defaults"

env = new nunjucks.Environment()

module.exports = (options={}) ->
  options = _.extend {}, defaults, options

  gulp.task "templates", ->
    prefix = options.templates.prefix
    compileTemplate = map (a, filename) ->
      opts =
        env: env
        name: filename.slice(filename.indexOf(prefix) + prefix.length)
      console.log "compiling #{opts.name}"
      nunjucks.precompile filename, opts

    gulp.src options.templates.src
      .pipe compileTemplate
      .pipe concat options.templates.filename
      .pipe gulp.dest options.templates.destination
