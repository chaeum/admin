$(function() {
    var query = $('.content .result .text .h1').text();
    var highlight = $('<span>');
    highlight.addClass('ac2');
    highlight.text(query);
    $('.content .result .info .name').each(function(idx) {
        var origin = $(this).text();
        var replaced = origin.replace(query, highlight.clone().wrap('<p>').parent().html());
        $(this).html(replaced);
    });
});