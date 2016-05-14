
var iTime = 200;
	var Account;
	function RemainTime(){
		document.getElementById('zphone').disabled = true;
		var iSecond,sSecond="",sTime="";
		if (iTime >= 0){
			iSecond = parseInt(iTime%60);
			iMinute = parseInt(iTime/60)
			if (iSecond >= 0){
				if(iMinute>0){
					sSecond = iMinute + "分" + iSecond + "秒";
				}else{
					sSecond = iSecond + "m";
				}
			}
			sTime=sSecond;
			if(iTime==0){
				clearTimeout(Account);
				sTime='重新发送';
				iTime = 200;
				document.getElementById('zphone').disabled = false;
			}else{
				Account = setTimeout("RemainTime()",1000);
				iTime=iTime-1;
			}
		}else{
			sTime='发送验证码';
		}
		document.getElementById('zphone').innerText = sTime;
	}


$(function(){
    $('.ui-icon-close').click(function(){
        //alert('123');
        $(this).sibling('inupt').val('');
    })
    //发送验证码
    $(".verify").click(function(event){
        var mobile=$('.phone').val();
        if(!/^(0|86|17951)?(13[0-9]|15[012356789]|18[0-9]|14[57]|17[0-9])[0-9]{8}$/.test(mobile)){
                    var el=$.tips({
                        content:'请输入正确手机号',
                        stayTime:2000,
                        type:"success"
                    })
                    el.on("tips:hide",function(){
                        console.log("tips hide");
                    })
            return false;
         }



        $.get('/website/sms/verifycode?mobile='+mobile,function(data){
           RemainTime();
        })
    })

       $("#dialogButton0").live('click',function(){
           $('.ui-dialog').hide();
       })
    $("#dialogButton1").live('click',function(){
           $('.ui-dialog').hide();
       })
    //验证码验证
    $(".submit").click(function(event){
         var mobile=$('.phone').val();
         if(!/^(0|86|17951)?(13[0-9]|15[012356789]|18[0-9]|14[57]|17[0-9])[0-9]{8}$/.test(mobile)){
                    var el=$.tips({
                        content:'请输入正确手机号',
                        stayTime:2000,
                        type:"warn"
                    })
                    el.on("tips:hide",function(){
                        console.log("tips hide");
                    })
            return false;
         }

        var veryfy=$(".veryfy").val();
        if(veryfy.length<1){
            return false;
        }
        $.post('/wx_veryfy',{'veryfy':veryfy,'phone':mobile},function(data){
            var data1=eval("("+data+")");
            if(data1.code==1){
                var dia=$.dialog({
			        title:'',
			        content:'绑定成功',
			        button:["确认","取消"]
			    });
			    dia.on("dialog:action",function(e){
                    dia.hide();
			        console.log(e.index)
			    });
			    dia.on("dialog:hide",function(e){
                    dia.hide();
			        console.log("dialog hide")
			    });
            }else{
                var el=$.tips({
                        content:'验证失败，请输入正确手机号和验证码',
                        stayTime:3000,
                        type:"warn"
                    })
                    el.on("tips:hide",function(){
                        console.log("tips hide");
                    })
            }

        })
        event.preventDefault;
    })
})