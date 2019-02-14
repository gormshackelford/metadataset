$(document).ready(function(){

  <!-- Collapsible classification tree (Django MPTT recursetree) -->

  <!-- Show level 1 of the classification on page load -->
  $("ul.root").children().show(500);
  $("ul.root").children("li").children("span").text("---");

  <!-- Toggle the next level in the classification tree -->
  $(".toggle").click(function(){
    $(this).parent().next().toggle(500);
    <!-- Change from "+++" to "---" when toggling -->
    if ($(this).text() == "+++") {
      $(this).text("---");
    } else {
      $(this).text("+++");
    }
  });
  $(".toggle").hover(function(){
    $(this).css("cursor", "pointer");
  });

  <!-- Show all levels in the classification tree -->
  $(".show_all").click(function(){
    $("ul.children").show(250);
    $(".toggle").text("---");
  });
  $(".show_all").hover(function(){
    $(this).css("cursor", "pointer");
  });

  <!-- Hide all levels in the classification tree -->
  $(".hide_all").click(function(){
    $("ul.children").hide(250);
    $(".toggle").text("+++");
  });
  $(".hide_all").hover(function(){
    $(this).css("cursor", "pointer");
  });

});
