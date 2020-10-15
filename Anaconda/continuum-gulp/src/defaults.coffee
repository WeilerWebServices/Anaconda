module.exports =
  taskDirectories: [
    "#{__dirname}/tasks/",
  ]

  watch:
    watch: [
      {glob: "./static/coffee/**/*.*", tasks: ["scripts", ]}
      {glob: "./static/scss/**/*.scss", tasks: ["sass", ]}
    ]

  build:
    tasks: ["copy", "sass", "scripts", "templates"]

  clean:
    dirs: ["build", ]

  templates:
    prefix: "static/templates/"
    src: "./static/templates/**/*.*"
    filename: "templates.js"
    destination: "./build/js/"

  copy:
    sources: [
      "html", "bower", "fonts", "images",
    ]

  html:
    src: "static/**/*.html"
    destination: "build/"

  bower:
    path: "bower_components"
    src: "bower_components/**"
    destination: "build/bower_components"

  fonts:
    src: "static/fonts/**/*.*"
    destination: "build/fonts/"

  images:
    src: "static/images/**/*.*"
    destination: "build/images/"

  sass:
    src: "static/scss/*.scss"
    watch: "static/scss/**/*.scss"
    destination: "build/css"

  scripts:
    filename: "app.js"
    destination: "build/js"
    entries: ["./static/coffee/app.coffee", ]
    extensions: ['.coffee', ]
    paths: [
      './node_modules',
      './static/coffee',
    ]
    debug: yes  # get this running based on env

