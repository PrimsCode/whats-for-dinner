const baseUrl = 'https://api.spoonacular.com/recipes/';
import {apiKey} from './secrets.js';

let searchResults = {};
let date = "";
let meal = "";
let recipeJson = [];

let appetizer = null;
let mainCourse = null;
let sideDish = null;
let dessert = null;
let dinnerId = 0;

const searchOutput = document.querySelector('#searchOutput');
const datePicker = document.querySelector('#datePicker');
const searchForm = document.querySelector('#searchForm');
const submitBtn = document.querySelector('#submitBtn');
const dinnerBtn = document.querySelector('.dinnerBtn');
const hiddenInput = document.querySelector('#hiddenInput');
const dinnerOutput = document.querySelector('#dinnerOutput');
const displayRecipe = document.getElementsByClassName('displayRecipe');
const printRecipe = document.querySelector("#printRecipe");
const printMenu = document.querySelector("#printMenu");

//function for datepicker calendar 
flatpickr("input[type=date]", {
    altInput: true,
    altFormat: "F j, Y",
    dateFormat: "m-d-Y",
    minDate:'today',
    maxDate: new Date().fp_incr(60),
    disable: [
        function(date){
            return (date.getDay() < 'today');
        }
    ]
});

//getting the latest dinner menu id
if(dinnerBtn){
    dinnerId = dinnerBtn.id;
}

//handle submit from searchForm
if (searchForm) {
    searchForm.addEventListener('submit', (e)=>{
        e.preventDefault();
        const mealSelector = document.querySelector('#mealType'); 
        const searchBar = document.querySelector('#searchBar');
        const dateDisplay = document.querySelector('#dateDisplay')
        ;
        searchOutput.innerHTML = '';            
        date = datePicker.value;    
        dateDisplay.innerHTML = `<div class="container w-75">
                                    <p class="pb-2 h5" >Date: ${date}</p>
                                </div>`;    

        meal = mealSelector.value;           
        let searchTerm = searchBar.value;    
        getSearchResults(searchTerm);        
    })
}

//fetch Get search results from external API
function getSearchResults(searchTerm){
    let url = baseUrl + "complexSearch?query=" + searchTerm + '&number=5' + '&apiKey=' + apiKey;
    fetch(url)
    .then(res => res.json())
    .then(data=>{
        console.log(data);
        searchResults = data;
        outputResults(searchResults);        
    })
}

//append HTML to show search results on page
function outputResults(res){
    const searchTitle = document.querySelector('#searchTitle');    
    searchTitle.innerHTML = "<h1 class='pt-3 mt-2' style='font-size:40px'>Search Results</h1>";  

    for (i=0; i< res.results.length; i++){
        console.log(res.results[i]);
        let newTitle = "";

        if (res.results[i].title.length > 40){
            newTitle = res.results[i].title.slice(0,41);
        } else {
            newTitle = res.results[i].title;
        }
        
        searchOutput.innerHTML += `
        <div class="container m-1 p-3 bg-primary text-center" style="width:210px; height:230px" id="${res.results[i].id}">
            <img src="${res.results[i].image}" style="max-width:180px; max-height:100px">
            <p style="font-size:14px; font-weight:600">${newTitle}</p>            
            <button class="btn btn-success add-result" id="${i}">+</button>                          
        </div>`
    }
    return;
}

//add selected recipe to dinner menu
if (searchOutput) {
    searchOutput.addEventListener('click', function(e){
        if (e.target.classList.contains('add-result')){
            e.preventDefault();        
            let resId = e.target.id;
            let selectedResult = searchResults.results[resId];    
           
            if (meal == 'appetizer'){
                appetizer = selectedResult;
                console.log(appetizer);
                const output = document.querySelector('#appetizerOutput');
                outputMenu(output, appetizer);    
            } else if (meal == 'main-course'){
                mainCourse = selectedResult;
                console.log(mainCourse);
                const output = document.querySelector('#mainCourseOutput');
                outputMenu(output, mainCourse);    
            } else if (meal == 'side-dish'){
                sideDish = selectedResult;
                console.log(sideDish);
                const output = document.querySelector('#sideDishOutput');
                outputMenu(output, sideDish);    
            } else {
                dessert = selectedResult;
                console.log(dessert);
                const output = document.querySelector('#dessertOutput');
                outputMenu(output, dessert);
            }
        }
        return;
    })
}

//Append HTML to show recipe title on page
function outputMenu(output, res){
    let newTitle = "";
    if (res.title.length > 28){
        newTitle = res.title.slice(0,28);
        output.innerHTML = `<h2 class="pt-2">${newTitle}...</h2>`
    } else {
        newTitle = res.title;
        output.innerHTML = `<h2 class="pt-2">${newTitle}</h2>`
    }
    return;
}

if(dinnerBtn){
    dinnerId = dinnerBtn.id;
}

//send dinner menu data to Flask & commit to database
function submitDinnerMenu(){
    let menu = {};
    createMenuObj(menu);
    menu['date'] = {date: date};

    const request = new XMLHttpRequest()
    request.open('POST', `/processInfo/${JSON.stringify(menu)}`);
    request.send();

    const titleOutput = document.getElementsByClassName('title-output');
    for (i=0; i<titleOutput.length; i++){
        titleOutput[i].innerHTML = '';
    }
   
    dinnerId ++;
    dinnerBtn.innerHTML += `<a href="/dinner-view/${dinnerId}">
    <button class="btn btn-danger p-2 mt-2" type="submit">View Created Menu</button>
    </a>`
}

//Handle favoriting and unfavoriting dinner menus
if (dinnerOutput) {
    dinnerOutput.addEventListener('click', function(e){
        if (e.target.classList.contains('favorite-icon')){
            e.preventDefault();

            if (e.target.classList.contains('noFav')){
                let favorite = {};
                favorite['dinner_id'] = e.target.id
                console.log(favorite);
                const request = new XMLHttpRequest()
                request.open('POST', `/processFav/${JSON.stringify(favorite)}`);
                request.send();
                e.target.innerHTML = `<path class="favorite-icon" id="${favorite['dinner_id']}" fill-rule="evenodd" d="M8 1.314C12.438-3.248 23.534 4.735 8 15-7.534 4.736 3.562-3.248 8 1.314z"/>`;
            } else {
                let favorite = {};
                favorite['dinner_id'] = e.target.id
                const request = new XMLHttpRequest()
                request.open('POST', `/processUnFav/${JSON.stringify(favorite)}`);
                request.send();
                e.target.outerHTML = '<path d="m8 2.748-.717-.737C5.6.281 2.514.878 1.4 3.053c-.523 1.023-.641 2.5.314 4.385.92 1.815 2.834 3.989 6.286 6.357 3.452-2.368 5.365-4.542 6.286-6.357.955-1.886.838-3.362.314-4.385C13.486.878 10.4.28 8.717 2.01L8 2.748zM8 15C-7.333 4.868 3.279-3.04 7.824 1.143c.06.055.119.112.176.171a3.12 3.12 0 0 1 .176-.17C12.72-3.042 23.333 4.867 8 15z"/>';
            }

       } 
    })
}

//Handle finding and displaying recipe in dinner view
if (displayRecipe) {
    for (let i=0; i< displayRecipe.length; i++){
        displayRecipe[i].addEventListener('click', function(e){
            e.preventDefault();
            let recipe_id = e.target.id;            
            addRecipeView(recipe_id);    
        })
    }    
}

//Generate Printable Recipe page
if (printRecipe) {
    let recipeId = document.querySelector("#recipeId").value;
    findRecipe(recipeId);
}

//Generate Printable Menu page
if (printMenu) {
    const recipes = document.querySelectorAll("#recipeId");
    console.log(recipes);
    for (let i=0; i<recipes.length; i++){
        let recipe = recipes[i].value;
        findRecipe(recipe);
    }
}

const printIngredients = document.querySelector("#printIngredients")

if (printIngredients) {
    let recipeId = document.querySelector("#recipeId").value;
    findRecipe(recipeId);
}

const printAllIngredients = document.querySelector("#printAllIngredients")

if (printAllIngredients) {
    const recipes = document.querySelectorAll("#recipeId");
    console.log(recipes);
    for (let i=0; i<recipes.length; i++){
        let recipe = recipes[i].value;
        findRecipe(recipe);
    }
}

const recipeView = document.querySelector('#recipeView');
const ingredientView = document.querySelector('#ingredientView');

//Get recipe data from external API and call showRecipe
function findRecipe(id){
    let url = baseUrl + id + '/information?includeNutrition=false' + '&apiKey=' + apiKey;
    console.log(url);
    fetch(url)
    .then(res=>res.json())
    .then(data=>{
        if(recipeView){
            showRecipe(data)
        } else {
            recipeJson.push(data)
            getAllIngredients(recipeJson)
        };   
    });
}

function getAllIngredients(jsonArr){
    let ingredients =[];

    for (let i=0; i<jsonArr.length; i++){
        for (let j=0; j<jsonArr[i].extendedIngredients.length; j++){
            let ingredient = jsonArr[i].extendedIngredients[j];
            const newObj = {id: ingredient.id, name:ingredient.nameClean, amount:ingredient.amount, unit:ingredient.unit};
            ingredients.push(newObj);
        };
    };
    pruneInt(ingredients);
};

function pruneInt(json){
    for (let i=0; i<json.length; i++){
        for (let j=0; j<json.length; j++){
            if (json[i].id == json[j].id){
                if(json[i].unit == json[j].unit){
                    json[i].amount += json[j].amount;
                    json.splice(j,1);
                };
            }; 
        };
    };
    console.log(json);
    showShoppingList(json);
};

function showShoppingList(json){
    const ingredientOutput= document.querySelector('#ingredientDisplay');
    let ingredientList =[];

    json.forEach((ingredient)=>{        
        const ingString = `${ingredient.name} - ${ingredient.amount} ${ingredient.unit}`;
        ingredientList.push(ingString);
    });

    displaySortedList(ingredientOutput, ingredientList);
};

function displaySortedList(output, list){
    let sortedList = list.sort();
    console.log(sortedList);

    list.forEach((ingredient)=>{     
        output.innerHTML += `<li>${ingredient}</li>`; 
    });
}


//Call functions to diaplay recipe on page
function showRecipe(json){
    recipeInfoOutput(json);
    ingredientOutput(json);
    instructionOutput(json);
}

//Dynamictally add recipe display to menu view page
function addRecipeView(recipe_id){
    recipeView.innerHTML = `
    <div class="container-fluid p-2 bg-primary">
    <div class="container-fluid bg-white justify-content-start text-start p-2">    
        <div class="text-center" id="titleDisplay${recipe_id}"></div>

        <span class="text-center" id="imgSourceDisplay${recipe_id}"></span>
        
        <p class=" pt-1 pb-1"><span class="h5" style="font-size:15px">Servings: </span>
            <span id="servingDisplay${recipe_id}" style="font-size:15px"></span>
        </p>

        <p class=" pt-1 pb-1"><span class="h5" style="font-size:15px">Cook Time: </span>: 
            <span id="cookTimeDisplay${recipe_id}" style="font-size:15px"></span>
        </p>

        <p class="pt-1 pb-1 h5" style="font-size:15px">Ingredients:</p>
        <ul id="ingredientDisplay${recipe_id}" style="font-size:15px">

        </ul>

        <p class="pt-1 pb-1 h5" style="font-size:15px;">Instructions:</p>
        <ul style="list-style:none; font-size:15px" id="instructionDisplay${recipe_id}">

        </ul>
    </div>
    </div>         
    `;
    findRecipe(recipe_id);
}

//Dynamictally add recipe info to page
function recipeInfoOutput(json){
    const titleDisplay = document.querySelector(`#titleDisplay${json.id}`)
    const imgSourceOutput = document.querySelector(`#imgSourceDisplay${json.id}`)
    const servingOutput = document.querySelector(`#servingDisplay${json.id}`);
    console.log(servingOutput);
    const cookTimeOutput = document.querySelector(`#cookTimeDisplay${json.id}`);
    const menuId = document.querySelector('#menuId');
    
    if (menuId){
        dinnerId = menuId.value;        
    }

    titleDisplay.innerHTML = `<h3 class="p-1 m-0">${json.title}</h3>`;

    if (imgSourceOutput){
        imgSourceOutput.innerHTML = `<img src="${json.image}" class="mx-auto d-block" style="max-width:200px; max-height:200px">
        <a href="${json.sourceUrl}" target="_blank" class="text-dark"><p style="font-size:12px"><i>Source: ${json.sourceName}</i></p></a>
        <a href="/printable/${dinnerId}/${json.id}" style="text-decoration-none"><button class="btn btn-sm btn-success">Print</button></a>
        <a href="/printable/${dinnerId}/${json.id}/shopping-list" style="text-decoration-none"><button class="btn btn-sm btn-danger">Shopping List</button></a>`; 
    };

    servingOutput.innerHTML = `${json.servings}`;
    cookTimeOutput.innerHTML = `${json.readyInMinutes} mins`;
}

//Dynamictally add recipe ingredient to page
function ingredientOutput(json){
    const ingredientOutput = document.querySelector(`#ingredientDisplay${json.id}`)
    json.extendedIngredients.forEach((ingredient)=>{
        const ingName = `${ingredient.originalName}`;
        const ingAmount = `${ingredient.measures.us.amount} ${ingredient.measures.us.unitShort}`
        const ingString = `${ingAmount} ${ingName}`
        ingredientOutput.innerHTML += `<li>${ingString}</li>`;
    });
}

//Dynamictally add recipe instruction to page
function instructionOutput(json){
    const instructionOutput = document.querySelector(`#instructionDisplay${json.id}`)
    if (json.analyzedInstructions.length !=0){
        json.analyzedInstructions[0].steps.forEach((instruction)=>{
            const insNum = `${instruction.number}`;
            const insStep = `${instruction.step}`;
            const insString =`${insNum}: ${insStep}`;
            instructionOutput.innerHTML += `<li>${insString}</li>`
        });
    } else {
        instructionOutput.innerHTML += `<p class="text-center">No Instructions!
        <br><a href="${json.sourceUrl}" target="_blank" class="text-success text-center">Please check ${json.sourceName} Website</a></p>`
    };    
}

//Create menu object to send to flask
function createMenuObj(menu){
    if (appetizer != null){
        menu['appetizer'] = {
            id: appetizer.id,
            title: appetizer.title
        };
    };
    if (mainCourse != null){
        menu['main_course'] = {
            id: mainCourse.id,
            title: mainCourse.title
        };
    };
    if (sideDish != null){
        menu['side_dish'] = {
            id: sideDish.id,
            title: sideDish.title
        };
    };
    if (dessert != null){
        menu['dessert'] = {
            id: dessert.id,
            title: dessert.title
        };
    };
    return menu;
}

//send updated dinner menu data to Flask & commit to database for edit
function editDinnerMenu(){
    let user_id = document.querySelector('#editUserMenu').value;
    let menu = {};
    createMenuObj(menu);

    menu['id'] = {id:dinnerId};
    menu['date'] = {date: date};
    menu['user'] = {user_id: user_id};
    
    const request = new XMLHttpRequest()
    request.open('POST', `/editInfo/${JSON.stringify(menu)}`);
    request.send();
  
    dinnerId;
    dinnerBtn.innerHTML += `<a href="/dinner-view/${dinnerId}">
    <button class="btn btn-success mt-2" type="submit">View Edited Menu</button>
    </a>`
}

//add dinner menu data to the edit dinner menu page
const editMenu = document.querySelector('.editMenu');
if (editMenu) {
    let appetizerId = document.querySelector('#editAppetizerId').value;
    let mainCourseId = document.querySelector('#editMainCourseId').value;  
    let sideDishId = document.querySelector('#editSideDishId').value;  
    let dessertId = document.querySelector('#editDessertId').value;

    if (appetizerId != null){
        let appetizerTitle = document.querySelector('#editAppetizerTitle').value;
        appetizer ={id:appetizerId, title:appetizerTitle};
        console.log(appetizer);
        const output = document.querySelector('#appetizerOutput');
        outputMenu(output, appetizer);
    }; 
    if (mainCourseId != null){
        let mainCourseTitle = document.querySelector('#editMainCourseTitle').value;
        mainCourse ={id:mainCourseId, title:mainCourseTitle};
        console.log(mainCourse);
        const output = document.querySelector('#mainCourseOutput');
        outputMenu(output, mainCourse);
    }; 
    if (sideDishId != null){
        let sideDishTitle = document.querySelector('#editSideDishTitle').value;
        sideDish ={id:sideDishId, title:sideDishTitle};
        console.log(sideDish);
        const output = document.querySelector('#sideDishOutput');
        outputMenu(output, sideDish);
    };
    if (dessertId != null){
        let dessertTitle = document.querySelector('#editDessertTitle').value;
        dessert ={id:dessertId, title:dessertTitle};
        console.log(dessert);
        const output = document.querySelector('#dessertOutput');
        outputMenu(output, dessert);
    };
}

