$(function() {
    // navigation bar on from current page urls
    $('header nav .sub_menu_wrap div').each(function(index) {
        var from = $(this).attr('from');
        var currentUrl = window.location.href;
        if (currentUrl.indexOf(from) >= 0) {
            $(this).addClass('on');
        }
    });

    // sub navigation bar on/off slide
    $('header nav .sub_menu_wrap').click(function() {
        $('header subnav').slideToggle();
    });

    // search focus in/out
    $('header .top .search input').focusin(function() {
        // focus in
        $('header .top .search').css('border-color', '#ff531d');
        $('header .top .search .auto_comp').toggle();
    }).focusout(function() {
        // focus out
        $('header .top .search').css('border-color', '#563540');
        $('header .top .search .auto_comp').toggle();
    });

    // top sign in button
    $('#top_sign_in').on('click', function(e) {
        popupSwap('sign_in');
        popupToggle();
        e.preventDefault();
    });

    // top sign up button
    $('#top_sign_up').on('click', function(e) {
        popupSwap('sign_up');
        popupToggle();
        e.preventDefault();
    });

    // select box initialize
    $('select').simpleselect();
});
