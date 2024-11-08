// controll the box "all" in the category selector
var select_all_categories = function(){
    let all_cbox = document.getElementById("all_cat_in_full_img");
    var checked = all_cbox.checked

    let cboxes_container = document.getElementById("checkboxes_full_img");

    var nodes = document.getElementById('checkboxes_full_img').childNodes;
    var nodes = document.querySelectorAll('#checkboxes_full_img label input')

    for(var i=0; i<nodes.length; i++) {
        if(nodes[i].id != 'all_cat_in_full_img'){
            nodes[i].click();
            // nodes[i].checked = checked;
        }
    }
};