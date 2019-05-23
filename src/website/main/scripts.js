function previewFile(){
   var preview = document.querySelector('img');
   var file    = document.querySelector('input[type=file]').files[0];
   var reader  = new FileReader();

   reader.onload = function () {
      var image = new Image;
      image.onload = function() {
         preview.setAttribute('w', image.width)
         preview.setAttribute('h', image.height)
      };
      image.src = reader.result
      preview.src = reader.result;
   }

   if (file) {
	   reader.readAsDataURL(file);
   } 
   else {
	   preview.src = "";
   }
}


function accessModel(){
   var image = document.querySelector('img')
   h = image.getAttribute('h')
   w = image.getAttribute('w')
   sendBase64ToServer(image.src, h, w);
}


var sendBase64ToServer = function(base64, h, w){
   var txt = document.getElementById('test_id')
   var httpPost = new XMLHttpRequest(),
       path = 'https://nsoaoib0c8.execute-api.us-east-1.amazonaws.com/dev/run_model',
       data = JSON.stringify({image: base64, height: h, width: w});
   httpPost.onreadystatechange = function(err) {
           if (httpPost.readyState == 4 && httpPost.status == 200){
               console.log(httpPost.responseText);
               txt.innerHTML = httpPost.responseText;
           } else {
               console.log(err);
               txt.innerHTML = err;
           }
       };
   // Set the content type of the request to json since that's what's being sent
   httpPost.open("POST", path, true);
   httpPost.setRequestHeader('Content-Type', 'application/json');
   httpPost.send(data);
};

