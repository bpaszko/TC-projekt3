const linksPerPage = 10;


function loadPhotosHistory() {
	var urlParams = new URLSearchParams(window.location.search);
	var pageNumber = getPageNumber(urlParams);
	var maxPageNumber = getMaxPageNumber();
	pageNumber = Math.min(pageNumber, maxPageNumber);
	pageNumber = Math.max(pageNumber, 1);
	loadList(pageNumber);
	makePaginator(pageNumber, maxPageNumber);
}


function loadList(pageNumber) {
	var linksList = getLinksList(pageNumber);
	makeList(linksList, pageNumber);
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


function getLinksList(pageNumber) {
	var linksList = ['img1','img2','img3','img4','img5','img6','img7','img8','img9','img10','img11','img12','img13','img14','img15','img16','img17','img18','img19','img20','img21','img22','img23','img24','img25','img26','img27','img28','img29','img30','img31'];
	var startIndex = (pageNumber - 1) * linksPerPage;
	return linksList.slice(startIndex, startIndex + linksPerPage);
}


function makeList(array, pageNumber) {
    var list = document.createElement('ol');
	list.start = (pageNumber - 1) * linksPerPage + 1;
	
	array.forEach(elem => {
		var item = document.createElement('li');
		var url = document.createElement('a');
		url.innerHTML = elem;
		url.href = elem;
		item.appendChild(url);
        list.appendChild(item);
	});
	
	var links = document.getElementById('links');
	links.innerHTML = '';
    links.appendChild(list);
}


function makePaginator(pageNumber, maxPageNumber) {
	Pagination.Init(document.getElementById('pagination'), {
        size: maxPageNumber, // pages size
        page: pageNumber,    // selected page
        step: 3              // pages before and after current
    });
	
	Pagination.PageChanged = function() {
		loadList(Pagination.page);
	};
}