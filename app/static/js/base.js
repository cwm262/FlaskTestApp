/**
 * Created by cwm on 3/6/2016.
 */

(function ($) {

    $('#filter').keyup(function () {

        var rex = new RegExp($(this).val(), 'i');
        $('.searchable tr').hide();
        $('.searchable tr').filter(function () {
            return rex.test($(this).text());
        }).show();

    });

}(jQuery));

// $(document).ajaxStart(function(){
//     $("#loader").show();
// });
//
// $(document).ajaxStop(function(){
//     $("#loader").hide();
//     $("#ajaxTarget").show();
// });

$(document).ready(function () {

    $("#viewSummaryBtn").click(function(){
        event.preventDefault();
        var paw = $("#hiddenPaw").val();
        var filters = [{"name": "pawprint", "op": "like", "val": paw}];
        $.ajax({
          url: '/api/students',
          data: {"q": JSON.stringify({"filters": filters})},
          dataType: "json",
          contentType: "application/json"
        })
            .done( function(response){
                var resp = response;
                var student = resp.objects[0];
                var profileWin = "<div class='panel panel-default'>\
                                    <div class='panel-heading'>\
                                        <h3>" + student.lname + ", " +  student.fname + "</h3>\
                                    </div>\
                                    <div class='panel-body'>\
                                        Pawprint:" +  student.pawprint + "<hr>\
                                        <a href='mailto:" + student.pawprint + "@mail.missouri.edu'>" + student.pawprint + "@mail.missouri.edu</a><hr>\
                                        In tracker since: " + moment(student.whenAdded).format('MM/DD/YYYY') + "<hr>\
                                        Point Total: " + student.pointTotal + "\
                                    </div>\
                                </div>";
                $("#ajaxTarget").html(profileWin);
            })
    });

    $('#viewWarnBtn').click(function(){
        event.preventDefault();
        var paw = $("#hiddenPaw").val();
        var filters = [{"name": "student_id", "op": "like", "val": paw}];
        $.ajax({
          url: '/api/warns',
          data: {"q": JSON.stringify({"filters": filters})},
          dataType: "json",
          contentType: "application/json"
        })
            .done( function(response){
                var r = response;
                var warns = r.objects;
                var warnTable = "<div class='panel panel-default'>\
                                    <div class='panel-heading'>\
                                        <h3 class='panel-title'>Warning History</h3>\
                                    </div>\
                                    <div class='panel-body'>\
                                        <div class='input-group'> <span class='input-group-addon'>Filter</span>\
                                            <input id='filter' type='text' class='form-control' placeholder='Type here...'>\
                                        </div>\
                                    </div>\
                                    <table class='table table-bordered'>\
                                        <thead>\
                                            <tr>\
                                                <th>Date Assigned</th>\
                                                <th>Type</th>\
                                                <th>Why</th>\
                                                <th>Supervisor</th>\
                                            </tr>\
                                        </thead>\
                                        <tbody class='searchable'>";
                $.each(warns, function(i, val){
                    warnTable += "<tr class='studentListRow active'>\
                        <td>" + moment(val.when).format('MM/DD/YYYY') + "</td>\
                        <td>" + val.type + "</td>\
                        <td>" + val.why + "</td>\
                        <td>" + val.supervisor + "</td>\
                        </tr>";
                });
                warnTable += "</tbody>\
                    </table>\
                    </div>";
                $("#ajaxTarget").html(warnTable);
                $('#filter').keyup(function () {
                    var rex = new RegExp($(this).val(), 'i');
                    $('.searchable tr').hide();
                    $('.searchable tr').filter(function () {
                        return rex.test($(this).text());
                    }).show();
                })

            })
    });

    $('#viewPtsBtn').click(function(){
        event.preventDefault();
        var paw = $("#hiddenPaw").val();
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
                var ptsTable = "<div class='panel panel-default'>\
                                    <div class='panel-heading'>\
                                        <h3 class='panel-title'>Point History, Ordered by Date</h3>\
                                    </div>\
                                    <div class='panel-body'>\
                                        <div class='input-group'> <span class='input-group-addon'>Filter</span>\
                                            <input id='filter' type='text' class='form-control' placeholder='Type here...'>\
                                        </div>\
                                    </div>\
                                    <table class='table table-bordered'>\
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
                        <td>" + moment(val.when).format('MM/DD/YYYY') + "</td>\
                        <td>" + val.type + "</td>\
                        <td>" + val.why + "</td>\
                        <td>" + val.amount + "</td>\
                        <td>" + val.supervisor + "</td>\
                        </tr>";
                });
                ptsTable += "</tbody>\
                    </table>\
                    </div>";
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