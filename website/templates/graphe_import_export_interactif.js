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
	"begin" : "2021-01-01",
	"end"   : "2021-02-01"
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

function callback(params){
	return (response) => 
	{
		responseData = JSON.parse(response)
		labeledKeys = [{
			dataApiName : "imported_energy",
			label: "import (Wh/foyer)",
			color:'rgb(75, 192, 192)',
		},
		{
			dataApiName : "exported_energy",
			label: "export (Wh/foyer)",
			color:'rgb(75, 192, 192)',
		}
		]
		console.log({responseData})
		if (window.plotData == undefined)
			createChart(responseData, "mcanvas", labeledKeys)
		else
			updateChart(responseData, "mcanvas", labeledKeys)
		dataviewer = document.getElementById("resultslot")
		sendRequest("/sims/api/results/agglomerated_result", params, () => {
			dataviewer.innerHTML = ""
			responseJSON = JSON.parse(xhr.response)
			for (element of Object.keys(responseJSON))
			{
				div = document.createElement("div")
				div.innerText = element + " : " + responseJSON[element].toFixed(2)	
				div.style = "padding-right:10px; display: block;"
				dataviewer.appendChild(div)
			}
		})
	}
}

sendRequest("/sims/api/ie", params, callback(params) )
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
		sendRequest("/sims/api/ie", values, callback(values) )
	}
}
window.addEventListener("load", function(){
	window.generateForm("import_export", window.GRAPH_2D_DYNAMIC,
	[
		window.setFloatParam("solar_power", "Energie annuelle de la production solaire(MWh/an) ", 1.31 * 8760),
				window.setFloatParam("wind_tubine_prod", "Energie annuelle de la production éolienne (MWh/an) ", 0.728 * 8760 * 19),
				window.setFloatParam("bioenergy_power", "Energie annuelle de la production bioénergétique (MWh/an) ", 0.69 * 8760),
				window.setBoolParam("has_battery", "Stockage présent ", false),
				window.setFloatParam("battery_capacity", "Stockage installé (MWh) ", 2),
				window.setBoolParam("has_flexibility", "Flexibilité présente ?", false),
				window.setFloatParam("flexibility_ratio", "Fexibilité des utilisateurs (en % de leur consommation)", 5),
				window.setFloatParam("res_ratio", "Pourcentage de la consommation 'RES' actuelle pour la simulation", 100.0),
				window.setFloatParam("ent_ratio", "Pourcentage de la consommation 'ENT' actuelle pour la simulation", 100.0),
				window.setFloatParam("pro_ratio", "Pourcentage de la consommation 'PRO' actuelle pour la simulation", 100.0),
				window.setBoolParam("has_ra", "Moyenne glissante ", true),
				window.setFloatParam("ra_period", "Période sur laquelle la moyenne glissante est effectuée(H)", 24),
				window.setDateParam("begin", "Date de départ de la simulation ", "2021-01-01"),
				window.setDateParam("end", "Date de fin de la simulation ", "2022-01-01"),
				window.setBoolParam("slice_after_sim", "Simuler sur toutes les données", true),
				window.setBoolParam("scale_before_slice", "Mise à l'échelle sur toutes les données", false),
	], actualize)
})