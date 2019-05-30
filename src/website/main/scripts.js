var imgLink;


function getImgLink() {
	if (imgLink == null) {
		imgLink = document.getElementById('link_id');
	}
	return imgLink;
}


function previewFile(){
	var preview = document.querySelector('img');
	var file    = document.querySelector('input[type=file]').files[0];
	var filePath = file.name;
	var allowedExtensions = /(\.jpg|\.jpeg|\.png)$/i;
	
	if(!allowedExtensions.exec(filePath)){
        alert("Please upload file having extensions .jpeg/.jpg/.png only.");
        preview.src = "";
        return false;
    }
	
	var reader  = new FileReader();

	reader.onload = function () {
		var image = new Image;
		image.onload = function() {
			var img_w = image.width;
			var img_h = image.height;
			
			if(img_w > 75 || img_h > 75) {
				alert("Photo should be max 75px x 75px.");
				image.src = "";
				preview.src = "";
				return false;
			}
			
			preview.setAttribute('w', img_w);
			preview.setAttribute('h', img_h);
		};
		image.src = reader.result;
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
	var image = document.querySelector('img');
	
	if(image.currentSrc == "") {
		alert("Please upload photo.");
		return false;
	}
	
	h = image.getAttribute('h');
	w = image.getAttribute('w');
	z = getZoom();
	sendBase64ToServer(image.src, h, w, z);
}


function getZoom() {
	var radioForm = document.getElementById('radioForm');
	return radioForm.elements['zoom'].value || 2;
}


function sendBase64ToServer(base64, h, w, z) {
	var httpPost = new XMLHttpRequest(),
		path = 'https://nsoaoib0c8.execute-api.us-east-1.amazonaws.com/dev/run_model',
		data = JSON.stringify({image: base64, height: h, width: w, zoom: z});
	httpPost.onreadystatechange = function(err) {
			if (httpPost.readyState == 4 && httpPost.status == 200){
				console.log(httpPost.responseText);
				processResponse(httpPost.responseText);
			} else {
				console.log(err);
				getImgLink().innerHTML = err;
			}
	   };
	// Set the content type of the request to json since that's what's being sent
	httpPost.open("POST", path, true);
	httpPost.setRequestHeader('Content-Type', 'application/json');
	httpPost.send(data);
};


function processResponse(responseText) {
	var imgUrlObject = JSON.parse(responseText);
	var imgUrl = imgUrlObject["img_url"];
	getImgLink().innerHTML = imgUrl;
	getImgLink().href = imgUrl;
	var enlargedImg = document.getElementById('img_id');
	enlargedImg.src = imgUrl;
}