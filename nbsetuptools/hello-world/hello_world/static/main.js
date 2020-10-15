define(['jquery'], function ($) {

    var readHello = function() {
        $.getJSON('/hello', function(data) {
            console.log(data);
        });
    }

    var load_ipython_extension = function () {
        readHello();
    };

    return {
        load_ipython_extension : load_ipython_extension,
    };
});
