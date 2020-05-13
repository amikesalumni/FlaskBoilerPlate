
//this function sends data to the python code
function post(data) {
   return $.ajax({
    url: "/myFunc", // location to which the request is sent
    type: "POST", // requests that the website accepts data
    data: data, // the data for the request to accept
    processData: false,
    contentType: false,
    complete: function () {
      console.log("done")
    }
  });
}

//this function listens for a file upload and sends the data then downloads it when its done
document.getElementById("file").onchange = function () {
	console.log("file received");
  var $form = document.getElementById("uploadForm");
  var file = document.getElementById('file').files[0];
  var formData = new FormData();
  formData.append('file', file);
  fileSize = file.size / 1000000;
  console.log("file size", fileSize);
  res = post(formData);
};

//this function sends data to the python code
function param(data) {
  return $.ajax({
   url: "/parameters", // location to which the request is sent
   type: "POST", // requests that the website accepts data
   data: data, // the data for the request to accept
   processData: false,
   contentType: false,
   complete: function () {
     console.log("done")
   }
 });
}

// this function will ultimately cause the TPD functions to refire when parameters are changed
document.getElementById("update").onclick = function (){
  console.log("update fired");
  var formData = new FormData();
  formData.append('TPDs',document.getElementById("TPDs").value)
  formData.append('Ars',document.getElementById("Ars").value)
  formData.append('Are',document.getElementById("Are").value)
  formData.append('wf',document.getElementById("wf").value)
  formData.append('SM',document.getElementById("SM").value)
  formData.append('RF',document.getElementById("RF").value)
  formData.append('MA',document.getElementById("MA").value)
  formData.append('SA',document.getElementById("SA").value)
  pass = param(formData)
  console.log("update complete");
}

function result() {
  return $.ajax({
    url: "/result",
    type: "POST",
    processData: false,
    contentType: false,
    complete: function () {
      console.log("done")
    }
  });
}

document.getElementById("test").onclick = function () {
  console.log("test fired")
  testit = result()
  console.log("test complete")
}
/*
//this function sends data to the python code
function rect() {
  return $.ajax({
   url: "/counter", // location to which the request is sent
   type: "GET", // requests that the website accepts data
   data: data, // the data for the request to accept
   processData: false,
   contentType: false,
   complete: function () {
     console.log("done")
   }
 });
}
*/

/*
//this will download the file
function downloadCSV(csvString) {
  var blob = new Blob([csvString]);
  if (window.navigator.msSaveOrOpenBlob){
    window.navigator.msSaveBlob(blob, "filename.csv");
  }
  else {
    var a = window.document.createElement("a");

    a.href = window.URL.createObjectURL(blob, {
      type: "text/plain"
    });
    a.download = "filename.csv";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }
}
*/