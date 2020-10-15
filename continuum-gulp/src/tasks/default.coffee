_ = require "underscore"
gulp = require "gulp"
gutil = require "gulp-util"
livereload = require "gulp-livereload"

defaults = require "../defaults"
flask = require "../flask"

module.exports = (options={}) ->
  options = _.extend defaults.watch, options

  gulp.task "default", ["build"], ->
    livereload.listen auto: true
    server = flask.createServer()

    options.watch.forEach (a) ->
      gulp.watch a.glob, a.tasks

    process.handleExit = ->
      gutil.log "calling server.shutodwn"
      server.shutdown

    process.once "exit", process.handleExit
    process.once "SIGTERM", process.exit
    process.once "SIGINT", process.exit

    process.once "uncaughtException", (e) ->
      if process.listeners("uncaughtException").length is 0
        process.removeListener "exit", process.handleExit
        server.shutdown ->
          throw e

