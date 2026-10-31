var debug = 1;
var ow_dates = [];
var rt_dates = [];
var ow_direct = true;
$(document).ready(function () {
$("input, textarea").placeholder();
$("#flts #ccc, #flts #orderCity").autocomplete("/app/tools/get-point.php", {
width: 300,
minChars: 3,
selectFirst: true,
formatItem: formatItem,
formatResult: formatResult,
noRecord: ''
});
function formatItem(row, i, n) {
return row[0] +' ' + row[1] + '';
}
function formatResult(row) {
return row[0];
}
$("#from1,#from2,#to1,#to2").autocomplete("/app/tools/get-point.php", {
width: 300,
minChars: 3,
//autoFill: true,
selectFirst: true,
formatItem: formatItem,
formatResult: formatResult,
noRecord: ''
});
$("#from1,#from2,#to1,#to2").result(function(){
if ($(this).val() != '') {
if ($("#from2").val() == '') {
$("#to2").val($("#from1").val());
$("#to2").change();
$("#from2").val($("#to1").val());
$("#from2").change();
$("#date1").focus();
}
}
});
$("#from1,#from2,#to1,#to2").on('change blur paste', function(){
$.post('/app/req-flight.php', $("#big-fly" ).serialize(), function(data) {
ow_dates = data.ow;
rt_dates = data.rt;
$('#date1').datepicker('update');
$('#date2').datepicker('update');
},"json")
});
$("#date1").on('click', function(){
ow_direct = true;
$('#date1').datepicker('update');
});
$("#date2").on('click', function(){
ow_direct = false;
$('#date2').datepicker('update');
});
$(".tablo").on("click", "a", function (e) {
e.preventDefault();
$("#from1, #to2").val($(this).data('from'));
$("#from2, #to1").val($(this).data('to'));
$("a[data-tab='tab-ch']").click();
$("#to2").change();
$('html, body').animate({ scrollTop: $('#tab-ch').position().top + 20 }, 'fast');
//$("#big-fly").submit();
$("#date1").focus();
});
$("#start-tab").on("click", "a", function (e) {
e.preventDefault();
$("#start-tab > li").removeClass('active');
if ($(this).data('tab') == 'tab-ch') {
$(this).parent().addClass('active');
$('#tab-ch').fadeIn();
$('#tab-reg').hide();
}
else
{
$(this).parent().addClass('active');
$('#tab-ch').hide();
$('#tab-reg').fadeIn();
}
});
$('#flts #flydate').datepicker({
language: "ru",
orientation: "bottom right",
autoclose: true,
todayHighlight: true,
format: "dd.mm.yyyy",
startDate: "today"
});
$('#flts #orderDate').datepicker({
language: "ru",
orientation: "bottom right",
autoclose: true,
todayHighlight: true,
format: "dd.mm.yyyy"
});
$('.daterange').datepicker({
language: "ru",
inputs: [$('#date1'), $('#date2')],
orientation: "bottom right",
autoclose: true,
//todayHighlight: true,
format: "dd.mm.yyyy",
startDate: "today",
//multidate: true,
beforeShowDay: function(date) {
var hilightedDays = [];
if (ow_direct)
hilightedDays = ow_dates;
else
hilightedDays = rt_dates;
if (~hilightedDays.indexOf(date.getFullYear() + '-' + (date.getMonth() + 1) + '-' +date.getDate())) {
return {classes: 'highlight', tooltip: 'Есть рейс'};
}
}
});
$('#date1').datepicker().on('changeDate', function(ev) {
$('#date2').datepicker('setStartDate', ev.date);
// $('#date2').datepicker('update', ev.date);
});
var today = new Date();
var s_date = new Date(today.getTime() + (1 * 24 * 60 * 60 * 1000));
var e_date = new Date(today.getTime() + (7 * 24 * 60 * 60 * 1000));
// update individual dates
if ($('#date1').val() == "") {
$('#date1').datepicker('update', s_date);
$('#date2').datepicker('setStartDate', s_date);
// $('#date2').datepicker('update', e_date);
// $('.daterange').datepicker('updateDates');
}
$('.nav-blue a').click(function(e){
e.preventDefault();
var arr = $(this).attr('href')./*substr(this.href.lastIndexOf('/') + 1).*/split('#');
var ids = arr[1];
$('.tab-pane.active > table > tbody > tr').css('display', 'none');
$('.tab-pane.active > table > tbody > tr[data-route="'+ids+'"]').css('display', 'table-row');
});
$('.btn-date').click(function(){
$(this).prev().datepicker('show');
});
$('.btn-plus').click(function(){
var step = $(this).prev().val();
if (step < 5) step++;
$(this).prev().val(step);
});
$('.btn-minus').click(function(){
var step = $(this).next().val();
if (step > 1) step--;
$(this).next().val(step);
});
$('.btn-plus-pass').click(function(){
var step = $(this).prev().val();
if (step < 15) step++;
$(this).prev().val(step);
update_passlist();
});
$('.btn-minus-pass').click(function(){
var step = $(this).next().val();
if (step > 0) step--;
$(this).next().val(step);
update_passlist();
});
function update_passlist() {
if ($('#passcnt-adult').val()==0) $('#passcnt-adult').val('1'); // минимум 1 взрослый
if ($('#passcnt-inf').val()>$('#passcnt-adult').val()) $('#passcnt-inf').val($('#passcnt-adult').val()); // младенцев не больше чем взрослых
$("#passd-adult").html('');
step = $('#passcnt-adult').val();
for (k=0;k= 12) $("div[id^='modal-']").removeClass('fade');
$('.switch-label').each(function () {
if ($.browser.msie && parseInt($.browser.version) < 9) {
var n = $(this).prop('for');
if ($('#' + n).prop('checked')) $(this).children().animate({ left: '+=32' });
}
});
$('.switch-label').click(function () {
if ($.browser.msie && parseInt($.browser.version) < 9) {
var p = $(this).children().position();
var n = $(this).prop('for');
if ($('#' + n).prop('checked')) $('#' + n).prop("checked", false); else $('#' + n).prop("checked", true);
if (p.left == 32 ) $(this).children().animate({left: '-=32'}); else $(this).children().animate({left: '+=32'});
$('#fb-switch').change();
}
});
$('#fb-switch').change(function () {
if ($(this).prop('checked')) {
$('#fb-search-back').slideDown();
}
else {
$('#fb-search-back').slideUp();
}
});
$('#fb-run').click(function () {
$("#big-fly").submit();
});
$(".input-phone").mask("(999)999-99-99");
$('#pd-switch').change(function () {
$('#passd-all').slideToggle();
});
$("a.popup-frame").fancybox({
maxWidth : 600,
//maxHeight : 200,
fitToView : true,
padding : 10,
width : '600',
height : 'auto'
});
jQuery.validator.addMethod('regexp', function (value, element, regexp) {
var re = new RegExp(regexp);
return this.optional(element) || re.test(value);
}, "Недопустимый ввод");
jQuery.validator.addMethod('cyrillic', function (value, element) {
var re = new RegExp('^[ёЁа-яА-Я- ]{1,40}$');
return this.optional(element) || re.test(value);
}, "Допустима только кириллица");
$("#big-fly").validate({
onsubmit: true,
submitHandler: function (form) {
$('#main-progress').slideToggle();
$('#main-orderdata').slideUp('fast');
$('html, body').animate({ scrollTop: $('#tab-ch').position().top + 20}, 'fast');
$(form).ajaxSubmit({
url: '/app/req-tickets.php',
type: 'post',
//dataType : 'json',
success: function(responseText){
$("#main-results").html(responseText);
$('#main-orderdata').fadeIn();
$('#main-progress').slideToggle();
$('html, body').animate({ scrollTop: $('#main-orderdata').position().top - 200}, 'fast');
}
})
},
highlight: function (label) {
$(label).closest('td').addClass('input-error');
},
unhighlight: function (label) {
$(label).closest('td').removeClass('input-error');
$(label).tooltip('destroy');
},
errorPlacement: function (error, element) {
$(element).tooltip({
title: error[0].innerText,
placement: "top",
trigger: "hover"
});
},
errorElement: "span",
event: "submit",
focusCleanup: false
});
$("#frm-findorder").validate({
onsubmit: true,
submitHandler: function (form) {
$(form).ajaxSubmit({
url: '/app/orderinfo.php',
success: function(responseText){
$.fancybox({
content: responseText,
autoResize: false,
padding: 0,
minWidth: 300,
maxWidth: 1004,
topRatio: .2,
height: 'auto'
});
}
})
},
highlight: function (label) {
$(label).closest('.navdar-search').addClass('input-error');
},
unhighlight: function (label) {
$(label).closest('.navdar-search').removeClass('input-error');
$(label).tooltip('destroy');
},
errorPlacement: function (error, element) {
$(element).tooltip({
title: error[0].innerText,
placement: "top",
trigger: "hover"
});
},
errorElement: "span",
event: "submit",
focusCleanup: false
});
$("#frm-sendorder").validate({
onsubmit: true,
submitHandler: function (form) {
$("#frm-sendorder button").prop('disabled',true);
$(form).ajaxSubmit({
url: '/app/send-order.php',
type: 'post',
//dataType : 'json',
success: function(responseText){
$.fancybox({
helpers: {
overlay : {
closeClick : false
}
},
content: responseText,
closeBtn: false,
autoResize: false,
padding: 0,
minWidth: 550,
maxWidth: 554,
topRatio: .2,
height: 'auto'
});
}
})
},
highlight: function (label) {
$(label).parent().addClass('input-error');
},
unhighlight: function (label) {
$(label).parent().removeClass('input-error');
$(label).tooltip('destroy');
},
errorPlacement: function (error, element) {
$(element).tooltip('destroy');
$(element).tooltip({
title: error[0].innerText,
placement: "top",
trigger: "hover"
});
},
errorElement: "span",
event: "submit",
focusCleanup: false,
rules: {
'client_phone': {
regexp: '^[(][0-9]{3}[)][0-9]{3}-[0-9]{2}-[0-9]{2}$'
}
}
});
$("#frm-profile").validate({
onsubmit: true,
submitHandler: function (form) {
$(form).ajaxSubmit({
url: '/app/send-profile.php',
type: 'post',
//dataType : 'json',
success: function(responseText){
$('#frm-profile').prepend(responseText);
$('#frm-profile').children('div').first().fadeOut(1600);
}
})
},
highlight: function (label) {
$(label).parent().addClass('input-error');
},
unhighlight: function (label) {
$(label).parent().removeClass('input-error');
$(label).tooltip('destroy');
},
errorPlacement: function (error, element) {
$(element).tooltip({
title: error[0].innerText,
placement: "top",
trigger: "hover"
});
},
errorElement: "span",
event: "submit",
focusCleanup: false
});
$("#frm-crm").validate({
onsubmit: true,
submitHandler: function (form) {
$(form).ajaxSubmit({
url: '/app/send-crm.php',
type: 'post',
//dataType : 'json',
success: function(responseText){
$.fancybox.close();
}
})
},
event: "submit",
focusCleanup: false
});
$(".form-signin").validate({
onsubmit: true,
highlight: function (label) {
$(label).parent().addClass('input-error');
},
unhighlight: function (label) {
$(label).parent().removeClass('input-error');
$(label).tooltip('destroy');
},
errorPlacement: function (error, element) {
$(element).tooltip('destroy');
$(element).tooltip({
title: error[0].innerText,
placement: "top",
trigger: "hover"
});
},
errorElement: "span",
event: "submit",
focusCleanup: false,
rules: {
'client_phone': {
regexp: '^[(][0-9]{3}[)][0-9]{3}-[0-9]{2}-[0-9]{2}$'
}
}
});
$("#frm-flight").validate({
highlight: function (label) {
$(label).closest('div').addClass('input-error');
},
unhighlight: function (label) {
$(label).closest('div').removeClass('input-error');
$(label).tooltip('destroy');
},
errorPlacement: function (error, element) {
$(element).tooltip({
title: error[0].innerText,
placement: "top",
trigger: "hover"
})
},
errorElement: "span",
event: "submit",
rules: {
t91: {
rangelength: [4, 50]
}
},
messages: {
t91: {
rangelength: 'Подозрительно короткий номер'
},
captcha: {
required: 'Докажите что вы не робот'
}
}
});
$('.btn-lostpass').click(function(){
$('#passbox').siblings('.btn').html('Выслать пароль');
$('#passbox').slideToggle().empty();
$('.form-signin-heading').html('Восстановление пароля').after('Введите почту, используемую при регистрации');
});
$(".btn-find").click( function () {
$("#frm-findorder").submit();
});
$('#my-btn-print').click(function (e){
e.preventDefault();
});
$('#my-accept-offer').change(function (){
if ($("#my-accept-offer").is(':checked') == true) {
$("#my-btn-print").prop('disabled',false);
$("#my-btn-pay").prop('disabled',false);
}
else
{
$("#my-btn-print").prop('disabled',true);
$("#my-btn-pay").prop('disabled',true);
}
})
$('input[name="my_paymethod"]').change(function (){
if ($("input[name='my_paymethod']:checked").val() == '1') {
$("#my-btn-print").hide();
$("#my-btn-pay").show();
}
else
{
$("#my-btn-print").show();
$("#my-btn-pay").hide();
}
$('#my-pay-block').slideDown().show();
})
$('input[id^="orderid-"]').change( function () {
var sum = 0;
var csum = 0;
var oid = '';
$("input[id^='orderid-']:checked").each(function (i) {
idx = $(this).val();
oid += idx+':';
cval = parseFloat($("input[id^='prices-"+idx+"']").val());
sum += cval;
csum += parseFloat(cval + cval*($("input[id^='comm-"+idx+"']").val() / 100));
});
if (oid != '') {
$('#pay input[name="orderId"]').val(oid);
$('#pay input[name="recipientAmount"]').val(csum.toFixed(2));
$("#price_total1").html(csum.toFixed(2) + ' руб.');
$("#price_total2").html(sum.toFixed(2) + ' руб.');
}
else
{
$('#pay input[name="orderId"]').val('');
$('#pay input[name="recipientAmount"]').val('');
$("#price_total1").html('');
$("#price_total2").html('');
}
})
$('.tablo').tooltip({
selector: "abbr[data-toggle=tooltip]"
})
function addPassRow(node) {
$(tmplPass(j++)).hide().appendTo(node).fadeIn();
$('.date-any').datepicker({
language: "ru",
orientation: "bottom right",
autoclose: true,
startView: "years",
format: "dd.mm.yyyy"
});
$('.date-today').datepicker({
language: "ru",
orientation: "bottom right",
autoclose: true,
todayHighlight: true,
startView: "years",
format: "dd.mm.yyyy",
startDate: "today"
});
};
var j = 0;
if ($("#template2").val() != undefined) {
var tmplPass = jQuery.format($("#template2").val());
for (k=0;k<2;k++){
addPassRow('#passd-adult');
}
}
});
function _adpress(i, p, z) {
$.get('/serv/advstat.php?tid=' + i + '&page=' + p + '&zone=' + z);
}
function print_window(url) {
PWindow = window.open(url, 'PWindow', 'width=760,height=680,left=30,top=30');
PWindow.focus();
}
function confirmLink(theLink, theQuery) {
var is_confirmed = confirm(theQuery);
if (is_confirmed) {
theLink.href += '&is_confirmed=1';
}
return is_confirmed;
}
