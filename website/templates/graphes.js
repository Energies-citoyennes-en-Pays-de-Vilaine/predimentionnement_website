window.GRAPH_2D_STATIC = "2dimg"
window.generateForm = function(docid, graphType, params){
	slot = document.getElementById(docid)
	controls = null
	imgToPut = null
	if (graphType == GRAPH_2D_STATIC){
		imgdiv = document.createElement("div")
		imgdiv.className = "img singlegraphstatic"
		imgToPut = document.createElement("img")
		imgToPut.src = "/sims/graphs/ie2"
		imgToPut.class = "singlegraphstatic"
		controls = document.createElement("div")
		controls.className = "singlegraphstatic controls"
		imgdiv.appendChild(imgToPut)
		slot.appendChild(imgdiv)
		slot.appendChild(controls)
	}
	function actualize(){
		console.log("change")
		values = []
		for (param of params){
			if (param.valueType == "bool")
			{
				elem = document.getElementById(param.paramName)
				values.push(param.paramName + "=" + elem.checked)
				continue
			}
			elem = document.getElementById(param.paramName)
			values.push(param.paramName + "=" + elem.value)
		}
		imgToPut.src = "/sims/graphs/ie2?" + values.join("&")
	}
	for (param of params){
		if (param.valueType == "int"){
			div = document.createElement("div")
			divtext = document.createElement("span")
			divtext.innerText = param.description
			input = document.createElement("input")
			input.type = param.formType
			input.value = param.defaultValue
			input.id = param.paramName
			input.addEventListener("change", actualize)
			div.appendChild(divtext)
			div.appendChild(input)
			controls.appendChild(div)
		}
		if (param.valueType == "float"){
			div = document.createElement("div")
			divtext = document.createElement("span")
			divtext.innerText = param.description
			input = document.createElement("input")
			input.type = param.formType
			input.value = param.defaultValue
			input.step = 0.01
			input.id = param.paramName
			input.addEventListener("change", actualize)
			div.appendChild(divtext)
			div.appendChild(input)
			controls.appendChild(div)
		}
		if (param.valueType == "bool"){
			div = document.createElement("div")
			divtext = document.createElement("span")
			divtext.innerText = param.description
			input = document.createElement("input")
			input.type = param.formType
			input.checked = param.defaultValue
			input.step = 0.01
			input.id = param.paramName
			input.addEventListener("change", actualize)
			div.appendChild(divtext)
			div.appendChild(input)
			controls.appendChild(div)
		}
		if (param.valueType == "date"){
			div = document.createElement("div")
			divtext = document.createElement("span")
			divtext.innerText = param.description
			input = document.createElement("input")
			input.type = param.formType
			input.value = param.defaultValue
			input.id = param.paramName
			input.addEventListener("change", actualize)
			div.appendChild(divtext)
			div.appendChild(input)
			controls.appendChild(div)
		}
	}
}
window.setIntParam = function(paramName, description, defaultValue = 5, formType = "number")
{
	return {paramName, description, defaultValue, formType, valueType : "int"}
}
window.setFloatParam = function(paramName, description, defaultValue = 5.1, formType = "number")
{
	return {paramName, description, defaultValue, formType, valueType : "float"}
}
window.setBoolParam = function(paramName, description, defaultValue = true, formType = "checkbox")
{
	return {paramName, description, defaultValue, formType, valueType : "bool"}
}
window.setDateParam = function(paramName, description, defaultValue = "2020-01-01", formType = "date")
{
	return {paramName, description, defaultValue, formType, valueType : "date"}
}