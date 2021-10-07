function virtualMachineQuery() {
    $.ajax({
        url: "/_machines",
        success: function(data) {
            $("#virtual_machines").html(data)
        }
    });
    setTimeout(virtualMachineQuery, 1000);
}

$(document).ready(function() {
    console.log("testing");
    setTimeout(virtualMachineQuery, 1000);
})