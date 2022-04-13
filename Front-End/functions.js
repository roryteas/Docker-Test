var jasonInit = {method: 'GET'}
async function getJason(){
    
    return fetch("portfolio.json",jasonInit)
      .then(response => response.json())
             
}

async function setVar(){
  var myList = await getJason();
  myList = myList.portfolio;
  console.log(myList)
  
  
  return myList
}

  
  // Builds the HTML Table out of myList.
  async function buildHtmlTable(selector) {

    var myList = await setVar();
    var columns = await addAllColumnHeaders(myList, selector);  

    
    for (var i = 0; i < myList.length; i++) {
      var row$ = $('<tr/>');
      
      for (var colIndex = 0; colIndex < columns.length; colIndex++) {
        var cellValue = myList[i][columns[colIndex]];

        if (cellValue == null) cellValue = "";
        row$.append($('<td/>').html(cellValue));
      }
      $(selector).append(row$);
    }
  }
  
  // Adds a header row to the table and returns the set of columns.
  // Need to do union of keys from all records as some records may not contain
  // all records.
  async function addAllColumnHeaders(myList, selector) {
    var columnSet = [];
    var headerTr$ = $('<tr/>');
  
    for (var i = 0; i < myList.length; i++) {
      var rowHash = myList[i];
      for (var key in rowHash) {
        if ($.inArray(key, columnSet) == -1) {
          columnSet.push(key);
          headerTr$.append($('<th/>').html(key));
        }
      }
    }
    columnSet.push("Gain/Loss");
    headerTr$.append($('<th/>').html("Gain/Loss"));
    $(selector).append(headerTr$);
  
    return columnSet;
  }

 async function update() {

  var stock = {"Stock":"", "Quantity":"", "Price":""}

  stock["Stock"] = (document.getElementById("stock-add").elements["stocksym"].value);
  stock["Quantity"] = (document.getElementById("stock-add").elements["quantityp"].value);
  stock["Price"] = (document.getElementById("stock-add").elements["pricep"].value);
  console.log(stock)
  var response = await fetch("Portfolio",{method :'POST', body: JSON.stringify(stock)})
  location.reload()

  }