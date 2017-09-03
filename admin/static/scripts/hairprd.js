$(function() {
    // tab swap when clicked
    $('.tab').on('click', function(e) {
        var swapto = $(this).attr('swapto');

        // tab change
        $('.tab').removeClass('on');
        $(this).addClass('on');

        // body change
        $('.prd_body').hide();
        $('.prd_body[name="'+swapto+'"]').show();

        e.preventDefault();
    });

    // info popup
    $('.prd_body table.detail a').on('click', function(e) {
        // open comp info popup
        popupSwap('comp');
        popupToggle();

        e.preventDefault();
    });

    // review popup
    $('.prd_header .btn_review').on('click', function(e) {
        // open review popup
        popupSwap('review');
        popupToggle();

        e.preventDefault();
    });
});