var isDrawerOpen = false;
function openNav() {
  if(!isDrawerOpen) {
      document.getElementById("mySidenav").style.width = "250px";
      $('.navoverlay').addClass('active');
      isDrawerOpen = true;
  }
  else {
    closeNav();
  }
}

function closeNav() {
  document.getElementById("mySidenav").style.width = "0";
  $('.navoverlay').removeClass('active');
  isDrawerOpen = false;
}

function toggle(id) {
    $('#'+id).toggle();
}
