// Add New Client From Creat / Edit (modal handler)

function AddNewClient() {
    $(document).ready(function () {
        $("#AddClientModal").modal({ backdrop: false });
    });
}

// on submit form use Ajax
$('#AddNewClientForm').submit(function (e) {
    e.preventDefault() // prevat form from reloading page
    document.getElementById('IconPlus').style = 'display:none'
    document.getElementById('IconSpin').style = 'display:content'
    $.ajax({
        type: "POST",
        url: this.action, // get action from form
        data: $('#AddNewClientForm').serialize(), // get all inputs from from and convert them to Json
        dataType: "json",
        encode: true,
        success: function (response) { // if respond == 200
            toastr.success(response.MSG, "demande réussie");
            var ClientName = response.ClientData.Client_Name.toUpperCase() + ':' + response.ClientData.City
            $("#ClientID").append(new Option(ClientName, response.CLIENT_ID));
            $("#ClientID").val(response.CLIENT_ID)
            document.getElementById('IconPlus').style = 'display:content'
            document.getElementById('IconSpin').style = 'display:none'
            $('#AddClientModal').modal('hide');
            document.getElementById("AddNewClientForm").reset();
        },
        error: function (response) {
            document.getElementById('IconPlus').style = 'display:content'
            document.getElementById('IconSpin').style = 'display:none'
            toastr.error(response.responseJSON.ERR_MSG, "demande infructueuse");
        }
    })
})

// on submit form use Ajax
$('#MainAddNewClientForm').submit(function (e) {
    e.preventDefault() // prevat form from reloading page
    document.getElementById('IconPlus').style = 'display:none'
    document.getElementById('IconSpin').style = 'display:content'
    $.ajax({
        type: "POST",
        url: this.action, // get action from form
        data: $('#MainAddNewClientForm').serialize(), // get all inputs from from and convert them to Json
        dataType: "json",
        encode: true,
        success: function (response) { // if respond == 200
            toastr.success(response.MSG, "demande réussie");
            var ClientName = response.ClientData.Client_Name
            var ICE = response.ClientData.ICE
            var City = response.ClientData.City
            var Action = `<a class='btn btn-info  btn-sm' href='#' onclick="EditClient(this, '/settings/manage-clients/edit/${response.CLIENT_ID}')" title='Edit' data-toggle='tooltip'><i class='fas fa-pencil-alt' ></i >\n</a ><a class='btn btn-danger btn-sm' href='#' title='Delete' onclick="EnterPwdToDeletePopup('/settings/manage-clients/delete/${response.CLIENT_ID}');" data-toggle='tooltip'><i class='fas fa-trash'></i></a>`
            var ROWS = [ClientName, ICE, City, Action]
            var table = document.getElementById('ClientTable').getElementsByTagName('tbody')[0];
            var new_row = table.insertRow(0)
            for (i = 0; i < ROWS.length; i++) {
                new_cell = new_row.insertCell(i)
                new_cell.innerHTML = ROWS[i]
            }
            document.getElementById('IconPlus').style = 'display:content'
            document.getElementById('IconSpin').style = 'display:none'
            document.getElementById("MainAddNewClientForm").reset();
        },
        error: function (response) {
            document.getElementById('IconPlus').style = 'display:content'
            document.getElementById('IconSpin').style = 'display:none'
            toastr.error(response.responseJSON.ERR_MSG, "demande infructueuse");
        }
    })
})








function GetSelectedProductThenSet() {
    var ProductName = document.getElementById("ProductName");
    document.getElementsByClassName('editOption')[0].value = ProductName.value
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
        if (this.status == 404 || this.status == 502) {
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
    document.getElementsByClassName('editOption')[1].value = ProductName.value
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
        if (this.status == 404 || this.status == 502) {
            document.getElementById('circle_edit').style.display = 'none'
        }
    };
    if (ProductName.value !== '-') {
        document.getElementById('circle_edit').style.display = 'block'
    }
    xhttp.open("GET", url, true);
    xhttp.send();
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


// datatable javascipt config code
$(function () {
    $("#example1").DataTable({
        "responsive": true,
        "info": true,
        "lengthChange": false,
        "autoWidth": false,
        "searching": false,
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
const loadingmsg = document.querySelector(".loadingmsg");
window.onload = function () {
    setTimeout(function () {
        loader.style.opacity = "0";
        loader.style.display = "none";
        document.getElementById('circle').remove()
        loadingmsg.style.display = "none";
        wrapper.style.visibility = "visible"
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

function EditProduct(row, action) {
    var p = row.parentNode.parentNode;
    var row_data_client = p.innerText
    var row_data_client = row_data_client.split('	').slice(0, 3)
    document.getElementById('ProductName').value = row_data_client[0]
    document.getElementById('PU').value = row_data_client[1]
    document.getElementById('FormToEditProduct').action = action
    $(document).ready(function () {
        $("#EditProductModal").modal({ backdrop: false });
    });
};


function EditClient(row, action) {
    var p = row.parentNode.parentNode;
    var row_data_client = p.innerText
    var row_data_client = row_data_client.split('	').slice(0, 3)
    document.getElementById('ICE').value = row_data_client[1]
    document.getElementById('ClientName').value = row_data_client[0]
    document.getElementById('City').value = row_data_client[2]
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


function AddNewFactureItemModalHandler() {
    document.getElementById('Qs').value = 1
    document.getElementById('ProductName').value = "-"
    document.getElementsByClassName('editOption')[0].value = null
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
    TableInfoHandler()


};
function DeleteSelectedRow(row) {
    var p = row.parentNode.parentNode;
    p.parentNode.removeChild(p);
    TableInfoHandler()
};
function EditSelectedRow(row) {
    var p = row.parentNode.parentNode;
    var row_data = p.innerText
    var row_data = row_data.split('	').slice(0, 4)
    document.getElementById('SelectedRowNumber').value = p.rowIndex
    document.getElementById('Edit_Qs').value = row_data[0]
    document.getElementById('Edit_ProductName').value = row_data[1]
    document.getElementsByClassName('editOption')[1].value = row_data[1]
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
$('#Form').submit(function (e) {
    e.preventDefault() // prevat form from reloading page
    document.getElementById('IconPlus').style = 'display:none'
    document.getElementById('IconSpin').style = 'display:content'
    document.getElementById('savebttn').disabled = true
    $.ajax({
        type: "POST",
        url: this.action, // get action from form
        data: $('#Form').serialize(), // get all inputs from from and convert them to Json
        dataType: "json",
        encode: true,
        success: function (response) { // if respond == 200
            Swal.fire(
                response.MSG,
                '',
                'success'
            ).then(function () {
                window.open(response.ROOT_URL, '_self');
                window.open(response.ROOT_URL+'detail/open/' + response.ID, '_blank').focus();
            });
            document.getElementById('IconPlus').style = 'display:content'
            document.getElementById('IconSpin').style = 'display:none'
            document.getElementById('savebttn').disabled = false
            document.getElementById("Form").reset();
        },
        error: function (response) {
            document.getElementById('IconPlus').style = 'display:content'
            document.getElementById('IconSpin').style = 'display:none'
            document.getElementById('savebttn').disabled = false
            toastr.error(response.responseJSON.ERR_MSG, "demande infructueuse");
        }
    })
})
function LoadDatatableAndSubmit() {
    var JsonTable = tableToJSON()
    let tabledata = JSON.parse(JsonTable)
    if (tabledata.myrows.length > 0) {
        document.getElementById('tableinput').value = JsonTable
        // document.getElementById("Form").submit();
    }
    if (tabledata.myrows.length == 0) {
        toastr.error('Le tableau des éléments. est vide', "S'il Vous Plaît Ajouter Un élément");
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
    TableInfoHandler()

}


function ValidInputNotEmpty(modaltype) {
    function valid(list_of_inputs, modaltype) {
        let InvalidInputs = []
        var IDs = ['ClientID', 'paiementmethod']
        for (let index = 0; index < list_of_inputs.length; index++) {
            var theinput = list_of_inputs[index]
            if (IDs.includes(theinput.id) == true) {
                if (IDs.includes(theinput.id) == true && theinput.value == '-') {
                    if (theinput.id == 'ClientID') {
                        $('#ClientID').val('-');
                        InvalidInputs.push(document.getElementById('ClientID'))
                    }
                    var isPaid = document.getElementById('ispaid')
                    if (isPaid != null){
                        if (document.getElementById('ispaid').value == 'Oui' && theinput.id == 'paiementmethod') {
                            $('#paiementmethod').val('-')
                            InvalidInputs.push(document.getElementById('paiementmethod'))
                        }
                    }
                }
                if (IDs.includes(theinput.id) == true && theinput.value !== '-') {
                    if (theinput.id == 'ClientID') {
                        RemoveInvalidClass([document.getElementById('ClientID')]);
                    }
                    if (theinput.id == 'paiementmethod') {
                        RemoveInvalidClass([document.getElementById('paiementmethod')]);
                    }
                }
            }
            else {
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
    if (modaltype == 'addnew') {
        var Qs = document.getElementById('Qs')
        var ProductName = document.getElementById('ProductName')
        var PU = document.getElementById('PU')
        var PT = document.getElementById('PT')
        var list_of_inputs = [Qs, ProductName, PU, PT]
        valid(list_of_inputs, modaltype);
    }
    if (modaltype == 'edit') {
        var Qs = document.getElementById('Edit_Qs')
        var ProductName = document.getElementById('Edit_ProductName')
        var PU = document.getElementById('Edit_PU')
        var PT = document.getElementById('Edit_PT')
        var list_of_inputs = [Qs, ProductName, PU, PT]
        valid(list_of_inputs, modaltype);
    }
    if (modaltype == 'clientside') {
        var F = document.getElementById('facture_number')
        var C = document.getElementById('ClientID')
        var D = document.getElementById('Date')

        var M = document.getElementById('paiementmethod')
        var isPaid = document.getElementById('ispaid')
        if (M == null && isPaid == null) {
            var list_of_inputs = [F, C, D]
        }
        else {
            var list_of_inputs = [F, C, D, M]
        }

        valid(list_of_inputs, modaltype);
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



/*
    Select ALL/Choose BL then send POST to convert them
*/

function Selectallthengo(table_id) {
    var ALL_BLs = []
    var theTable = document.getElementById(table_id)
    for (let rw = 1; rw < theTable.rows.length; rw++) {
        // get BL id that stored in checkbox that come from APPfunctions :)
        var BL_id = theTable.rows[rw].cells[0].firstChild.id
        ALL_BLs.push(BL_id)
    }
    POSTselectedBL(ALL_BLs);
}

function Selectthengo(table_id) {
    var ALL_BLs = []
    var theTable = document.getElementById(table_id)
    for (let rw = 1; rw < theTable.rows.length; rw++) {
        // get BL id that stored in checkbox that come from APPfunctions :)
        var BL = theTable.rows[rw].cells[0].firstChild
        if (BL.checked) {
            ALL_BLs.push(BL.id)
        }
    }
    if (ALL_BLs.length == 0) {
        toastr.error('Please Select At Least One BL', "No BL Selected");
    }
    if (ALL_BLs.length !== 0) {
        POSTselectedBL(ALL_BLs);
    }
}

function POSTselectedBL(BLs) {
    var frm = document.getElementById('FormSELECTEDBL')
    var inpt = document.getElementById('SELECTEDBL')
    inpt.value = BLs
    frm.submit()
}

// Screen Width Handler
jQuery(document).ready(function ($) {
    var alterClass = function () {
        var ww = document.body.clientWidth;
        if (ww <= 685) {
            // Remove 3 Buttns on top nav bar
            document.getElementById('RemoveOn650px').style = 'display:none !important ;'
        } else if (ww > 685) {
            document.getElementById('RemoveOn650px').style = 'display:inherit !important ;'
        };
    };
    $(window).resize(function () {
        alterClass();
    });
    //Fire it when the page first loads:
    alterClass();
});





