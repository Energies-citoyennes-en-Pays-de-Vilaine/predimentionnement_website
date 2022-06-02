window.chart = undefined
window.plotData = undefined
window.indexes = undefined
function sendRequest(url, requestParams, callback){
	xhr = new XMLHttpRequest()
	xhr.open("POST", url, true)
	xhr.onload = function(){
		callback(xhr.response)
	}
	xhr.withcredentials = true
	xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
	params_url = []
	for (key of Object.keys(requestParams)){
		params_url.push(key + "=" + requestParams[key])
	}
	xhr.send(params_url.join("&"))
}



function createChart(data, name){
	window.plotData = []
	z_data = []
	x_data = []
	y_data = []
	for (x of Object.keys(data)){
		z_data_to_add = []
		x_data_to_add = []
		y_data_to_add = []
		for (y of Object.keys(data[x]))
		{
			x_data_to_add.push(x)
			y_data_to_add.push(y)
			z_data_to_add.push(data[x][y])
		}
		x_data.push(x_data_to_add)
		y_data.push(y_data_to_add)
		z_data.push(z_data_to_add)
	}
	window.plotData.push({
		type : "surface",
		x    : x_data,
		y    : y_data,
		z    : z_data
	})
	console.log(window.plotData)
	layout = {
		title:"import et export d'energie par habitant"
	}
	config = {
		responsive: true
	}
	Plotly.newPlot(name, plotData, layout, config);
}

function updateChart(data, name){
	z_data = []
	for (x of Object.keys(data)){
		z_data_to_add = []
		for (y of Object.keys(data[x]))
		{
			z_data_to_add.push(data[x][y])
		}
		z_data.push(z_data_to_add)
	}
	window.plotData[0].x = Object.keys(data)
	window.plotData[0].y = Object.keys(data[Object.keys(data)[0]])
	window.plotData[0].z = z_data
	Plotly.redraw(name)
}

function callback(response){
	responseData = JSON.parse(response)
	console.log(responseData)
	if (window.plotData == undefined)
		createChart(responseData, "mcanvas")
	else
		updateChart(responseData, "mcanvas")
}

sendRequest("/sims/api/results/data", {}, callback )
function actualize(params){
	return function(){
		values = []
		for (param of params){
			if (param.valueType == "bool")
			{
				elem = document.getElementById(param.paramName)
				values [param.paramName] = elem.checked
				continue
			}
			elem = document.getElementById(param.paramName)
			values [param.paramName] = elem.value
		}
		sendRequest("/sims/api/results/data", values, callback )
	}
}

window.addEventListener("load", function(){
	sendRequest("/sims/api/results/index", {}, (response)=>{
		console.log(response)
	})
	window.generateForm("graph", window.GRAPH_3D_DYNAMIC,
	[

	], actualize)
})