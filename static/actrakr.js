function updateItem(check, id) {
	if (!check.checked) {
		return;
	}
	$("#item-name-" + id).css('text-decoration', 'line-through');
  $.post("/", { 
    'id' : id, 
    'status' : 1 
  }, function(data) { 
    window.location.href = '/';
  });
}

function deleteListItem(id) {
  item_text = $('#list_' + id + '>span').text();
  if (confirm("Delete '" + item_text + "'?")) { 
    $.post("/delete", { 
      'id' : id
    }, function(data) { 
      window.location.href = '/';
    });
  }
}
