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
	for (let key of labeledKeys)
	{	
		dataApiName = key.dataApiName,
		window.plotData.push({
			keyName : dataApiName,
			type : "scatter",
			mode : "lines",
			name : key.label,
			x    : data["dates"],
			y    : data[dataApiName]
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
	for (let key of labeledKeys)
	{	
		dataApiName = key.dataApiName
		for (let i  in window.plotData){
			if (window.plotData[i].keyName == dataApiName){
				window.plotData[i].x = data["dates"]
				window.plotData[i].y = data[dataApiName]
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

sendRequest("/sims/api/ie", params, callback )
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
		sendRequest("/sims/api/ie", values, callback )
	}
}
window.addEventListener("load", function(){
	window.generateForm("import_export", window.GRAPH_2D_DYNAMIC,
	[
		window.setFloatParam("solar_power", "Puissance moyenne de la production solaire (MW) ", 3.44),
		window.setFloatParam("bioenergy_power", "Puissance moyenne de la production bio-énergétique (MW) ", 2.07),
		window.setFloatParam("wind_tubine_prod", "Puissance moyenne de la production d'une éolienne (MW) ", 0.577),
		window.setIntParam("wind_turbine_count", "Nombre d'éoliennes ", 13),
		window.setBoolParam("has_battery", "Stockage présent ", false),
		window.setFloatParam("battery_capacity", "Stockage installé (MWh) ", 2),
		window.setBoolParam("has_ra", "Moyenne glissante ", true),
		window.setFloatParam("ra_period", "Période sur laquelle la moyenne glissante est effectuée(H)", 24),
		window.setDateParam("begin", "Date de départ de la simulation ", "2020-01-01"),
		window.setDateParam("end", "Date de fin de la simulation ", "2020-02-01"),
		window.setBoolParam("slice_after_sim", "Simuler sur toutes les données", true),
		window.setBoolParam("has_flexibility", "Flexibilité présente ?", false),
		window.setFloatParam("flexibility_ratio", "Fexibilité des utilisateurs (en % de leur consommation)", 5)
	], actualize)
})