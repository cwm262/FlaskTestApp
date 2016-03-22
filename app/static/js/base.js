/**
 * Created by cwm on 3/6/2016.
 */

$(document).ready(function () {

    /*(function ($) {

        $('#filter').keyup(function () {

            var rex = new RegExp($(this).val(), 'i');
            $('.searchable tr').hide();
            $('.searchable tr').filter(function () {
                return rex.test($(this).text());
            }).show();

        })

    }(jQuery));*/

    $(function(){
        $("#showProfileBtn").click(function(){
            $("#ajaxTarget").hide();
            $("#showProfileBtn").hide();
            $("#viewPtsBtn").show();
            $("#profileWindow").show();
        });
        $('#viewPtsBtn').click(function(){
            $("#profileWindow").hide();
            $("#viewPtsBtn").hide();
            $("#showProfileBtn").show();
            $("#ajaxTarget").html("<img src='/static/images/load.gif'/>");
            //event.preventDefault();
            var paw = $("#profileWindow").attr("about");
            var filters = [{"name": "student_id", "op": "like", "val": paw}];
            $.ajax({
              url: '/api/points',
              data: {"q": JSON.stringify({"filters": filters})},
              dataType: "json",
              contentType: "application/json"
            })
                .done( function(response){
                    var resp = response;
                    var points = resp.objects;
                    var ptsTable = "<div class='panel-heading'>\
                                                <h3 class='panel-title'>Point History, Ordered by Date</h3>\
                                            </div>\
                                            <div class='panel-body'>\
                                                <div class='input-group'> <span class='input-group-addon'>Filter</span>\
                                                    <input id='filter' type='text' class='form-control' placeholder='Type here...'>\
                                                </div>\
                                            </div>\
                                            <table class='table table-bordered table-hover'>\
                                                <thead>\
                                                    <tr>\
                                                        <th>Date Assigned</th>\
                                                        <th>Type</th>\
                                                        <th>Why</th>\
                                                        <th>Amount</th>\
                                                        <th>Supervisor</th>\
                                                    </tr>\
                                                </thead>\
                                                <tbody class='searchable'>";
                    $.each(points, function(i, val){
                        ptsTable += "<tr class='studentListRow active'>\
                            <td>" + val.when + "</td>\
                            <td>" + val.type + "</td>\
                            <td>" + val.why + "</td>\
                            <td>" + val.amount + "</td>\
                            <td>" + val.supervisor + "</td>\
                            </tr>";
                    });
                    ptsTable += "</tbody>\
                        </table>";
                    $("#ajaxTarget").html(ptsTable);
                    $('#filter').keyup(function () {
                        var rex = new RegExp($(this).val(), 'i');
                        $('.searchable tr').hide();
                        $('.searchable tr').filter(function () {
                            return rex.test($(this).text());
                        }).show();
                    })
                })
        });

    });


});