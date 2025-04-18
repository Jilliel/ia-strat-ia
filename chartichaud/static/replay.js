list_matchs = []
player="all"

function draw_list() {
    cur_round = -1 ;
    document.getElementById("board").style.visibility = 'hidden';
    document.getElementById("top").style.visibility = 'hidden';
    document.getElementById("list").style.visibility = 'visible';
    var winner = document.getElementById("winnerTitle") ;
    if(winner) winner.remove();
    out = "";
    filter_keywords = document.getElementById("filterList").value ;
    for (var i = 0; i < list_matchs.length; i++) {
        all_fields = list_matchs[i]["A"]+" "+list_matchs[i]["B"]+" "+list_matchs[i]["date"] ;
        if(filter_keywords =="" || all_fields.search(filter_keywords) != -1) {
            out += "<tr onClick=\"load_replay('"+list_matchs[i]["replay"]+"')\"><td>"+
                list_matchs[i]["date"]+"</td><td>"+
                list_matchs[i]["A"]+"</td><td>"+
                list_matchs[i]["B"]+"</td><td>"+
                list_matchs[i]["winner"]+"</td></tr>";
        }
    }  
    document.getElementById("listContent").innerHTML = "<table border=1><thead><tr><th>Date</th><th>Player A</th><th>Player B</th><th>Winner</th></tr></thead><tbody>"+out+"</tbody></table>" ;
}

function start_replay() {
    $.ajax({
      url: '/matchlist',
      success: function(d){ list_matchs=d; draw_list() ; }
    });

}

function draw_replay() {
    if(cur_round >= 0) {
        document.getElementById("board").style.visibility = 'visible';
        document.getElementById("top").style.visibility = 'visible';
        document.getElementById("list").style.visibility = 'hidden';
        if(cur_round < match_data.length) {
            drawWithData(match_data[Math.trunc(cur_round)]["state"]);
            // cur_round += 1;
            speed = document.getElementById('speed').value;
            cur_round += speed/100;
            setTimeout( () => {draw_replay() ;}, "50") ;
        }
    }
}

function load_replay(url) {
    $.ajax({
      url: url,
        success: function(d){ match_data = d; cur_round = 0; draw_replay() ; }
    });
}
start_replay();
