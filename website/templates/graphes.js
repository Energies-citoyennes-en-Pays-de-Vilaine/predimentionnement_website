window.GRAPH_2D_STATIC = "2dimg"
window.GRAPH_2D_DYNAMIC = "2dint"
window.GRAPH_3D_DYNAMIC = "3dint"
window.generateForm = function(docid, graphType, params, actualize){
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
	else if (graphType == GRAPH_2D_DYNAMIC)
	{
		controls = document.createElement("div")
		controls.className = "singlegraphstatic controls"
		slot.appendChild(controls)
	}
	else if (graphType == GRAPH_3D_DYNAMIC)
	{
		controls = document.createElement("div")
		controls.className = "singlegraphstatic controls"
		slot.appendChild(controls)
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
			input.addEventListener("change", actualize(params))
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
			input.addEventListener("change", actualize(params))
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
			input.addEventListener("change", actualize(params))
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
			input.addEventListener("change", actualize(params))
			div.appendChild(divtext)
			div.appendChild(input)
			controls.appendChild(div)
		}
		if (param.valueType == "radio"){
			div = document.createElement("div")
			divtext = document.createElement("span")
			divtext.innerText = param.description
			div.appendChild(divtext)
			console.log(param.choices)
			for (let choice of Object.keys(param.choices)){
				inputWrapper = document.createElement("div")
				input = document.createElement("input")
				input.type = param.formType
				input.value = param.choices[choice].index
				if (param.choices[choice].index == param.defaultValue)
					input.checked = true
				input.name = param.paramName
				input.addEventListener("change", actualize(params))
				label = document.createElement("label")
				label.innerText = param.choices[choice].name
				inputWrapper.appendChild(input)
				inputWrapper.appendChild(label)
				div.appendChild(inputWrapper)
			}
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
window.setEnumParam = function(paramName, description, choices, defaultValue = 0, formType = "radio")
{
	return {paramName, description, choices,defaultValue, formType, valueType : "radio"}
}