function deleteNote(noteId) {
  fetch("/delete-note", {
    method: "POST",
    body: JSON.stringify({ noteId: noteId }),
  }).then((_res) => {
    window.location.href = "/wishlist";
  });
}

const body = document.querySelector('body');
const toggle_button = document.getElementById("toggle-button");
toggle_button.onclick = function(){
  toggle_button.classList.toggle('active');
  body.classList.toggle('active');

}


//table transactions
$('table').DataTable();

let alerts = document.querySelectorAll('.success')



setTimeout(function() {
  $('.success').fadeOut('fast');
}, 30000); // <-- time in milliseconds


window.setTimeout("document.querySelectorAll('.success').style.display='none';", 2000)