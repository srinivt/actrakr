function updateItem(id) {
  $.post("/", { 
    'id' : id, 
    'status' : 1 
  }, function(data) { 
    window.location.pathname = '/';
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