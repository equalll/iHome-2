function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}


function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    // DO: 查询用户的实名认证信息
    $.get("/api/v1.0/user/auth",function (resp) {
        if (resp.errno=="0"){
            if(resp.data.real_name && resp.data.id_card){
                $("#real-name").val(resp.data.real_name)
                $("#id-card").val(resp.data.id_card)
                // 吧输入框设置为不可点击
                $("#real-name").prop("disabled",true)
                $("#id-card").prop("disabled",true)
                //  shezhi  yincang baocun
                $(".btn").hide()
            }
        }
        else if(resp.errno=="4101"){
            location.href="/login.html"
        }
        else{
            alert(resp.errmsg)
        }
    })
    // DO: 管理实名信息表单的提交行为

    $("#form-auth").submit(function (e) {
        e.preventDefault()

        var real_name=$("#real-name").val()
        var id_card = $("#id-card").val()
        if(! (real_name && id_card)){
            $(".error-msg").show()
        }
        $(".error-msg").hide()

        var params={
            "real_name":real_name,
            "id_card":id_card
        }
        $.ajax({
            url:"/api/v1.0/user/auth",
            type:"post",
            contentType:"application/json",
            headers:{
                "X-CSRFToken":getCookie("csrf_token")
            },
            data:JSON.stringify(params),
            success:function (resp) {
                if(resp.errno=="0"){
                $("#real-name").val(resp.data.real_name)
                $("#id-card").val(resp.data.id_card)
                // 吧输入框设置为不可点击
                $("#real_name").pop("disabled",true)
                $("#id-card").pop("disabled",true)
                $(".error-msg").hide()
                }else if(resp.errno=="4101"){
                    location.href("/login.html")
                }else{
                    alert(resp.errmsg)
                }

            }

        })

    })


})