function spinner() {
   var element = document.getElementById("wrapper");
   var loader = document.getElementById("loader");
   var div = document.createElement("div");
   loader.classList.add("overlay");
   div.setAttribute("id", "misshapen-doughnut");
   element.appendChild(div);
}

var currentTab = 0; // Current tab is set to be the first tab (0)
showTab(currentTab); // Display the current tab
var options = {};

function showTab(n) {
  // This function will display the specified tab of the form ...
  var x = document.getElementsByClassName("tab");
  x[n].style.display = "block";
  // ... and fix the Previous/Next buttons:
  if (n == 0) {
    document.getElementById("prevBtn").style.display = "none";
  } else {
    document.getElementById("prevBtn").style.display = "inline";
  }
  if (n == (x.length - 1)) {
    document.getElementById("nextBtn").innerHTML = "Generate TF";
    toggleGenerateTFButton();
    $('#nextBtn').blur();
  } else {
    document.getElementById("nextBtn").innerHTML = "Next";
    $('#nextBtn').removeAttr('disabled');
  }
  // ... and run a function that displays the correct step indicator:
  fixStepIndicator(n)
}

function nextPrev(n) {
  // This function will figure out which tab to display
  var x = document.getElementsByClassName("tab");
  // Exit the function if any field in the current tab is invalid:
  if (n == 1 && !validateForm()) return false;
  // Hide the current tab:
  if(currentTab+n < x.length) {
    x[currentTab].style.display = "none";
  }
  // Increase or decrease the current tab by 1:
  currentTab = currentTab + n;
  // if you have reached the end of the form... :
  if (currentTab >= x.length) {
    //...the form gets submitted:
    tenantForm = document.getElementById("tenantForm");
    tenantForm.submit();
    spinner();
    return false;
  }
  // Otherwise, display the correct tab:
  showTab(currentTab);
}

function validateForm() {
  // This function deals with validation of the form fields
  var x, y, i, valid = true;
  x = document.getElementsByClassName("tab");
  y = x[currentTab].getElementsByTagName("input");
  z = x[currentTab].getElementsByTagName("select");
  // A loop that checks every input field in the current tab:
  for (i = 0; i < y.length; i++) {
    // If a field is empty...
    if(y[i].id == "id_Compartment_Name") {
        if($('#id_RM').prop("checked") == true && y[i].value == "") {
            y[i].className += " invalid";
            valid = false;
        }
    }
    else if(y[i].id == "id_Export_Compartment_Name") {
        if($('#id_Compartment').prop("checked") != true && $('input[name="Network"]:checked').val() == 'export_secrt' ) {
            if (y[i].value == "") {
              // add an "invalid" class to the field:
              y[i].className += " invalid";
              // and set the current valid status to false:
              valid = false;
            }
        }
    }
    else if(y[i].id == "id_Instance_SSH_Public_Key" || y[i].id == "id_Instance_SSH_Public_Value") {
        if($('#id_Compartment').prop("checked") != true && $('#id_Instance').prop("checked") == true ) {
            if (y[i].value == "") {
              // add an "invalid" class to the field:
              y[i].className += " invalid";
              // and set the current valid status to false:
              valid = false;
            }
        }
    }
    else if( y[i].id == "id_CD3_Excel") {

        var cd3exceldiv = document.getElementById("cd3excel");

        if(cd3exceldiv) {;}
        else {
            if (y[i].value == "") {
              // add an "invalid" class to the field:
              y[i].className += " invalid";
              // and set the current valid status to false:
              valid = false;
            }
        }
    }
    else if (y[i].value == "") {
      // add an "invalid" class to the field:
      y[i].className += " invalid";
      // and set the current valid status to false:
      valid = false;
    }
    else {
        y[i].className = y[i].className.replace(" invalid", "");
    }
  }

  for (j = 0; j < z.length; j++) {
    value = z[j].options[z[j].selectedIndex].value;
    if(value == "") {
            z[j].className += " invalid";
            valid = false;
     }
     else {
        z[j].className = z[j].className.replace(" invalid", "");
     }
  }
  // If the valid status is true, mark the step as finished and valid:
  if (valid) {
    document.getElementsByClassName("step")[currentTab].className += " finish";
  }
  return valid; // return the valid status
}

function fixStepIndicator(n) {
  // This function removes the "active" class of all steps...
  var i, x = document.getElementsByClassName("step");
  for (i = 0; i < x.length; i++) {
    x[i].className = x[i].className.replace(" active", "");
  }
  //... and adds the "active" class to the current step:
  x[n].className += " active";
}

$('input[type="text"]').addClass("form-control");
$("select").addClass("form-control");

var keyFile = document.getElementById("keyfile");
var currNetwork = $('input[name="Network"]:checked').val();

if(!keyFile) {
    $('input[name="Network"][value!="create_ntk"]').attr('disabled', 'disabled');
    currNetwork = null;
}

var excelCd3File = document.getElementById("cd3excel");

if(excelCd3File)  {
    var existingExcelFile = $('#cd3excel').html();
    existingExcelFile = existingExcelFile.replace("Currently: ", "Existing: ");
    existingExcelFile = existingExcelFile.replace("Change:", "")
    $('#cd3excel').empty();
    $('#cd3excel').append(existingExcelFile);
}

$(document).ready(function(){
  $('[data-toggle="tooltip"]').tooltip();
});

$('input[name="Network"]').click(function(){
      let newval = $(this).val();
      if(currNetwork == newval) {
        $(this).prop("checked", false);
        currNetwork = null;
        delete options['network'];
      }
      else {
      	currNetwork = newval;
      	options['network'] = true;
      }
      toggleGenerateTFButton();
      if(currNetwork == "export_secrt") {
        $('#id_Export_Compartment_Name').show();
        /* code added by karthik for testing */
        $('#nextBtn').hide();
        $('#generateExcel').show();
        $('#id_Compartment').attr('disabled', 'disabled');
        $('#id_Groups').prop('checked', false);
        $('#id_Groups').attr('disabled', 'disabled');
        $('#id_Groups').prop('checked', false);
        $('#id_Instance').attr('disabled', 'disabled');
        $('#id_Instance').prop('checked', false);
        $('#id_NSG').attr('disabled', 'disabled');
        $('#id_NSG').prop('checked', false);
        $('#id_Block_Volume').attr('disabled', 'disabled');
        $('#id_Block_Volume').prop('checked', false);
        $('#id_RM').attr('disabled', 'disabled');
        $('#id_RM').prop('checked', false);
        $('#id_CD3_Excel').attr('disabled', 'disabled');
        $('#id_Export_Compartment_Name').val('');
        $('#id_Instance_SSH_Public_Key').val('');
        $('#id_Instance_SSH_Public_Value').val('');
        $('#id_Instance_SSH_Public_Key').hide();
        $('#id_Instance_SSH_Public_Value').hide();
        $('input[name="Network"]').attr('disabled','disabled');
        $('input[name="Network"]:checked').removeAttr('disabled');
      }
      else {
        $('#id_Export_Compartment_Name').val('');
        $('#id_Export_Compartment_Name').hide();
        /* code added by karthik for testing */
        $('#nextBtn').show();
        $('#generateExcel').hide();
        $('#id_Compartment').removeAttr('disabled');
        $('#id_Groups').removeAttr('disabled');
        /* Disabled for further use
        $('#id_Instance').removeAttr('disabled');
        $('#id_Block_Volume').removeAttr('disabled');
        */
        $('#id_NSG').removeAttr('disabled');
        $('#id_RM').removeAttr('disabled');
        $('input[name="Network"]').removeAttr('disabled');
      }
});


$('#id_Compartment').click(function(){
            if($(this).prop("checked") == true){
                options['compartment'] = true;
                $('#id_Groups').attr('disabled', 'disabled');
                $('#id_Groups').prop('checked', false);
                $('input[name="Network"]').attr('disabled', 'disabled');
                $('input[name="Network"]').prop('checked', false);
                $('#id_Instance').attr('disabled', 'disabled');
                $('#id_Instance').prop('checked', false);
                $('#id_NSG').attr('disabled', 'disabled');
                $('#id_NSG').prop('checked', false);
                $('#id_Block_Volume').attr('disabled', 'disabled');
                $('#id_Block_Volume').prop('checked', false);
                $('#id_Export_Compartment_Name').val('');
                $('#id_Instance_SSH_Public_Key').val('');
                $('#id_Instance_SSH_Public_Value').val('');
                $('#id_Export_Compartment_Name').hide();
                $('#id_Instance_SSH_Public_Key').hide();
                $('#id_Instance_SSH_Public_Value').hide();
                currNetwork = null;
            }
            else if($(this).prop("checked") == false){
                delete options['compartment'];
                $('#id_Groups').removeAttr('disabled');
                $('input[name="Network"]').removeAttr('disabled');
                if(!keyFile) {
                    $('input[name="Network"][value!="create_ntk"]').attr('disabled', 'disabled');
                }
                /* Disabled for further user
                $('#id_Instance').removeAttr('disabled');
                $('#id_Block_Volume').removeAttr('disabled');
                */
                $('#id_NSG').removeAttr('disabled');

            }
            toggleGenerateTFButton();
        });

if($('#id_Compartment').prop("checked") == true) {
    options['compartment'] = true;
    $('#id_Groups').attr('disabled', 'disabled');
    $('#id_Groups').prop('checked', false);
    $('input[name="Network"]').attr('disabled', 'disabled');
    $('#id_Instance').attr('disabled', 'disabled');
    $('#id_NSG').attr('disabled', 'disabled');
    $('#id_Block_Volume').attr('disabled', 'disabled');
 }

 if($('#id_RM').prop("checked") == false) {
    $('#id_Compartment_Name').hide();
    $('label[for="id_Compartment_Name"').hide();
    $('#info_rmcompartment').hide();
 }
 else {
    options['rm'] = true;
 }

 if($('input[name="Network"]:checked').val() == 'export_secrt') {
    $('#id_Export_Compartment_Name').show();
    options['network'] = true;
 }
 else {
    $('#id_Export_Compartment_Name').hide();
    if(!typeof $('input[name="Network"]:checked') == 'undefined') {
        options['network'] = true;
    }
 }

 $('#id_RM').click(function() {
    if($(this).prop("checked") == true) {
        options['rm'] = true;
        $('#id_Compartment_Name').show();
        $('label[for="id_Compartment_Name"').show();
        $('#info_rmcompartment').show();
    }
    else if($(this).prop("checked") == false) {
        delete options['rm'];
        $('#id_Compartment_Name').hide();
        $('#id_Compartment_Name').val('');
        $('label[for="id_Compartment_Name"').hide();
        $('#info_rmcompartment').hide();
    }
    toggleGenerateTFButton();
 });


if($('#id_Block_Volume').prop("checked") == true) {
    options['blockvolume'] = true;
}
$('#id_Block_Volume').click(function() {updateOptions('id_Block_Volume', 'blockvolume')});

if($('#id_Instance').prop("checked") == true) {
    options['instance'] = true;
}
else{
    $('#id_Instance_SSH_Public_Key').hide();
    $('label[for="id_Instance_SSH_Public_Key"').hide();
    $('#id_Instance_SSH_Public_Value').hide();
}

$('#id_Instance').click(function() {
    if($(this).prop("checked") == true) {
        options['instance'] = true;
        $('#id_Instance_SSH_Public_Key').show();
        $('label[for="id_Instance_SSH_Public_Key"').show();
        $('#id_Instance_SSH_Public_Value').show();
    }
    else if($(this).prop("checked") == false) {
        delete options['instance'];
        $('#id_Instance_SSH_Public_Key').hide();
        $('#id_Instance_SSH_Public_Key').val('');
        $('#id_Instance_SSH_Public_Value').val('');
        $('label[for="id_Instance_SSH_Public_Key"').hide();
        $('#id_Instance_SSH_Public_Value').hide();
    }
    toggleGenerateTFButton();
});

if($('#id_NSG').prop("checked") == true) {
    options['nsg'] = true;
}
$('#id_NSG').click(function() {updateOptions('id_NSG', 'nsg')});

if($('#id_Groups').prop("checked") == true) {
    options['groups'] = true;
}
$('#id_Groups').click(function() {updateOptions('id_Groups', 'groups')});

 function updateOptions(id, key) {
    if($('#'+id).prop("checked") == true) {
        options[key] = true;
    }
    else if($('#'+id).prop("checked") == false) {
        delete options[key];
    }
    toggleGenerateTFButton();
 }

 function toggleGenerateTFButton() {
    var keys = Object.keys(options);
    if(keys.length == 0) { $('#nextBtn').attr('disabled', 'disabled'); }
    else {$('#nextBtn').removeAttr('disabled');}
 }
