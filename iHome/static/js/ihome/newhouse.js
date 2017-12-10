function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    // $('.popup_con').fadeIn('fast');
    // $('.popup_con').fadeOut('fast');

    // 在页面加载完毕之后获取区域信息
    $.get('/api/v1.0/areas',function (resp) {
        if(resp.errno=="0"){
            // $("#areas-tmpl").
            for(var i=0; i<resp.data.length;i++){
                //<option value="{{area.aid}}">{{area.aname}}</option>
                // var areaId = resp.data[i].aid
                // var areaName = resp.data[i].aname
                // $("#area-id").append('<option value= " '+areaId+' ">'+areaName+'</option>')
                var html = template("areas-tmpl",{"areas":resp.data})
                $("#area-id").html(html)
            }
        }else{
            alert(resp.errmsg)
        }


    })


    // TODO: 处理房屋基本信息提交的表单数据

    // TODO: 处理图片表单的数据

})