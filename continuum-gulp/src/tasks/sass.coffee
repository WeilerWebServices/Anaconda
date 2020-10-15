_ = require "underscore"
gulp = require "gulp"
livereload = require "gulp-livereload"
sass = require "gulp-sass"
defaults = require "../defaults"

module.exports = (options={}) ->
	options = _.extend defaults, options
	gulp.task "sass", ->
	  gulp.src options.src
	    .pipe sass()
	    .pipe gulp.dest(options.destination)
	    .pipe livereload auto: false
