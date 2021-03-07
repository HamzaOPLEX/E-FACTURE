
function GetSelectedThenSet() {
    var clientname = document.getElementById("ClientName");
    if (clientname.value !== '') {
        document.getElementsByClassName('editOption')[0].value = clientname.value
        var url = '/create-new-facture/getclientinfo/' + clientname.value
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                ClientData = JSON.parse(this.responseText);
                document.getElementById("ICE").value = ClientData.ICE;
                document.getElementById("City").value = ClientData.City;
                document.getElementById('circle01').style.display = 'none'
                document.getElementById('circle02').style.display = 'none'
            }
            if (this.status == 404){
                document.getElementById('circle01').style.display = 'none'
                document.getElementById('circle02').style.display = 'none'
            }
        }
        if (clientname.value !== '-'){
            document.getElementById('circle01').style.display = 'block'
            document.getElementById('circle02').style.display = 'block'
        }
        xhttp.open("GET", url, true);
        xhttp.send();
    }
}
function GetSelectedProductThenSet() {
    var ProductName = document.getElementById("ProductName");
    document.getElementsByClassName('editOption')[1].value = ProductName.value
    var url = '/create-new-facture/getproductinfo/' + ProductName.value
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let Qs = document.getElementById('Qs').value
            let ProductData = JSON.parse(this.responseText);
            document.getElementById("PU").value = ProductData.PU;
            if (Qs.value !== null || Qs.value !== 0) {
                document.getElementById('PT').value = document.getElementById("PU").value * Qs
            }
            document.getElementById('circle_addnew').style.display = 'none'
        }
        if (this.status == 404){
            document.getElementById('circle_addnew').style.display = 'none'
        }

    };
    if (ProductName.value !== '-') {
        document.getElementById('circle_addnew').style.display = 'block'
    }
    xhttp.open("GET", url, true);
    xhttp.send();
}
function GetSelectedProductThenSetEdit() {
    var ProductName = document.getElementById("Edit_ProductName");
    document.getElementsByClassName('editOption')[2].value = ProductName.value
    var ProductName = document.getElementById("Edit_ProductName");
    var url = '/create-new-facture/getproductinfo/' + ProductName.value
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let Qs = document.getElementById('Edit_Qs').value
            let ProductData = JSON.parse(this.responseText);
            document.getElementById("Edit_PU").value = ProductData.PU;
            if (Qs.value !== null || Qs.value !== 0) {
                document.getElementById('Edit_PT').value = document.getElementById("Edit_PU").value * Qs
            }
            document.getElementById('circle_edit').style.display = 'none'
        }
        if (this.status == 404) {
            document.getElementById('circle_edit').style.display = 'none'
        }
    };
    if (ProductName.value !== '-') {
        document.getElementById('circle_edit').style.display = 'block'
    }
    xhttp.open("GET", url, true);
    xhttp.send();
}




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
    document.getElementById('deleteform').action = action
    $(document).ready(function () {
        $("#DeleteModal").modal({ backdrop: false });
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
        $("#EditProductModal").modal({ backdrop: false });
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
        $("#EditClientModal").modal({ backdrop: false });
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
        $("#AddNewFactureItemModal").modal({ backdrop: false });
    });
};
function AddToTable() {
    var Qs = document.getElementById('Qs').value;
    var DESIGNATION = document.getElementById('ProductName').value;
    var PU = document.getElementById('PU').value;
    var PT = document.getElementById('PT').value;
    var Action = '<button type="button"  class="btn btn-danger btn-sm" onclick="DeleteSelectedRow(this);"><i class="fas fa-trash"></i></button><button type="button" id="editrow" class="btn btn-info btn-sm" style="margin-left: 12px;padding-right: 6px;"  onclick="EditSelectedRow(this);"><i class="fas fa-edit"></i></button>'
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
    $('#AddNewFactureItemModal').modal('hide')

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
        $("#EditFactureItemModal").modal({ backdrop: false });
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
    let tabledata = JSON.parse(JsonTable)
    if (tabledata.myrows.length > 0){
        document.getElementById('tableinput').value = JsonTable
        document.getElementById("Form").submit();
    }
    if (tabledata.myrows.length == 0) {
        toastr.error('Le tableau des éléments de facture est vide', "S'il Vous Plaît Ajouter Un Élément à Votre Facture");
    }

}
function SaveEdited(row) {
    var row_index = document.getElementById('SelectedRowNumber').value;
    var table = document.getElementById('Table');
    table.rows[row_index].cells[0].innerText = document.getElementById('Edit_Qs').value
    table.rows[row_index].cells[1].innerText = document.getElementById('Edit_ProductName').value
    table.rows[row_index].cells[2].innerText = document.getElementById('Edit_PU').value
    table.rows[row_index].cells[3].innerText = document.getElementById('Edit_PT').value
    $('#EditFactureItemModal').modal('hide')
}



/* --> Start Function To Valid All Inputs <-- */


        /* 
            1 - Find a way to push input into InvalidInputs Array
            2 - Find a way to get for every Select here Input :)
        */
// function ValidSelectXinput(select,input) {
//     if (select.value.trim() == '-' || input.value.trim() == '') {
//         clearSelected(select)
//         InvalidInputs.push(input)
//     }
//     if (select.value.trim() !== '-' || input.value.trim() !== '') {
//         RemoveInvalidClass([input]);
//     }
// }



function ValidInputNotEmpty(modaltype) {
    function valid(list_of_inputs,modaltype) {
        let InvalidInputs = []
        for (let index = 0; index < list_of_inputs.length; index++) {
            var theinput = list_of_inputs[index]

            if (theinput.id == 'ClientName'){
                if (theinput.id == 'ClientName' && theinput.value.trim() == '-' || document.getElementById('ClientNameInput').value.trim() == '') {
                    clearSelected(document.getElementById('ClientName'))
                    InvalidInputs.push(document.getElementById('ClientNameInput'))
                }
                if (theinput.id == 'ClientName' && theinput.value.trim() !== '-' || document.getElementById('ClientNameInput').value.trim() !== '') {
                    RemoveInvalidClass([document.getElementById('ClientNameInput')]);
                }  
            }
            else{
                if (theinput.value.trim() == '') {
                    InvalidInputs.push(theinput)
                };
                if (theinput.value.trim() !== '') {
                    RemoveInvalidClass([theinput]);
                };
            }      
        }
        if (InvalidInputs.length == 0) {
            if (modaltype == 'addnew') {
                AddToTable();
            };
            if (modaltype == 'edit') {
                SaveEdited();
            };
            if (modaltype == 'clientside') {
                LoadDatatableAndSubmit();
            };
        }
        if (InvalidInputs.length > 0) {
            for (let index = 0; index < InvalidInputs.length; index++) {
                var theInvalidInput = InvalidInputs[index]
                AddInvalidClass([theInvalidInput]);
            }
        }
    }
    if (modaltype == 'addnew'){
        var Qs = document.getElementById('Qs')
        var ProductName = document.getElementById('ProductName')
        var PU = document.getElementById('PU')
        var PT = document.getElementById('PT')
        var list_of_inputs = [Qs, ProductName, PU, PT]
        valid(list_of_inputs,modaltype);
    }
    if (modaltype == 'edit') {
        var Qs = document.getElementById('Edit_Qs')
        var ProductName = document.getElementById('Edit_ProductName')
        var PU = document.getElementById('Edit_PU')
        var PT = document.getElementById('Edit_PT')
        var list_of_inputs = [Qs, ProductName, PU, PT]
        valid(list_of_inputs,modaltype);
    }
    if (modaltype == 'clientside') {
        var F = document.getElementById('facture_number')
        var C = document.getElementById('ClientName')
        var I = document.getElementById('ICE')
        var CI = document.getElementById('City')
        var D = document.getElementById('Date')
        var list_of_inputs = [F, C, I, CI,D]
        valid(list_of_inputs,modaltype);
    }
}





function clearSelected(select) {
    var elements = select.selectedOptions;
    for (var i = 0; i < elements.length; i++) {
        elements[i].selected = false;
    }
}
function RemoveInvalidClass(list_of_inputs) {
    for (let index = 0; index < list_of_inputs.length; index++) {
        var theinput = list_of_inputs[index].classList.remove('is-invalid')
    }
}
function AddInvalidClass(list_of_inputs) {
    for (let index = 0; index < list_of_inputs.length; index++) {
        var theinput = list_of_inputs[index].classList.add('is-invalid')
    }
}



/* --> End Function To Valid All Inputs <-- */
