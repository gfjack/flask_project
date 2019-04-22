

 function addNewVote(title, description) {
    var  h5= document.createElement("h5");
    h5.className ="card-title";
    var h5text = document.createTextNode(title);
    h5.appendChild(h5text);

    var p = document.createElement("p");
    p.className = "card-text";
    var ptext = document.createTextNode(description);
    p.appendChild(ptext);

    var a = document.createElement("a");
    a.href = "#";
    a.className = "btn btn-primary";
    var atext = document.createTextNode("TEST");
    a.appendChild(atext);

    var div1 = document.createElement("div");
    div1.className = "card-body";
    div1.appendChild(h5);
    div1.appendChild(p);
    div1.appendChild(a);


    var div2 = document.createElement("div");
    div2.className = "card";
    div2.appendChild(div1);


     var div3 = document.createElement("div")
     div3.className = "col-sm-4";
     div3.appendChild(div2);

     var votelist = document.getElementsByClassName("VoteList")[0];
     console.log(div3);
     console.log(votelist);
     votelist.appendChild(div3);
 }
