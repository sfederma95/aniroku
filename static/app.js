$('#add-anime').on('click', function() {
	$('.waitpage').show();
});

$('.genre').on('click', function() {
	$('.waitpage').show();
});

$('#search').on('click', function() {
	$('.waitpage').show();
});

$('.recommended').on('click', function() {
	$('.waitpage').show();
});

$('button.update-button').on('click', function() {
	$(this).siblings().attr('hidden', false);
	$(this).attr('hidden', true);
	for (i = 0; i < $('.listed-anime').length; i++) {
		$('.update-button,.i').attr('hidden', true);
	}
});

$('button.cancel-entry-update').on('click', function() {
	$(this).siblings().attr('hidden', true);
	$(this).attr('hidden', true);
	for (i = 0; i < $('.listed-anime').length; i++) {
		$('.update-button,.i').attr('hidden', false);
	}
});

function categorySelect() {
	// from https://stackoverflow.com/questions/2683794/jquery-selectors-where-item-does-not-have-children-with-a-certain-class
	let category = $(this).attr('id');
	let notCategory = $('.listed-anime').filter(function() {
		return !$(this).children().is(`.${category}`);
	});
	notCategory.attr('hidden', true);
	$(`.${category}`).parent().attr('hidden', false);
}

$('button.category-select').on('click', categorySelect);

$('button.comment-button').on('click', function() {
	$(this).siblings().attr('hidden', false);
	$(this).attr('hidden', true);
	for (i = 0; i < $('.listed-anime').length; i++) {
		$('.comment-button,.i').attr('hidden', true);
	}
});

$('button.cancel-comment').on('click', function() {
	$(this).siblings().attr('hidden', true);
	$(this).attr('hidden', true);
	for (i = 0; i < $('.listed-anime').length; i++) {
		$('.comment-button,.i').attr('hidden', false);
	}
});

$('#clear-filter').on('click', function() {
	$('.listed-anime').attr('hidden', false);
});

$('.spoiler-toggle').on('click', function() {
	$(this).next().toggleClass('spoiler');
});
