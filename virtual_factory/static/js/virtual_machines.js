function virtualMachineQuery() {
    $.ajax({
        url: "/_machines",
        success: function(data) {
            $("#virtual_machines").html(data)
        }
    });
    setTimeout(virtualMachineQuery, 10000);
}

$(document).ready(function() {
    console.log("testing");
    setTimeout(virtualMachineQuery, 10000);
})