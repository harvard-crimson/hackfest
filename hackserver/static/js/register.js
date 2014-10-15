// From http://stackoverflow.com/questions/1184624/
$.fn.serializeObject = function() {
    var o = {};
    var a = this.serializeArray();
    $.each(a, function() {
        if (o[this.name] !== undefined) {
            if (!o[this.name].push) {
                o[this.name] = [o[this.name]];
            }
            o[this.name].push(this.value || '');
        }
        else {
            o[this.name] = this.value || '';
        }
    });
    return o;
};

function validate_form($form) {
    var valid = true;
    var required = ['gender', 'name', 'email', 'is_harvard', 'grad_year',
                    'size'];
    var is_harvard = $('#is_harvard').val();
    if (is_harvard == 'No') {
        required.push('host_email');
        required.push('uni');
    }
    else {
        $('#inviter').parents('.field').removeClass('empty');
    }
    
    for (var i = 0; i < required.length; i++) {
        var $elt = $('#' + required[i]);
        var val = $elt.val() == null ? '' : $elt.val();
        var $field = $elt.parents('.field');
        var is_wrong = val.length == 0;
        if (required[i] == 'email' || required[i] == 'host_email') {
            is_wrong = val.indexOf('@') < 0;
        }
        if (is_wrong) {
            $field.addClass('empty')
            valid = false;
        }
        else {
            $field.removeClass('empty');
        }
    }
    return valid;
}

function selectChanged(el, val) {
    if (el.id == 'is_harvard') {
        if (val == 'Yes') {
            $('#non-harvard-fields').slideUp();
        }
        else {
            $('#non-harvard-fields').slideDown();
        }
    }
}

$(document).ready(function(){
    $('#mainForm').submit(function(event){
        if (!validate_form($(this))) {
            event.preventDefault();
            var scroll_top = $('.field.empty').first().offset().top - 50;
            var curr_top = document.documentElement.scrollTop ||
                           document.body.scrollTop;
            var go_to = scroll_top < curr_top ? scroll_top : curr_top;
            $('html, body').stop().animate({
                scrollTop: scroll_top
            }, 400);
        }
        else {
            $(this).fadeOut().promise().done(function() {
                $('#success').fadeIn();
            });
            $('html, body').stop().animate({
                scrollTop: 0
            }, 400);
        }
    });

    (function() {
        [].slice.call( document.querySelectorAll( 'select.cs-select' ) ).forEach( function(el) {    
            new SelectFx(el, {
                onChange: function(val) {
                            selectChanged(el, val);
                          }
            });
        } );
    })();

    var $selects = $('.cs-select');
    var i = $selects.length;
    $selects.each(function() {
        $(this).css('z-index', parseInt($(this).css('z-index')) + i);
        i --;
    });

    $('input, select').change(function() {
        $(this).parents('.field').removeClass('empty');
    });
    $('.cs-select .cs-options ul li').click(function() {
        $(this).parents('.field').removeClass('empty');
    });
});
