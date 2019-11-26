function search(searchfield) {
	txt = searchfield.value;
	if (txt == "") {
		reallyclear()
	}
	else {
		xhttp = new XMLHttpRequest();
		xhttp.onreadystatechange = searchresult
		xhttp.open("GET","/api/search?max=5&query=" + encodeURIComponent(txt), true);
		xhttp.send();
	}
}


function html_to_fragment(html) {
	var template = document.createElement("template");
	template.innerHTML = resulthtml;
	return template.content;
}


const results_artists = document.getElementById("searchresults_artists");
const results_tracks = document.getElementById("searchresults_tracks");
const searchresultwrap = document.getElementById("resultwrap");

var resulthtml = `
<tr>
	<td class="image"></td>
	<td>
		<span></span><br/>
		<span></span>
	</td>
</tr>
`
const oneresult = html_to_fragment(resulthtml).firstElementChild;




function searchresult() {
	if (this.readyState == 4 && this.status == 200 && document.getElementById("searchinput").value != "") {
		// checking if field is empty in case we get an old result coming in that would overwrite our cleared result window
		var result = JSON.parse(this.responseText);
		var artists = result["artists"].slice(0,5)
		var tracks = result["tracks"].slice(0,5)

		while (results_artists.firstChild) {
			results_artists.removeChild(results_artists.firstChild);
		}
		while (results_tracks.firstChild) {
			results_tracks.removeChild(results_tracks.firstChild);
		}

		for (var i=0;i<artists.length;i++) {
			name = artists[i]["name"];
			link = artists[i]["link"];
			image = artists[i]["image"];

			var node = oneresult.cloneNode(true);
			node.setAttribute("onclick","goto(" + link + ")");
			node.children[0].style.backgroundImage = "url('" + image + "')";
			node.children[1].children[0].innerHTML = name;

			results_artists.appendChild(node);
		}
		for (var i=0;i<tracks.length;i++) {

			artists = tracks[i]["artists"].join(", ");
			title = tracks[i]["title"];
			link = tracks[i]["link"];
			image = tracks[i]["image"];

			var node = oneresult.cloneNode(true);
			node.setAttribute("onclick","goto(" + link + ")");
			node.children[0].style.backgroundImage = "url('" + image + "')";
			node.children[1].children[0].innerHTML = artists;
			node.children[1].children[2].innerHTML = title;

			results_tracks.appendChild(node);
		}
		searchresultwrap.classList.remove("hide")

	}
}

function clearresults() {
	window.setTimeout(reallyclear,500)
}
function reallyclear() {
	searchresultwrap.classList.add("hide")
}

function goto(link) {
	window.location = link
}
