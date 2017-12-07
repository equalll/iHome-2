function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

// 点击推出按钮时执行的函数
function logout() {
    $.ajax({
        url: "/api/v1.0/session",
        method: "delete",
        headers: {
            "X-CSRFToken": getCookie('csrf_token')
        },
        success: function (resp) {
            location.href = "/index.html"
        }
    })
}

$(document).ready(function(){

    // 在页面加载完毕之后去加载个人信息
    $.get("/api/v1.0/users", function (resp) {
        if (resp.errno == "0") {
            $("#user-name").html(resp.data.name)
            $("#user-mobile").html(resp.data.mobile)
            if (!resp.data.avatar) {
                $("#user-avatar").attr('src', resp.data.avatar)
            }
        }else if (resp.errno == "4101"){
            location.href = "/index.html"
        }
    })

});
