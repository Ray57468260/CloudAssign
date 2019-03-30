
var order = $(".order.green").find("a").attr("value");//刷新后默认排序策略
var csrftoken = $.cookie("csrftoken");

function loadInner(sId, order){
    var sId = window.location.hash;
	var url, i;
	switch(sId){
		case "#fresh": url = "fresh/"; i = 0; break;
		case "#reviewed": url = "reviewed/"; i = 1; break;
		case "#rejected": url = "rejected/"; i = 2; break;
		default: url = "fresh/"; i = 0; break;
	}
	$("#tab-content").load(url, {'csrfmiddlewaretoken': csrftoken, 'order': order});//加载相对应的内容
	$(".tab-menu li").eq(i).addClass("active").siblings().removeClass("active");
};

//排序策略改变触发
$(function(){
	$(".order-select").on("click", "span", function(){
		var order = $(".order.green").find("a").attr("value");//获取排序策略
		var sId = $(".class.active").data("id");//获取data-id的值
		loadInner(sId, order);
	});
});

//分类改变触发
$(function(){
	$(".tab-menu").on("click", "li", function(){
		var sId = $(this).data("id");//获取data-id的值
		var order = $(".order.green").find("a").attr("value");//获取排序策略
        window.location.hash = sId;  //设置锚点
		loadInner(sId, order);
	});

	var sId = window.location.hash;
	loadInner(sId, order);
});