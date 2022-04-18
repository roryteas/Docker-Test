
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
        if (colIndex < 1){
          var cellValue = portfolioList[i][columns[colIndex]];
          
        }
        else if (colIndex <2) {
          
          var num = parseFloat(portfolioList[i][columns[colIndex]]).toFixed(2);
          var cellValue = num
          
        }
        else if (colIndex <3) {
          
          var num = parseFloat(portfolioList[i][columns[colIndex]]).toFixed(2);
          var cellValue = "$".concat(String(num));
          
        }
        else if (colIndex <4) {
          
          var num = parseFloat(portfolioList[i][columns[colIndex]]).toFixed(2);
          var cellValue = String(num).concat("%");
          
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
 

 
async function update() {

  
   //creates a stock object to send to server
 // stock = buildStock()

  var stock = {"Stock":"", "Quantity":"", "Price":""}
  stock["Stock"] = (document.getElementById("stock-add").elements["stocksym"].value);
  stock["Quantity"] = (document.getElementById("stock-add").elements["quantityp"].value);
  stock["Price"] = (document.getElementById("stock-add").elements["pricep"].value);
  
  //post new stock object to server
  var resBody = await fetch("Portfolio",{method :'POST', body: JSON.stringify(stock)})
    .then(response => response.text())
  
 
  //check for error text in the response
  if (resBody != ""){
    
    errorMessage(resBody)
  }
  else 
    var error = document.getElementById("error");
    error.textContent = "";
    var Table = document.getElementById("stockTable");
    Table.innerHTML = "";
    await buildHtmlTable('#stockTable')
  }

async function getData() {


  //creates a stock object to send to server
// stock = buildStock()
  
  
  var stock = document.getElementById("stocksym").value;

  
  //post new stock object to server
  var resBody = await fetch("GetStats",{method :'POST', body: JSON.stringify(stock)})
    .then(response => response.json())
  

  //check for error text in the response
  await stockStats(resBody)
  await chart(resBody)
}
  
async function stockStats(resBody){
  var stats = resBody["stockStats"]

  var symbol = document.getElementById("Symbol")
  symbol.textContent = "Symbol: ".concat(document.getElementById("stocksym").value)

  var companyName = document.getElementById("Company Name")
  companyName.textContent = "Company Name: ".concat(stats["companyName"])

  var peRatio = document.getElementById("PE Ratio")
  peRatio.textContent = "PE Ratio: ".concat(stats["peRatio"])

  var marketCap = document.getElementById("Market Cap")
  marketCap.textContent = "Market Capitalisation: ".concat(stats["marketcap"])

  var yearHigh = document.getElementById("52Weekhigh")
  yearHigh.textContent = "52 Week High: ".concat(stats["week52high"])

  var yearlow = document.getElementById("52Weeklow")
  yearlow.textContent = "52 Week Low: ".concat(stats["week52low"])
}
async function chart(resBody) {

  var limit = resBody["stockChart"].length;   
  console.log(resBody)
  var data = [];
  var dataSeries = { type: "line" , xvaluetype : "dateTime"};
  var dataPoints = [];
  for (var i = 0; i < limit; i += 1) {
    var myDate = resBody["stockChart"][i]['date'];
    newDate = new Date(Date.parse(myDate))
    dataPoints.push({
      x: newDate,
      y: resBody["stockChart"][i]['close']
    })
  console.log(dataPoints)

    
  }
  dataSeries.dataPoints = dataPoints;
  data.push(dataSeries);

  //Better to construct options first and then pass it as a parameter
  var options = {
      zoomEnabled: true,
      animationEnabled: true,

      axisY: {
          lineThickness: 1
      },
      axisX: {
        valueFormatString: "MMM YYYY"
      },
      data: data  // random data
  };

  var chart = new CanvasJS.Chart("chartContainer", options);
  var startTime = new Date();
  chart.render();
  var endTime = new Date();


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



