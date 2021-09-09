/* Add Class requiredfield for required fields */
let req = $(".form-control:required");
for (var i = 0; i < req.length; i++) {
    let reqid = req[i].id;
    $("label[for="+reqid+"]").addClass('requiredfield');
    }
