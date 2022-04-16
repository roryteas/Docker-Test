
//fetches portfolio JSON file
var jasonInit = {method: 'GET'}
async function getJason(){
    
    return fetch("portfolio.json",jasonInit)
      .then(response => response.json())
             
}

//fetches tickers from server
async function getTickers(){
  return fetch("Tickers")
  .then(response => response.json())
}

//wrapper for functions loading on pageload
async function load(){
  buildHtmlTable('#stockTable')
  fillDataList()  
  
}

//calls ticker fetch function and returns a list of tickers, for use in the dropdown
async function tickersHelper(){
  var tickerList = await getTickers()
  return tickerList
}

//returns the portfolio of stocks 
async function setList(){
  var myList = await getJason();
  portfolioList = myList.portfolio; 
  
  
  return portfolioList
}
  
  // Builds the HTML Table out of myList.
  async function buildHtmlTable(selector) {

    
    var portfolioList = await setList();
    var columns = await addAllColumnHeaders(portfolioList, selector);  

    
    for (var i = 0; i < portfolioList.length; i++) {
      var row$ = $('<tr/>');
      
      for (var colIndex = 0; colIndex < 4; colIndex++) {
        if (colIndex < 3){
          var cellValue = portfolioList[i][columns[colIndex]];
        }
        if (colIndex == 3){
          // Get gain/loss
          var cellValue = "Gainz"
        }
        if (cellValue == null) cellValue = "";
        row$.append($('<td/>').html(cellValue));
      }
      $(selector).append(row$);
    }
  }
  
  // Adds a header row to the table and returns the set of columns.
   
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

//Takes error message passed from server and adds error text to Span object on the page
function errorMessage(errorcode) {
  var error = document.getElementById("error")
  
  
      
      // Changing content and color of content
      if (errorcode == "Error - WRONGSTOCK"){
        console.log("ABC")
        error.textContent = "Please enter a valid stock symbol";
        error.style.color = "red";
      }

      if (errorcode == "Error - EMPTYFIELD"){
        console.log("ABC")
        error.textContent = "You must fill in all fields";
        error.style.color = "red";
      }

      if (errorcode == "Error - SHORT"){
        console.log("CBA")
        error.textContent = "Error - Short Selling not allowed";
        error.style.color = "red";
      }

      if (errorcode == "Error - BADPRICE"){
        console.log("CBA")
        error.textContent = "Price must be above 0";
        error.style.color = "red";
      }
      
  
}

 //actions when update button is clicked
 
async function buildStock(){
  var stock = {"Stock":"", "Quantity":"", "Price":""}
  stock["Stock"] = (document.getElementById("stock-add").elements["stocksym"].value);
  stock["Quantity"] = (document.getElementById("stock-add").elements["quantityp"].value);
  stock["Price"] = (document.getElementById("stock-add").elements["pricep"].value);

  return stock
}
 
async function update() {

  
   //creates a stock object to send to server
  stock =  JSON.stringify( buildStock())
  
  //post new stock object to server
  var resBody = await fetch("Portfolio",{method :'POST', body: stock})
    .then(response => response.text())
  
 
  //check for error text in the response
  if (resBody != ""){
    
    errorMessage(resBody)
  }
  else 
    var error = document.getElementById("error")
    error.textContent = ""
    var Table = document.getElementById("stockTable");
    Table.innerHTML = "";
    await buildHtmlTable('#stockTable')
  }

//fills datalist to populate the dropdown
async function fillDataList() {
  var optionList = await tickersHelper();
  console.log(optionList[0])
  var container = document.getElementById('stocksym'),
  i = 0,
  len = optionList.length,
  dl = document.createElement('datalist');

  dl.id = 'tickerList';
  for (; i < len; i += 1) {
      var option = document.createElement('option');
      option.value = optionList[i];
      dl.appendChild(option);
  }
  console.log(dl)
  container.appendChild(dl);
}



