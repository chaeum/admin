function popupSwap(type) {
    $('.popup_frame > div[class*="popup_"]').hide();
    $('.popup_frame > div[class="popup_'+type+'"]').show();

    if(type == 'sign_up') {
        multiPopupSwap('account');
    } else{
        multiPopupSwap();
    }
}

function multiPopupSwap(type) {
    if(type == undefined) {
        $('.popup_frame .popup_multi').show();
    } else {
        $('.popup_frame .popup_multi').hide();
        $('.popup_frame .popup_multi.'+type).show();
    }
}

function popupToggle() {
    $('.bg_popup').height($('body').height());
    $('.bg_popup').fadeToggle();

    var screenWidth = $(window).width();
    var left = (screenWidth - $('.popup_frame').width()) / 2;
    $('.popup_frame').css('left', left/16.0+'em');
    $('.popup_frame').fadeToggle();
}

$(function() {
    // popup close
    $('.popup_frame .close, .bg_popup').on('click', function(e) {
        popupToggle();
        e.preventDefault();
    });

    // popup swap
    $('.popup_frame button[type="popup_swap"]').on('click', function(e) {
        popupSwap($(this).attr('swapto'));
        e.preventDefault();
    });

    // popup body swap
    $('.popup_frame button[type="popup_body_swap"]').on('click', function(e) {
        multiPopupSwap($(this).attr('swapto'));
        e.preventDefault();
    });

    // review score handling
    var reviewScore = 3;
    $('.popup_frame .popup_review .icon_review_score').on('click', function(e) {
        var score = parseInt($(this).attr('value'));
        reviewScore = score;

        $('.popup_frame .popup_review .icon_review_score').each(function(index) {
            var curScore = parseInt($(this).attr('value'));
            if(curScore <= score) {
                $(this).removeClass('off');
            } else {
                $(this).addClass('off');
            }
        });
    });
});