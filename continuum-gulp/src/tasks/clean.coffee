_ = require "underscore"
gulp = require "gulp"
del = require "del"
vinylPaths = require "vinyl-paths"
defaults = require "../defaults"

module.exports = (options={}) ->
	options = _.extend defaults.clean, options
	gulp.task "clean", ->
		for dir in options.dirs || []
	    gulp.src dir
	      .pipe vinylPaths del
