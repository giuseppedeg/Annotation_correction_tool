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

var display_labels = function(){
    var label_checked = document.getElementById('labels_in_full_img').checked;
    var thisCSS=document.styleSheets[1]
    var ruleSearch=thisCSS.cssRules? thisCSS.cssRules: thisCSS.rules

    if (label_checked){
        newValue = "block";
    }
    else{
        newValue = "none";
    }

    for (i=0; i<ruleSearch.length; i++)
    {
        if(ruleSearch[i].selectorText==".leaflet-marker-icon")
        {
            var target=ruleSearch[i]
            break;
        }
    }
    target.style.setProperty("display", newValue, "important")
};