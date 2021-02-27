

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

// Js Function to show delete object (facture,user,client,...) modal 
function EnterPwdToDeletePopup(action) {
    console.log('am in')
    document.getElementById('deleteform').action = action
    $(document).ready(function () {
        $("#DeleteModal").modal({ backdrop: true });
    });
};

function EditProduct(action) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            ProductData = JSON.parse(this.responseText);
            document.getElementById("ProductName").value = ProductData.ProductName;
            document.getElementById("PU").value = ProductData.PU;
        }
    };
    xhttp.open("GET", action, true);
    xhttp.send();
    document.getElementById('FormToEditProduct').action = action
    $(document).ready(function () {
        $("#EditProductModal").modal({ backdrop: true });
    });
};


function EditClient(action) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            ClientData = JSON.parse(this.responseText);
            document.getElementById("ClientName").value = ClientData.ClientName;
            document.getElementById("ICE").value = ClientData.ICE;
            document.getElementById("City").value = ClientData.City;
        }
    };
    xhttp.open("GET", action, true);
    xhttp.send();
    document.getElementById('FormToEditClient').action = action
    $(document).ready(function () {
        $("#EditClientModal").modal({ backdrop: true });
    });
};