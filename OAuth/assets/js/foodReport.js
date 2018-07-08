var apiKey = 'zXUuF4xob97q9Q9qtVWL6zJkgttptBj00gDvO8yh'

// Fills out a Table with the Search Results

function searchFoodButton(event){
    
    var searchValue = document.getElementById("searchValue").value;
    var ndbNumb = document.getElementsByClassName("ndb_numb");
    var resultDescriptions = document.getElementsByClassName("resultDescription")
    var searchButtons = document.getElementsByClassName("button select")
    
    var req = new XMLHttpRequest();
    req.open('GET', 'https://api.nal.usda.gov/ndb/search/?format=json&q='+ searchValue +'&sort=r&max=5&offset=0&api_key=' + apiKey, true)
    req.addEventListener('load',function(){
      if(req.status >= 200 && req.status < 400){
        var response = JSON.parse(req.responseText);
          for(var i = 0; i < resultDescriptions.length; i++){
              resultDescriptions[i].textContent = response.list.item[i].name;
              ndbNumb[i].textContent = response.list.item[i].ndbno;
              searchButtons[i].setAttribute( "onclick", "buttonSelectTwo(event, "+response.list.item[i].ndbno+")" );
              
          }
          
      } else {
        console.log("Error in network request: " + req.statusText);
      }
    });
    req.send(null);
    
    event.preventDefault();
}

function buttonSelectTwo(event, ndbIn){
    
    var i;
    var nutTable = document.getElementById("nutrition_body");
    while (nutTable.firstChild) {
        nutTable.removeChild(nutTable.firstChild);
    }

    
    var req = new XMLHttpRequest();
    req.open('GET', 'https://api.nal.usda.gov/ndb/reports/?ndbno='+ ndbIn +'&type=b&format=json&api_key=' + apiKey, true)
    req.addEventListener('load',function(){
      if(req.status >= 200 && req.status < 400){
        var response = JSON.parse(req.responseText);
        for(i = 0; i < 5; i++){
            var newTr = document.createElement("tr");
            
            var nameIn = document.createElement("td");
            nameIn.textContent = response.report.food.nutrients[i].name;
            newTr.appendChild(nameIn);
            
            var valueIn = document.createElement("td");
            valueIn.textContent = response.report.food.nutrients[i].value;
            newTr.appendChild(valueIn);
            
            var unitIn = document.createElement("td");
            unitIn.textContent = response.report.food.nutrients[i].unit;
            newTr.appendChild(unitIn);
            
            nutTable.appendChild(newTr);
        }
        
          
      } else {
        console.log("Error in network request: " + req.statusText);
      }
    });
    req.send(null);
    
    event.preventDefault();
}

