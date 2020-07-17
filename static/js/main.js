// global storage variable
var file = 0

//this function sends data to the python code
function post(data) {
  return $.ajax({
   url: "/fileupload", // location to which the request is sent
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
  var formData = new FormData();
  file = document.getElementById('file').files[0];
  formData.append('file', file);
  fileSize = file.size / 1000000;
  console.log("file size", fileSize);
  res = post(formData);
};

function get_params() {
  var formData = new FormData();
  formData.append('file', file)
  console.log('params grabbed')
  formData.append('TPDs',document.getElementById("TPDs").value);
  formData.append('TPDe',document.getElementById("TPDe").value);
  formData.append('Ars',document.getElementById("Ars").value);
  formData.append('Are',document.getElementById("Are").value);
  formData.append('wf',document.getElementById("wf").value);
  formData.append('SM',document.getElementById("SM").value);
  formData.append('RF',document.getElementById("RF").value);
  formData.append('MA',document.getElementById("MA").value);
  formData.append('SA',document.getElementById("SA").value);
  return formData
};

document.getElementById("plot").onclick = function () {
  console.log("plot fired");
  parameters = get_params();
  plotit = plot(parameters);
};

function plot(data){
  return $.ajax({
    url: "/plot",
    type: "POST",
    cache: false,
    data: data,
    success: function(spec) {
      // splitter takes the disconnects the string returned by the presence of } {. The brackets are readded in the for loop.
      // The plots are then inserted w/ VegaEmbed
      var splitter = spec.split('} {');
      var i;
      for (i=0; i<splitter.length; i++){
        if (i==0){
          graph = JSON.parse(splitter[i]+'}')
        } else if (i==splitter.length-1){
          graph = JSON.parse('{'+splitter[i])
        } else {
          graph = JSON.parse('{'+splitter[i]+'}')
        }
        vegaEmbed("#vis"+i.toString(), graph)
        .then(result => console.log(result))
        .catch(console.warn);
      }
    },
    processData: false,
    contentType: false,
    complete: function () {
      console.log("done")
    }
  });
}

document.getElementById("calculate").onclick = function () {
  console.log("calculate fired");
  parameters = get_params();
  plotit = calculate(parameters);
};

function calculate(data){
  return $.ajax({
    url: "/calculate",
    type: "POST",
    cache: false,
    data: data,
    success: function(something) {
      document.getElementById("p1").innerHTML = something
      console.log("this worked")
    },
    processData: false,
    contentType: false,
    complete: function () {
      console.log("done")
    }
  });
}


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