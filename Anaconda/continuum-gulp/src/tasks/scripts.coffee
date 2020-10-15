_ = require "underscore"
browserify = require "browserify"
source = require "vinyl-source-stream"
gulp = require "gulp"
defaults = require "../defaults"

module.exports = (options={}) ->
  options = _.extend defaults.scripts, options

  gulp.task "scripts", ->
    browserify options
      .bundle()
      .pipe source options.filename
      .pipe gulp.dest options.destination
