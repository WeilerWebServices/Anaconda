// Generated by CoffeeScript 1.4.0
(function() {
  var Module, Stitch, compilers, flatten, fs, modulerize, npath, _;

  npath = require('path');

  fs = require('fs');

  compilers = require('./compilers');

  modulerize = require('./resolve').modulerize;

  flatten = require('./utils').flatten;

  _ = require('underscore');

  Stitch = (function() {

    Stitch.prototype.ignores = [/.*~/, /^#/, /^\./i, /^.*.sw.?/];

    function Stitch(paths) {
      var path;
      this.paths = paths != null ? paths : [];
      this.paths = (function() {
        var _i, _len, _ref, _results;
        _ref = this.paths;
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          path = _ref[_i];
          _results.push(npath.resolve(path));
        }
        return _results;
      }).call(this);
    }

    Stitch.prototype.resolve = function() {
      var path;
      return flatten((function() {
        var _i, _len, _ref, _results;
        _ref = this.paths;
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          path = _ref[_i];
          _results.push(this.walk(path));
        }
        return _results;
      }).call(this));
    };

    Stitch.prototype.resolveFiles = function(parent) {
      var child, module, path, result, _i, _len, _ref;
      result = [];
      _ref = this.paths;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        path = _ref[_i];
        console.log("building", path);
        if (fs.existsSync(path + '.coffee')) {
          child = path + '.coffee';
        } else if (fs.existsSync(path + '.eco')) {
          child = path + '.eco';
        }
        module = new Module(child, parent);
        if (module.valid()) {
          result.push(module);
        }
      }
      return result;
    };

    Stitch.prototype.walk = function(path, parent, result) {
      var child, module, stat, _i, _len, _ref;
      if (parent == null) {
        parent = path;
      }
      if (result == null) {
        result = [];
      }
      if (!fs.existsSync(path)) {
        return;
      }
      _ref = fs.readdirSync(path);
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        child = _ref[_i];
        if (_.any(_.map(this.ignores, function(ignore) {
          return child.match(ignore);
        }))) {
          continue;
        }
        child = npath.join(path, child);
        stat = fs.statSync(child);
        if (stat.isDirectory()) {
          this.walk(child, parent, result);
        } else {
          module = new Module(child, parent);
          if (module.valid()) {
            result.push(module);
          }
        }
      }
      return result;
    };

    return Stitch;

  })();

  Module = (function() {

    function Module(filename, parent) {
      this.filename = filename;
      this.parent = parent;
      this.ext = npath.extname(this.filename).slice(1);
      this.id = modulerize(this.filename.replace(npath.join(this.parent, npath.sep), ''));
    }

    Module.prototype.compile = function() {
      return compilers[this.ext](this.filename);
    };

    Module.prototype.valid = function() {
      return !!compilers[this.ext];
    };

    return Module;

  })();

  module.exports = Stitch;

}).call(this);