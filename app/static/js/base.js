/**
 * Created by cwm on 3/6/2016.
 */

$(document).ready(function () {

    (function ($) {

        $('#filter').keyup(function () {

            var rex = new RegExp($(this).val(), 'i');
            $('.searchable tr').hide();
            $('.searchable tr').filter(function () {
                return rex.test($(this).text());
            }).show();

        })

    }(jQuery));

    $(function(){
        $('#viewPtsBtn').click(function(){
            var paw = $("#profileWindow").attr("about");
            $.ajax({
                type: "GET",
                url: "/api/students/"+paw,
                contentType: "application/json",
                dataType: "json",
                success: function(result){
                    console.log(result);
                }
            });
        });
    });

});