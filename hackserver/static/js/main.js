function scrollBlur(blur) {
	var blur = ".scroll-blur";

	var r = $(blur),
		wh = $(window).height(),
		dt = $(document).scrollTop(),
		elView, opacity;

	// Loop elements with class "blurred"
	r.each(function() {
		// console.log('dt: '+dt + "   wh: "+wh);
		// console.log($(this).offset());

	 	var outside = (dt - $(this).offset().top);

	 	var blurMinHeight = $(this).height() * 0.2;
	 	var blurMaxHeight = $(this).height() * 0.5;
		if (outside > blurMinHeight && outside < blurMaxHeight) {
			opacity = (outside - blurMinHeight) / (blurMaxHeight - blurMinHeight);
			// console.log("opacity " + opacity);
			$(this).css('opacity', opacity);
			// console.log('prev'+$(this).prev().css('opacity', 1-opacity));
		}

		/*

		if (elView > 0) { // Top of DIV above bottom of window.
			opacity = 1 / (wh + $(this).height()) * elView * 2
			if (opacity < 1) { // Bottom of DIV below top of window.
				$(this).css('opacity', opacity);
			}
		}*/
	});
}

$(window).load(function() {
	new WOW().init();
	
	smoothScroll.init({
        speed: 500, // Integer. How fast to complete the scroll in milliseconds
        easing: 'easeInOutQuart', // Easing pattern to use
        updateURL: true, // Boolean. Whether or not to update the URL with the anchor hash on scroll
        offset: 0, // Integer. How far to offset the scrolling anchor location in pixels
        callbackBefore: function ( toggle, anchor ) {}, // Function to run before scrolling
        callbackAfter: function ( toggle, anchor ) {
            $('menu').attr('data-section', anchor.substring(1));
        } // Function to run after scrolling
    });

	// init menu behavior
    var sections = ['landing', 'about', 'schedule', 'location', 'divisions', 'register'];
    for (var i = 0; i < sections.length; i++) {
        (function(cur){
            $('#' + sections[cur]).waypoint(function(direction) {
                if (cur > 0 && direction == 'up')
                    $('menu').attr('data-section', sections[cur - 1]);
                else
                    $('menu').attr('data-section', sections[cur]);
            }, { offset: 0 });
        })(i);
    }

	$(document).bind('scroll', scrollBlur);
});
