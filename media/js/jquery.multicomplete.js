function renderMultistringTable (containerId,arrayOfStrings) {
  tblId = containerId + "_tbl"
  resStr = "";
  valStr = '[';
  for ( var i = 0; i < arrayOfStrings.length; i ++ ) {
  	resStr += arrayOfStrings [ i ] + ";";
  	valStr += "\'" + arrayOfStrings [ i ] + "\'";
  	if ( i != arrayOfStrings.length - 1 )
  	  valStr +=',';
  }
  valStr += ']';
  r = "<table id=\"" + tblId + "\" alt=\"" + valStr +  "\">";
  idNum = 0;
  for (var i in arrayOfStrings) {
  	s = arrayOfStrings [ i ];
    idNum ++; strId = containerId + "_tbl_elem_" + idNum;
    r += "<tr id=\"" + strId + "\">" + 
    		"<td>" + s + "</td>" +
    		"<td><img src=\"/media/utils/images/delete.png\" onclick=\"removeFromMultistringTable('" + containerId + "','" + s + "')\"></img></td>" +
    	 "</tr>";
  }
  r += "</table>";
  inputId = containerId + "_id_input";
  resInputId = containerId + "_res";
  r += "<input name=\""+resInputId+"\"type=\"hidden\" id=\""+resInputId+"\"></input>";
  $('#' + containerId ).html(r);
  $('#' + inputId ).val("");
  $('#' + resInputId ).val(resStr);
}

function getFromMultistringTable (containerId) {
  return eval ( $('#'+containerId+"_tbl").attr ("alt") );
}

function removeFromMultistringTable (containerId, s) {
  arr = getFromMultistringTable (containerId);
  res = [];
  var j = 0;
  for ( var i in arr )
    if ( arr[i] != s )
	    res [j++] = arr[i];
  renderMultistringTable ( containerId, res )
}

function validateSymbolsForMultistringTable (s) {
  if ( !s )
    return false;
  for ( var i in s )
  {
    if ("\"\'<>#&".indexOf(s[i])>=0)
      return false;
  }
  return true;
}

function addToMultistringTable (containerId, s) {
  if (validateSymbolsForMultistringTable(s)) {
	  arr = getFromMultistringTable (containerId);
	  var flagNew = true;
	  for ( var i in arr )
	    if(arr[i]==s)
	      flagNew = false;
	  if ( flagNew ) {
		arr[arr.length] = s
	  	renderMultistringTable ( containerId, arr )
	  }
	}
}
