_ = require "underscore"
gulp = require "gulp"
defaults = require "../defaults"


module.exports = (options={}) ->
	options = _.extend {}, defaults.build, options
	gulp.task "build", options.tasks
