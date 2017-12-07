function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function generateUUID() {
    var d = new Date().getTime();
    if(window.performance && typeof window.performance.now === "function"){
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
}
var imageCodeId = ""
var preImageCodeId = ""
// 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
function generateImageCode() {
    imageCodeId = generateUUID()
    var imageCodeUrl = "/api/v1.0/imagecode?cur=" + imageCodeId + "&pre=" + preImageCodeId
    $(".image-code>img").attr("src", imageCodeUrl)
    preImageCodeId = imageCodeId
}

function sendSMSCode() {
    // 校验参数，保证输入框有数据填写
    $(".phonecode-a").removeAttr("onclick");
    var mobile = $("#mobile").val();
    if (!mobile) {
        $("#mobile-err span").html("请填写正确的手机号！");
        $("#mobile-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    } 
    var imageCode = $("#imagecode").val();
    if (!imageCode) {
        $("#image-code-err span").html("请填写验证码！");
        $("#image-code-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    }

    // 通过ajax方式向后端接口发送请求，让后端发送短信验证码
    var params = {
        "mobile": mobile,
        "image_code": imageCode, // 用户填写的图片验证码
        "image_code_id": imageCodeId // 图片验证码的编号
    }
    $.ajax({
        url: "/api/v1.0/smscode",
        method: "post",
        data: JSON.stringify(params),
        contentType: "application/json",
        headers: {
            "X-CSRFToken": getCookie('csrf_token')
        },
        dataType: "json",
        success: function (resp){
            if (resp.errno == "0") {
                // 倒数 60 秒
                var num = 60
                // 计时器
                var t = setInterval(function () {
                    if (num == 1) {
                        // 清除计时器
                        clearInterval(t)
                        $(".phonecode-a").html("获取验证码")
                        $(".phonecode-a").attr('onClick', 'sendSMSCode();')
                    }else {
                        num -= 1
                        $(".phonecode-a").html(num+"秒")
                    }
                }, 1000, 60)
            }else {
                // 表示后端出现了错误，可以将错误信息展示到前端页面中
                $("#phone-code-err").html(resp.errmsg)
                $("#phone-code-err").show()
                // 将点击按钮的onclick事件函数恢复回去
                $(".phonecode-a").attr('onClick', 'sendSMSCode();')

                if (resp.errno == "4004" | resp.errno == "4002") {
                    generateImageCode()
                }
            }
        }
    })
    // $.get("/api/v1.0/smscode", params, function (resp) {
    //     if (resp.errno == "0") {
    //         // 倒数 60 秒
    //         var num = 60
    //         // 计时器
    //         var t = setInterval(function () {
    //             if (num == 1) {
    //                 // 清除计时器
    //                 clearInterval(t)
    //                 $(".phonecode-a").html("获取验证码")
    //                 $(".phonecode-a").attr('onClick', 'sendSMSCode();')
    //             }else {
    //                 num -= 1
    //                 $(".phonecode-a").html(num+"秒")
    //             }
    //         }, 1000, 60)
    //     }else {
    //         // 表示后端出现了错误，可以将错误信息展示到前端页面中
    //         $("#phone-code-err").html(resp.errmsg)
    //         $("#phone-code-err").show()
    //         // 将点击按钮的onclick事件函数恢复回去
    //         $(".phonecode-a").attr('onClick', 'sendSMSCode();')
    //
    //         if (resp.errno == "4004" | resp.errno == "4002") {
    //             generateImageCode()
    //         }
    //     }
    // })
}

$(document).ready(function() {
    generateImageCode();  // 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#imagecode").focus(function(){
        $("#image-code-err").hide();
    });
    $("#phonecode").focus(function(){
        $("#phone-code-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
        $("#password2-err").hide();
    });
    $("#password2").focus(function(){
        $("#password2-err").hide();
    });

    // 注册的提交(判断参数是否为空)
    $(".form-register").submit(function (e) {
        e.preventDefault()

        var mobile = $("#mobile").val()
        var phonecode = $("#phonecode").val()
        var password = $("#password").val()
        var password2 = $("#password2").val()

        if (!mobile) {
            $("#mobile-err span").html('请填写手机号')
            $("#mobile-err").show()
            return
        }
        if (!phonecode) {
            $("#phone-code-err span").html("请输入短信验证码")
            $("#phone-code-err").show()
            return
        }

        if (!password) {
            $("#password-err span").html("请输入密码")
            $("#password-err").show()
            return
        }
        if (password != password2) {
            $("#password2-err span").html("两次密码不一致")
            $("#password2-err").show()
            return
        }

        var params = {}
        $(".form-register").serializeArray().map(function (x) {
            params[x.name] = x.value
        })

        $.ajax({
            url: "/api/v1.0/users",
            method: "post",
            data: JSON.stringify(params),
            contentType: "application/json",
            headers: {
                "X-CSRFToken": getCookie('csrf_token')
            },
            success: function (resp) {
                if (resp.errno == "0") {
                    location.href = "/index.html"
                }else {
                    $("#password2-err span").html(resp.errmsg)
                    $("#password2-err").show()
                }
            }
        })
    })
})
