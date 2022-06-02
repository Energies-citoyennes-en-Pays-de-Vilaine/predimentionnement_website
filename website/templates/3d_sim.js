window.chart = undefined
window.plotData = undefined

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

params = {
	"begin" : "2020-01-01",
	"end"   : "2020-02-01"
}

function createChart(data, name, labeledKeys){
	window.plotData = []
	z_data = []
	for (x of Object.keys(data)){
		z_data_to_add = []
		for (y of Object.keys(data[x]))
		{
			z_data_to_add.push(data[x][y])
		}
		z_data.push(z_data_to_add)
	}
	for (let key of labeledKeys)
	{	
		dataApiName = key.dataApiName,
		window.plotData.push({
			keyName : dataApiName,
			type : "surface",
			name : key.label,
			x    : Object.keys(data),
			y    : Object.keys(data[Object.keys(data)[0]]),
			z    : z_data
		})
		console.log(key,data[dataApiName])
	}
	layout = {
		title:"import et export d'energie par habitant"
	}
	config = {
		responsive: true
	}
	Plotly.newPlot(name, plotData, layout, config);
}

function updateChart(data, name, labeledKeys){
	z_data = []
	for (x of Object.keys(data)){
		z_data_to_add = []
		for (y of Object.keys(data[x]))
		{
			z_data_to_add.push(data[x][y])
		}
		z_data.push(z_data_to_add)
	}
	for (let key of labeledKeys)
	{	
		dataApiName = key.dataApiName
		for (let i  in window.plotData){
			if (window.plotData[i].keyName == dataApiName){
				window.plotData[i].x = Object.keys(data)
				window.plotData[i].y = Object.keys(data[Object.keys(data)[0]])
				window.plotData[i].z = z_data
			}
		}
	
		console.log(key,data[dataApiName])
	}
	Plotly.redraw(name)
}

function callback(response){
	responseData = JSON.parse(response)
	labeledKeys = [{
		dataApiName : "imported_energy",
		label: "import (W/habitant)",
		color:'rgb(75, 192, 192)',
	},
	{
		dataApiName : "exported_energy",
		label: "export (W/habitant)",
		color:'rgb(75, 192, 192)',
	}
	]
	console.log(responseData)
	if (window.plotData == undefined)
		createChart(responseData, "mcanvas", labeledKeys)
	else
		updateChart(responseData, "mcanvas", labeledKeys)
}

sendRequest("/sims/api/results/data", params, callback )
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
		sendRequest("/sims/api/", values, callback )
	}
}

window.addEventListener("load", function(){
	window.generateForm("graph", window.GRAPH_3D_DYNAMIC,
	[
		
	], actualize)
})