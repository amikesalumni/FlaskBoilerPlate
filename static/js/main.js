
//this function sends data to the python code
function post(data) {
  return $.ajax({
    url: "/myFunc",
    type: "POST",
    data: data,
    processData: false,
    contentType: false,
    complete: function () {
      console.log("done")
    }
  });
}




//this function listens for a file upload and sends the data then downloads it when its done
document.getElementById("file").onchange = async function () {
	console.log("got file");
  var $form = document.getElementById("uploadForm")
  var file = document.getElementById('file').files[0];
  var formData = new FormData();
  formData.append('file', file);
  fileSize = file.size / 1000000;
  console.log("file size", fileSize);

  res = await post(formData);

  console.log(res);
	
  downloadCSV(res);

};


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