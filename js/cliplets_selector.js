// Compare erroor field on image click
var function_letter_clickAndHide = function(){
  var SELECTION_COLOR = 'cc0000';

    $(".correction_letter").hide();
    $(".show_hide").show();

    $('.show_hide').click(function() {

        var isvisible = $(this).next('.correction_letter').is(':visible');
        var isCtrl = window.event.ctrlKey;
        var is_selected = $(this).hasClass("selected_letter");

        selected_id = $(this).attr('id')

        if (is_selected) { 
          if (isCtrl){
            selected_list = $('#selected_bb_image_id').attr('value')
            selected_list = selected_list.replace(selected_id, "")
            selected_list = selected_list.replace(",,", ",")
            selected_list = selected_list.replace(/^,|,$/g, '');
            if(selected_list == ""){
              selected_list = "None"
            }

            $('#selected_bb_image_id').val(selected_list);

          }
          else{
            $(this).parent().siblings().children('a').removeClass("selected_letter"); 
            if(isvisible){
              $(this).next('.correction_letter').slideToggle();
            }
            $('#selected_bb_image_id').val("None");
          }
          $(this).removeClass("selected_letter"); 
          $('#current_bb_image_id').val("None");
          $('#current_selected').html("");

        }
        else{
          if (isCtrl){
            // append to #selected_bb_image_id
            selected_list = $('#selected_bb_image_id').attr('value')
            if (selected_list=="None"){
              selected_list = selected_id;
            }
            else{
              selected_list = selected_list + "," + selected_id;
            }
            $('#selected_bb_image_id').val(selected_list);
          }
          else{
            $(this).parent().siblings().children('a').removeClass("selected_letter"); 
            $(this).next('.correction_letter').slideToggle();
            $('#selected_bb_image_id').val(selected_id);
          }
          //$(this).find('img').addClass("selected_letter");
          $(this).addClass("selected_letter");
          $('#current_bb_image_id').val(selected_id);
          $('#current_selected').html("Annotation ID:"+selected_id.split("_")[2]);

        }
        
        $(this).parent().siblings().children('.correction_letter').hide();
        
    });
  };

$(document).ready(function_letter_clickAndHide);