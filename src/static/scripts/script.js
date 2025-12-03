let source_type  = document.getElementById("source_type");
let source_host = document.getElementById("source_host");
let source_subnet = document.getElementById("source_subnet");

let dest_type  = document.getElementById("dest_type");
let dest_host = document.getElementById("dest_host");
let dest_subnet = document.getElementById("dest_subnet");

let filtro = document.getElementById("filtro");
let protocolli = document.getElementById("protocolli");

let line_number = document.getElementById("line_number")

let aggiungi = document.getElementById("aggiungi");
let rimuovi = document.getElementById("rimuovi")

source_type.addEventListener("change", () => {
    aggiorna(source_type, source_host, source_subnet);
});

dest_type.addEventListener("change", ()=>{
    aggiorna(dest_type, dest_host, dest_subnet);
});

aggiungi.addEventListener("click", ()=>{
    let source, dest;
    if(source_type.value == "host"){
        source = source_host.value;
    }
    else{
        if(source_type.value == "subnet"){
            source = source_subnet.value;
        }
        else{
            source = null;
        }
    }
    if(dest_type.value == "host"){
        dest = dest_host.value;
    }
    else{
        if(dest_type.value == "subnet"){
            dest = dest_subnet.value;
        }
        else{
            dest = null;
        }
    }

    if(dest && source){
        if(dest == source)
        {
            source_type.selectedIndex = 0;
            dest_type.selectedIndex = 0;
            aggiorna(source_type, source_host, source_subnet);
            aggiorna(dest_type, dest_host, dest_subnet);
            alert("sorgente e destinazione devono essere diversi!");
            return;
        }
        else{
            if(source[source.length - 1] === dest[dest.length - 1]){
                source_type.selectedIndex = 0;
                dest_type.selectedIndex = 0;
                aggiorna(source_type, source_host, source_subnet);
                aggiorna(dest_type, dest_host, dest_subnet);
                alert("Sorgente e destinazione devono essere in sottoreti diverse!");
                return;
            }
        }
    }

    prot_array = Array.from(protocolli.selectedOptions).map(option => option.value);

    const policy = {
        source: source,
        dest: dest,
        target: filtro.value,
        protocolli: prot_array.join(", ")
    }

    fetch("/aggiungi", {
        method: "POST", 
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(policy)
    })
    .then(response => response.json())
    .then(data => {
        ricarica_tabella(data);
    });

    source_type.selectedIndex = 0;
    aggiorna(source_type, source_host, source_subnet);
    dest_type.selectedIndex = 0;
    aggiorna(dest_type, dest_host, dest_subnet);
    filtro.selectedIndex = 0;
    protocolli.selectedIndex = -1;
});

let table = document.querySelector("tbody");
let selectedRow = null;
let menu = document.getElementById("menu");
table.addEventListener("contextmenu", function(e){
    e.preventDefault();

    const row = e.target.closest("tr");
    if(!row || row.rowIndex == 0){
        return;
    }

    selectedRow = row;

    menu.style.display = "block";
    menu.style.left = e.pageX + "px";
    menu.style.top = e.pageY + "px";
});

document.addEventListener("click", function(){
    menu.style.display = "none";
});

document.getElementById("elimina").addEventListener("click",() => {
    if(selectedRow){
        router_name = selectedRow.cells[0].innerText;
        line_number = selectedRow.cells[5].innerText;

        fetch(`/rimuovi?line_number=${encodeURIComponent(line_number)}&router_name=${encodeURIComponent(router_name)}`)
        .then(res => res.json())
        .then(data => {
            ricarica_tabella(data);
        });
        selectedRow = null;
        menu.style.display = "none";
    }
});

function aggiorna(type, host, subnet) {
    if(type.value == "host"){
        host.parentElement.classList.remove("hide");
        subnet.parentElement.classList.add("hide");
    }
    else{
        if(type.value == "subnet"){
            host.parentElement.classList.add("hide");
            subnet.parentElement.classList.remove("hide");
        }
        else{
            subnet.selectedIndex = 0;
            host.selectedIndex = 0;
            host.parentElement.classList.add("hide");
            subnet.parentElement.classList.add("hide");
        }
    }
}

function ricarica_tabella(data){

    const tbody = document.querySelector("tbody");
    tbody.innerHTML = "";

    data["router"].forEach(r => {
        r["policy"].forEach(p =>{
            const row = document.createElement("tr");
            row.innerHTML = "<td>" + r["nome"] + "</td><td>" + 
            p["src_node"]["nome"] + "</td><td>" + 
            p["dest_node"]["nome"] + "</td><td>" + 
            p["target"] + "</td><td>" + p["protocollo"] + "</td><td>" + p["line_number"] + "</td>";

            tbody.appendChild(row);
        });
    });
}