_ = require "underscore"
gulp = require "gulp"
gutil = require "gulp-util"
{spawn} = require "child_process"
psTree = require "ps-tree"
defaults = require "./defaults"
psTree = require "ps-tree"

createServer = (options={}) ->
  options = _.extend defaults, options.flask

  prefix = gutil.colors.cyan "flask:"
  serverOutput = (data) ->
    data.replace /\s*$/, ""
      .split("\n")
      .forEach (line) ->
        gutil.log "#{prefix} #{gutil.colors.grey line}"

  server = spawn "python", ["server.py", ]
  server.stdout.setEncoding "utf8"
  server.stdout.on "data", serverOutput

  server.stderr.setEncoding "utf8"
  server.stderr.on "data", serverOutput

  server.on "error", ->
    gutil.log "huh?"
  server.onUnexpectedExit = (code, signal) ->
    gutil.log gutil.colors.red "flask server has stopped with: #{code}"
    process.exit 1

  server.on "exit", server.onUnexpectedExit

  server.shutdown = (cb) ->
    gutil.log gutil.colors.red "flask shutdown initiated"
    @removeListener "exit", @onUnexpectedExit
    psTree server.pid, (err, children) ->
      kill = spawn('kill', ['-9'].concat(children.map (p) -> p.PID))
      kill.on "exit", ->
        server.kill "SIGTERM"
        cb() if cb?
  server

module.exports =
  createServer: createServer
