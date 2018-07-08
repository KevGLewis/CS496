var apiKey = 'zXUuF4xob97q9Q9qtVWL6zJkgttptBj00gDvO8yh'

function searchFoodTwo(event){
    
    var searchValue = document.getElementById("searchValueThree").value;
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
              searchButtons[i].setAttribute( "onclick", "buttonSelect(event, "+response.list.item[i].ndbno+")" );
              
          }
          
      } else {
        console.log("Error in network request: " + req.statusText);
      }
    });
    req.send(null);
    
    event.preventDefault();
}


function buttonSelect(event, param){
    console.log(param);
    event.preventDefault();
}

