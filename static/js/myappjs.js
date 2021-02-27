

// datatable javascipt config code
$(function () {
    $("#example1").DataTable({
        "responsive": true, "lengthChange": false, "autoWidth": false,
    })
    $('#example2').DataTable({
        "paging": true,
        "lengthChange": false,
        "searching": false,
        "info": true,
        "autoWidth": false,
        "responsive": true,
    });
});


// loading code
const loader = document.querySelector(".loader");
const sidebar = document.querySelector(".main-sidebar");
sidebar.style.visibility = "initial"
const wrapper = document.querySelector(".wrapper");
const footer = document.querySelector(".main-footer");
const loadingmsg = document.querySelector(".loadingmsg");
window.onload = function () {
    setTimeout(function () {
        loader.style.opacity = "0";
        loader.style.display = "none";
        document.getElementById('circle').remove()
        loadingmsg.style.display = "none";
        wrapper.style.visibility = "visible"
        footer.style.visibility = "visible"
        sidebar.style.visibility = "visible"
    }, 1000);
}