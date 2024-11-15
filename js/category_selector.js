// controll the box "all" in the category selector
var select_all_categories = function(){
    let all_checked = document.getElementById('all_cat_in_full_img').checked;
    var nodes = document.querySelectorAll('#checkboxes_full_img label input');

    for(var i=0; i<nodes.length; i++) {
        if(nodes[i].id != 'all_cat_in_full_img'){
            if(nodes[i].checked != all_checked){
                nodes[i].click();
            }
        }
    }
};