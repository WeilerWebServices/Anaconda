# Various utilities for working with code
_ = require "underscore"
fs = require "fs"
gulp = require "gulp"
path = require "path"
defaults = require "./defaults"

scriptFilter = (name) ->
  /(\.(js|coffee)$)/i.test(path.extname(name))


copySourceToTaskName = (source) ->
  "copy:#{source}"

# Function for generating simple tasks for copying files around
simpleCopyTask = (source, options) ->
  name = copySourceToTaskName source
  gulp.task name, ->
    gulp.src options.src
      .pipe gulp.dest options.destination

loadTasks = (dir) ->
  tasks = fs.readdirSync(dir).filter scriptFilter
  [path: "#{dir}#{task}", name: path.basename task, task.slice(task.lastIndexOf ".") for task in tasks]

module.exports =
  copySourceToTaskName: copySourceToTaskName
  loadTasks: loadTasks
  scriptFilter: scriptFilter
  simpleCopyTask: simpleCopyTask
