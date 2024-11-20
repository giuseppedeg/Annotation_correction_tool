
var load_imgViewer = function(zoom=0, x=0, y=0) {
	var $img = $("#full_image").imgViewer2({
	onReady: function() {
	  this.setZoom(zoom).panTo(x,y); // i valori di pan sono in percentuale! [0,1]
    },

	onClick: function( e, pos ) {
	  var imgpos = this.relposToImage(pos);

	  // set hidden values
	  $('#click_x').val(imgpos.x)
	  $('#click_y').val(imgpos.y)

	  // click - call pyscript
	  $('#click_full_img').trigger('click');

	}
  });
};


var set_zoom_and_position = function(zoom, x, y){
	$("#full_image").imgViewer2('setZoom', zoom);
	$("#full_image").imgViewer2('panTo', x, y);
};

var add_bbs_layer = function(bb_id, bb_list, label, color){
	bb_list = Array.from(bb_list);
	$("#full_image").imgViewer2('add_BBs', bb_id, bb_list, label, color);
}

var remove_bbs_layer = function(bb_id){
	$("#full_image").imgViewer2('remove_BBs', bb_id);
}


var test_imgViewer_interaction = function(arg){
	console.log("QUI");

	//Richiamare metodi del widjet imgViewer2
	$("#full_image").imgViewer2('test_in_imgv', "parametri");
	$("#full_image").imgViewer2('setZoom', "3");
};

