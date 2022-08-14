var searchWrapper = document.querySelector(".search-input");
var inputBox = searchWrapper.querySelector("input");
var suggBox = searchWrapper.querySelector(".autocom-box");

var suggestions = [
    "Aiuto",
    "Babbuino",
    "Cane",
    "Domenica",
    "Elicottero",
    "Famiglia",
    "Gianni",
    "Io",
    "Lavoro",
    "Maiale",
    "Nicotina",
    "Ora",
    "Panino",
    "Rabbia",
    "Sandro",
    "Tavolo",
    "Uva",
    "Vaniglia",
    "Zeta"
];
inputBox.onkeyup = function prova(e, listDb) {
    let userData = e.target.value;
    let itemList = [];
    if (userData) {
        itemList = suggestions.filter((data) => {
            return data.toLocaleLowerCase().startsWith(userData.toLocaleLowerCase());
        });
        itemList = itemList.map((data) => {
            return data = '<li>' + data + '</li>';
        });
        searchWrapper.classList.add("active");
        showSuggestions(itemList);
        let allList = suggBox.querySelectorAll("li");
        for (let i = 0; i < allList.length; i++) {
            allList[i].setAttribute("onclick", "select(this)");
        }
    }
    else {
        searchWrapper.classList.remove("active");
    }
};

function select(element) {
    let selectUserData = element.textContent;
    inputBox.value = selectUserData;
    searchWrapper.classList.remove("active");
}

function showSuggestions(list){
    let listData;
    if(!list.length) {
        userValue = inputBox.value;
        listData = '<li>' + userValue + '</li>';
    }
    else {
        listData = list.join('');
    }
    suggBox.innerHTML = listData;
}