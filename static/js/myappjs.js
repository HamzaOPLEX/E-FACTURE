

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


function check_if_inputval_is_already_in_select(selec, data2check) {
    // true : option exist
    // false : option does not exist
    if ($("#" + selec + " option[value='" + data2check + "']").length !== 0) { return true };
    if ($("#" + selec + " option[value='" + data2check + "]'").length == 0) { return false };
}
function GetInputAndSet2Select(Idselect, editOptionIndex) {
    var editText = document.getElementsByClassName('editOption')[editOptionIndex].value
    let select = document.getElementById(Idselect);
    if (editText !== '') {
        statuss = check_if_inputval_is_already_in_select(Idselect, editText)
        if (statuss == false) {
            var option = document.createElement("option");
            option.value = editText;
            option.text = editText;
            select.add(option);
            select.value = editText
            select.onchange()
        }
        if (statuss == true) {
            select.value = editText
            select.onchange()
        }
    }
}

function AddNewFactureItemModalHandler() {
    document.getElementById('Qs').value = 1
    document.getElementById('ProductName').value = "-"
    document.getElementsByClassName('editOption')[1].value = null
    document.getElementById('PU').value = 0
    document.getElementById('PT').value = 0
    $(document).ready(function () {
        $("#AddNewFactureItemModal").modal({ backdrop: true });
    });
};
function AddToTable() {
    var Qs = document.getElementById('Qs').value;
    var DESIGNATION = document.getElementById('ProductName').value;
    var PU = document.getElementById('PU').value;
    var PT = document.getElementById('PT').value;
    var Action = '<button type="button"  class="btn btn-default btn-danger" onclick="DeleteSelectedRow(this);"><i class="fas fa-trash"></i></button><button type="button" id="editrow" class="btn btn-default btn-info"  onclick="EditSelectedRow(this);"><i class="fas fa-edit"></i></button>'
    var table = document.getElementById('Table').getElementsByTagName('tbody')[0];
    var new_row = table.insertRow(-1)
    var cell_qs = new_row.insertCell(0)
    cell_qs.innerHTML = Qs
    var cell_DESIGNATION = new_row.insertCell(1)
    cell_DESIGNATION.innerHTML = DESIGNATION
    cell_DESIGNATION.id = 'ds'
    var cell_PU = new_row.insertCell(2)
    cell_PU.innerHTML = PU
    var cell_PT = new_row.insertCell(3)
    cell_PT.innerHTML = PT
    var cell_action = new_row.insertCell(4)
    cell_action.innerHTML = Action
    cell_action.style = 'text-align:center;'
};
function DeleteSelectedRow(row) {
    var p = row.parentNode.parentNode;
    p.parentNode.removeChild(p);
};
function EditSelectedRow(row) {
    var p = row.parentNode.parentNode;
    var row_data = p.innerText
    var row_data = row_data.split('	').slice(0, 4)
    document.getElementById('SelectedRowNumber').value = p.rowIndex
    document.getElementById('Edit_Qs').value = row_data[0]
    document.getElementById('Edit_ProductName').value = row_data[1]
    document.getElementsByClassName('editOption')[2].value = row_data[1]
    document.getElementById('Edit_PU').value = row_data[2]
    document.getElementById('Edit_PT').value = row_data[3]

    // if product name not in select as option add new one
    var data = {
        val: row_data[1],
        text: row_data[1]
    };
    var newOption = new Option(data.text, data.val, false, false);
    if ($('#Edit_ProductName').find("option[value='" + data.val + "']").length) {
        $('#Edit_ProductName').val(data.val).trigger('change');
    } else {
        var newOption = new Option(data.text, data.val, true, true);
        $('#Edit_ProductName').append(newOption).trigger('change');
    }

    $(document).ready(function () {
        $("#EditFactureItemModal").modal({ backdrop: true });
    });
}
function tableToJSON() {
    var myRows = [];
    var pass = 'pass'
    var $headers = $("th");
    var $rows = $("tbody tr").each(function (index) {
        $cells = $(this).find("td");
        myRows[index] = {};
        $cells.each(function (cellIndex) {
            if ($headers[cellIndex].innerText == "Action") {
                pass
            }
            else {
                myRows[index][$($headers[cellIndex]).html()] = $(this).html();
            }
        });
    });
    var myObj = {};
    myObj.myrows = myRows;
    return JSON.stringify(myObj)
}
function LoadDatatableAndSubmit() {
    var JsonTable = tableToJSON()
    document.getElementById('tableinput').value = JsonTable
    document.getElementById("Form").submit();
}
function SaveEdited(row) {
    var row_index = document.getElementById('SelectedRowNumber').value;
    var table = document.getElementById('Table');
    table.rows[row_index].cells[0].innerText = document.getElementById('Edit_Qs').value
    table.rows[row_index].cells[1].innerText = document.getElementById('Edit_ProductName').value
    table.rows[row_index].cells[2].innerText = document.getElementById('Edit_PU').value
    table.rows[row_index].cells[3].innerText = document.getElementById('Edit_PT').value
}