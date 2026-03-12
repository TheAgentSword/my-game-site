const games = [

{
name:"Run 3",
image:"https://upload.wikimedia.org/wikipedia/en/thumb/3/34/Run3game.jpg/220px-Run3game.jpg",
url:"games/run3/index.html"
},

{
name:"Slope",
image:"https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/3D-ball-game.jpg/320px-3D-ball-game.jpg",
url:"games/slope/index.html"
},

{
name:"Snow Rider 3D",
image:"https://img.itch.zone/aW1nLzE2NjA2NTQucG5n/original/4%2FrD9F.png",
url:"games/snowrider/index.html"
}

]

const grid = document.getElementById("game-grid")

function loadGames(list){

grid.innerHTML=""

list.forEach(game=>{

const div=document.createElement("div")
div.className="game"

div.innerHTML=`
<a href="${game.url}">
<img src="${game.image}">
<p>${game.name}</p>
</a>
`

grid.appendChild(div)

})

}

loadGames(games)

document.getElementById("search").addEventListener("input",e=>{

const q=e.target.value.toLowerCase()

const filtered=games.filter(g=>g.name.toLowerCase().includes(q))

loadGames(filtered)

})
