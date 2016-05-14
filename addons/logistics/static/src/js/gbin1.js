$(function(){
//    for(var loop= 1;loop++;loop<10){
//        var data=$("body",parent.document).find("input[name='images"+loop+"']").val();
//        if(data!=''){
//           $( "#pictures" ).append( '<img src="' + data + '" >');
//        }
//
//    }

    var index=1;
	$('#webcam').photobooth().on("image",function( event, dataUrl ){
		$('.nopic').hide();
        var lts=$("body",parent.document).find("input[name='images"+index+"']").length;
        //alert(lts);
        $("body",parent.document).find("input[name='images"+(index++)+"']").val(dataUrl);

        alert($("body",parent.document).find("input[name='images"+(index++)+"']").val());
		$( "#pictures" ).append( '<img src="' + dataUrl + '" >');
	});

	if(!$('#webcam').data('photobooth').isSupported){
		alert('HTML5 webcam is not supported by your browser, please use latest firefox, opera or chrome!');
	}

	$('.photobooth ul li:last').qtip({
		content: {
			text: '点此照相',
			title: {
				text: 'Tips',
				button: true
			}
		},
		show: {
			ready: false
		},
		position: {
			target: 'event',
	      	my: 'left center',
	      	at: 'right center'
		},
		style: {
			classes: 'ui-tooltip-shadow ui-tooltip-bootstrap',
			width: 300
		}
	});

	$('#site').qtip({
		content: {
			text: '',
			title: {
				text: 'wlecome',
				button: true
			}
		},
		position: {
			target: 'event',
	      	my: 'bottom center',
	      	at: 'top center',
			viewport: $(window)
		},
		style: {
			classes: 'ui-tooltip-shadow ui-tooltip-jtools'
		}
	});
});