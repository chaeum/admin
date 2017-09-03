

/* fit image width from screen size */
function set_body_width() {
    $('banner img').width($('body').width());
    $('banner').height($('banner img').height());
}

$(function() {
    $(window).bind('resize', set_body_width);
    set_body_width();
});
