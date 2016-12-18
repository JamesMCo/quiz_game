function init_player() {
  if ($("#playername").val() !== "") {
    $.ajax({
      url: "/init?name=" + $("#playername").val(),
      type: "GET",
      success: function(data) {
        window.location = "/next?uuid=" + data
      }
    })
  }
}

function get_answer(uuid, chosen) {
  $.ajax({
    url: "/ans?uuid=" + uuid,
    type: "GET",
    success: function(data) {
      $("a.btn-large").removeAttr("onclick")
      $("a.btn-large").css("background-color", "#F44336")
      $("a.btn-large:contains('" + data + "')").css("background-color", "#4CAF50")
      if (chosen == data) {
        $.get("/correct?uuid=" + uuid)
      }
      $(".card-content").append("<a class='waves-effect waves-light btn-large' onclick='location.reload()'>Next <i class='material-icons right'>send</i></a>")
    }
  })
}

function delete_player(uuid) {
  $.get("delete?uuid=" + uuid)
  $("#" + uuid).fadeOut(350, function(){$("#" + uuid).remove()})
}

function namekeypress(event) {
  if (event.keyCode == 13) {
    $("#enterbutton").click();
  }
}
