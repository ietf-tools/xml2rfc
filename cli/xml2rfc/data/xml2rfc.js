var toc = document.getElementById("toc");
var tocToggle = toc.querySelector("h2");
var tocNav = toc.querySelector("nav");

// mobile menu toggle
tocToggle.onclick = function(event) {
    if (window.innerWidth < 1024) {
	var tocNavDisplay = tocNav.currentStyle ? tocNav.currentStyle.display : getComputedStyle(tocNav, null).display;
	if (tocNavDisplay == "none") {
	    tocNav.style.display = "block";
	} else {
	    tocNav.style.display = "none";
	}
    }
}

// toc anchor scroll to anchor
tocNav.addEventListener("click", function (event) {
    event.preventDefault();
    if (event.target.nodeName == 'A') {
	if (window.innerWidth < 1024) {
	    tocNav.style.display = "none";
	}
	var href = event.target.getAttribute("href");
	var anchorId = href.substr(1);
	var anchor =  document.getElementById(anchorId);
	anchor.scrollIntoView(true);
	window.history.pushState("","",href);
    }
});

// switch toc mode when window resized
window.onresize = function () {
    if (window.innerWidth < 1024) {
	tocNav.style.display = "none";
    } else {
	tocNav.style.display = "block";
    }
}
