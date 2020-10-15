_ = require "underscore"
gulp = require "gulp"
defaults = require "../defaults"
utils = require "../utils"

module.exports = (options={}) ->
  options = _.extend defaults.copy, options
  tasks = []
  for source in options.sources
    utils.simpleCopyTask source, defaults[source]
    tasks.push utils.copySourceToTaskName source

  gulp.task "copy", tasks
