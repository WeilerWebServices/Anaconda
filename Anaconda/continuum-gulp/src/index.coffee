_ = require "underscore"
gulp = require "gulp"
taskList = require "gulp-task-listing"
utils = require "./utils"
defaults = require "./defaults"

registerAllTasks = (options) ->
  options = _.extend defaults, options
  for dir in options.taskDirectories
    for tasks in utils.loadTasks dir
      for task in tasks
        require(task.path) options[task.name] || {}

  gulp.task "help", taskList

module.exports =
  registerAllTasks: registerAllTasks
