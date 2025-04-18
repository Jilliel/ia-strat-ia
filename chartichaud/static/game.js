function nextTurn() {
  curPlayer = '' ;
  $.ajax({
      url: '/endturn/'+player+'/'+token,
      complete: function(data){redraw();}
  });
}

function autofarm() {
  curPlayer = '' ;
  $.ajax({
      url: '/autofarm/'+player+'/'+token,
      complete: function(data){redraw();}
  });
}

function moveUnit(id) {
  if(selected_unit != "") {
      document.getElementById(selected_unit).className =
          document.getElementById(selected_unit).className.replace(" selected","");
      selected_unit = "";
  } else {
    document.getElementById(id).className += " selected";
    selected_unit = id ;  
  }
}

function moveToCell(ty,tx) {
  if(selected_unit != "" && unit_type[selected_unit] != 'B') {
    [fy,fx] = position[selected_unit] ;
      if(Math.abs(fx-tx) + Math.abs(fy-ty) == 1) {
        $.ajax({
          url: '/move/'+player+'/'+unit_type[selected_unit]+'/'+fy+'/'+fx+'/'+ty+'/'+tx+'/'+token,
          complete: function(d){redraw();}
        });
      }
  }
}

function farm() {
  if( selected_unit != "" && unit_type[selected_unit] == 'C') { 
    [fy,fx] = position[selected_unit] ;
    $.ajax({
      url: '/farm/'+player+'/'+fy+'/'+fx+'/'+token,
      complete: function(d){redraw();}
    });      
  }
}

function build() {
  if( selected_unit != "" && unit_type[selected_unit] == 'C') { 
    [fy,fx] = position[selected_unit] ;
    $.ajax({
      url: '/build/'+player+'/'+fy+'/'+fx+'/B'+'/'+token,
      complete: function(d){redraw();}
    });      
  }
}

function recruit_unit(t) {
  if( selected_unit != "") { 
    [fy,fx] = position[selected_unit] ;
    $.ajax({
      url: '/build/'+player+'/'+fy+'/'+fx+'/'+t+'/'+token,
      complete: function(d){redraw();}
    });      
  }
}


function addUnit(cell, name, nb,movable,y,x, kind) {
  if(nb>0) {
    var unit = document.createElement('div');
    id = "unit"+id_unit;
    unit.setAttribute("id", id);
    unit.className = name;
    unit.innerHTML = "<img src='"+name.split(" ")[0]+".png' />";
    if (nb > 1) { 
      unit.innerHTML += "<span>"+nb+"</span>" ;
    }
    cell.append(unit);
    position[id] = [y,x];
    unit_type[id] = kind ;  
    if(player == curPlayer && movable) {
        unit.setAttribute("onclick", "moveUnit(this.id)");
    } else {
        unit.className += " fixed";
    }
    id_unit ++ ;
  }
}

function drawWithData(data) {
  curPlayer = data["player"] ;
  curMap = data["map"] ;
  curGold = data["gold"] ;
  height = data["height"] ;
    width = data["width"] ;
  var cpdiv = document.getElementById('gold');
  if(player != "all") {
    cpdiv.innerHTML = "<div class='curgold'>"+curGold[player]+"</div>";
  } else {
      cpdiv.innerHTML = '<div class="curgold player_a">' + curGold['A'] + '</div><div class="curgold player_b">'+curGold['B'] + "</div>" ;
  }
  var scdiv = document.getElementById('score');
  scdiv.innerHTML = '<div class="curscore player_a">' + data["score"]['A'] + '</div><div class="curscore player_b">'+data["score"]['B'] + "</div>" ;
  document.getElementById('nextTurn').disabled = (player != curPlayer) ;
  selected_unit = "" ;
  position = [] ;
  unit_type = [] ;
  document.getElementById('board').innerHTML = "" ;  
  for (var y = 0; y < height ; y++) {
     for(var x = 0; x < width ; x++){
       var cell = document.createElement('div');
       cell.style.position = 'absolute' ;
       cell.style.top = (y*(size_cells+1)+75)+'px' ;
       cell.style.left = (x*(size_cells+1))+'px' ;
       cell.setAttribute("onclick","moveToCell("+y+","+x+");");  
       cellData = data["map"][y][x] ;
       if(cellData.hasOwnProperty('G')) {
           cell.className = 'cell';
           if(data.hasOwnProperty("viewA")) {
               if(data["viewA"].hasOwnProperty(y+"_"+x)) {
                 if(data["viewB"].hasOwnProperty(y+"_"+x)) {
                     cell.className += ' vc';
                 } else {
                     cell.className += ' va';
                 }
               } else {
                 if(data["viewB"].hasOwnProperty(y+"_"+x)) {
                     cell.className += ' vb';
                 }
               }
           }
           addUnit(cell,'ab building player_a',cellData['A']['B'],cellData['A'].hasOwnProperty('Bm'),y,x,'B');
           addUnit(cell,'am unit mili player_a',cellData['A']['M'],cellData['A'].hasOwnProperty('Mm'),y,x,'M');
           addUnit(cell,'ac unit civil player_a',cellData['A']['C'],cellData['A'].hasOwnProperty('Cm'),y,x,'C');           
           addUnit(cell,'bb building player_b',cellData['B']['B'],cellData['B'].hasOwnProperty('Bm'),y,x,'B');
           addUnit(cell,'bm unit mili player_b',cellData['B']['M'],cellData['B'].hasOwnProperty('Mm'),y,x,'M');
           addUnit(cell,'bc unit civil player_b',cellData['B']['C'],cellData['B'].hasOwnProperty('Cm'),y,x,'C');
         if(cellData['G']>0) { 
           var gold = document.createElement('div');
           gold.className = 'gold';
           gold.innerHTML = "<p>"+cellData['G']+"</p>";
           cell.appendChild(gold);
         }
       } else {
          cell.className = 'cell hidden';
        }
      document.getElementById("board").appendChild(cell);
    }
  }
  if(data.hasOwnProperty("winner") && data["winner"] != "") {
      if(!document.getElementById("winnerTitle")) {
        var winnerTitle = document.createElement('div');
        winnerTitle.className = 'winner' ;
        winnerTitle.id = 'winnerTitle' ;
        winnerTitle.innerHTML = '<p>The winner is player '+data['winner']+'!</p>'
        document.body.appendChild(winnerTitle);
     }  
  } else {
      if(document.getElementById("winnerTitle")) {
          document.getElementById("winnerTitle").remove()
      }
  }
    
}

function redraw() {
  $.ajax({
      url: '/view/'+player+'/'+token,
      success: function(data){drawWithData(data);}
  });  
  if(player != curPlayer) {
      setTimeout( () => {redraw() ;}, "100") ;
  }
}

function start_game() {
  player = 'all';
  curPlayer = 'C' ;  
  id_unit = 0 ;
  size_cells = 100;
}

start_game();

function init_player() {
  if(confirm("Register as a player?")) {
    $.ajax({
      url: '/getToken',
        success: function(d){player=d['player']; token = d['token'];redraw();}
    });      
  } else {
      token='nop'
      redraw();
  }
}
