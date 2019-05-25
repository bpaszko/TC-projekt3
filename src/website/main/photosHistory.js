const linksPerPage = 10;
var paginatorCreated = false;


function loadPhotosHistory() {
	var urlParams = new URLSearchParams(window.location.search);
	var pageNumber = getPageNumber(urlParams);
	loadList(pageNumber);
	var maxPageNumber = getMaxPageNumber();
	pageNumber = Math.min(pageNumber, maxPageNumber);
	pageNumber = Math.max(pageNumber, 1);
}


function loadList(pageNumber) {
	getLinksList(pageNumber, linksPerPage);
}


function getPageNumber(urlParams) {
	var pageNumber = urlParams.get('page');
	pageNumber = parseInt(pageNumber, 10);
	
	if(isNaN(pageNumber)) {
		pageNumber = 1;
	}
	else {
		pageNumber = Math.floor(pageNumber);
	}
	
	return pageNumber;
}


function getMaxPageNumber() {
	return 4;
}


function getLinksList(pageNumber, linksPerPage) {
	var httpPost = new XMLHttpRequest(),
		path = 'https://nsoaoib0c8.execute-api.us-east-1.amazonaws.com/dev/get_history',
		data = JSON.stringify({pageNumber: pageNumber, linksPerPage: linksPerPage});
	httpPost.onreadystatechange = function(err) {
			if (httpPost.readyState == 4 && httpPost.status == 200){
				console.log(httpPost.responseText);
				processResponse(httpPost.responseText, pageNumber);
			} else {
				console.log(err);
			}
	   };
	// Set the content type of the request to json since that's what's being sent
	httpPost.open("POST", path, true);
	httpPost.setRequestHeader('Content-Type', 'application/json');
	httpPost.send(data);
}

function processResponse(responseText, pageNumber) {
	var historyObject = JSON.parse(responseText);
	makeList(historyObject["history"], pageNumber);	
	makePaginator(pageNumber, historyObject["sites"]);
}


function makeList(array, pageNumber) {
    var list = document.createElement('ol');
	list.start = (pageNumber - 1) * linksPerPage + 1;
	
	array.forEach(elem => {
		var item = document.createElement('li');
		var aTag = document.createElement('a');
		var url = elem[1];
		aTag.innerHTML = url;
		aTag.href = url;
		item.appendChild(aTag);
        list.appendChild(item);
	});
	
	var links = document.getElementById('links');
	links.innerHTML = '';
    links.appendChild(list);
}


function makePaginator(pageNumber, maxPageNumber) {
	if (paginatorCreated) {
		return;
	}
	
	Pagination.Init(document.getElementById('pagination'), {
        size: maxPageNumber, // pages size
        page: pageNumber,    // selected page
        step: 3              // pages before and after current
    });
	
	Pagination.PageChanged = function() {
		loadList(Pagination.page);
	};
	
	paginatorCreated = true;
}