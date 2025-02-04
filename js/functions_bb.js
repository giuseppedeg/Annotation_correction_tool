document.add_new = false;

function add_bb(){
    if ((typeof document.add_new == 'undefined') || !document.add_new){
        document.add_new = true;
        document.getElementById('new-bb-func-btn').style.backgroundColor = "#00be27";
    }
    else{
        document.add_new = false;
        document.getElementById('new-bb-func-btn').style.backgroundColor = "transparent";
    };
};
