/*
javascript vs2
11/10/2011
by Miwa Yagi
*/



// ================================================================ copyright year 		
$(document).ready(

function copyrightYear()		
{
	var d=new Date();
	document.getElementById("crYear").innerHTML = (d.getFullYear());		
}

);

// ================================================================ photo slider
	
var theInt = null;
var $crosslink, $navthumb;
var curclicked = 0;

theInterval = 
function(cur)
{
	clearInterval(theInt);
	
	if( typeof cur != 'undefined' )
	curclicked = cur;
	
	$crosslink.removeClass("active-thumb");
	$navthumb.eq(curclicked).parent().addClass("active-thumb");
	$(".stripNav ul li a").eq(curclicked).trigger('click');
	
	theInt = setInterval(
	function()
	{
		$crosslink.removeClass("active-thumb");
		$navthumb.eq(curclicked).parent().addClass("active-thumb");
		$(".stripNav ul li a").eq(curclicked).trigger('click');
		curclicked++;
		if( 5 == curclicked )
		curclicked = 0;
	
	}, 5000);
};


$(function()
{	
	$("#main-photo-slider").codaSlider();
	
	$navthumb = $(".nav-thumb");
	$crosslink = $(".cross-link");
	
	$navthumb.click(
		function() 
		{
			var $this = $(this);
			theInterval($this.parent().attr('href').slice(1) - 1);
			return false;
		}
	);	
	theInterval();
});

// ========================================================================== tabs
$(document).ready(
	function()
	{
	  	$(".chronuxTabs").hover(
			function()
			{
				$(this).addClass("chronuxHover");
			},
			function()
			{
				$(this).removeClass("chronuxHover");
			});
	}
	
);	

//flash new window pop-up
function imgObj(id,url)
{
	this.id = id;
	this.url = url;
}

function navigationLink(value, id)
{	
	this.value = value;
	this.id = id;
}

var upload = "Chronux++ - Upload data";
var explore = "Chronux++ - Explore data";
var analyze = "Chronux++ - Analyze data";
var discover = "Chronux++ - Discover patterns";

var linkArray = [];
linkArray [0] = new navigationLink(upload,"chronuxUpload");
linkArray [1] = new navigationLink(explore,"chronuxExplore");
linkArray [2] = new navigationLink(analyze,"chronuxAnalyze");
linkArray [3] = new navigationLink(discover,"chronuxDiscover");

function pTabs()
{
	for (i=0; i<linkArray.length; i++)
		{	
			if (document.getElementById("chronuxPageTitle").innerHTML == linkArray[i].value)
			{	
				 document.getElementById(linkArray[i].id).setAttribute("class", "chronuxTabs currentTab");
				break;
			}
		}
}







