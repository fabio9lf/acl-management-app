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

let ip_sel = true;
protocolli.addEventListener("change", ()=>{
    const options = Array.from(protocolli.options);
    const ip = options.find(o => o.value === "ip");

    if (ip.selected) {
        ip_sel = true;
        options.forEach(o => {
            o.selected = true;
            if (o.value !== "ip") {
                o.disabled = true;
            }
        });
    } else {
        options.forEach(o => {
            if(ip_sel)
                o.selected = false;
            o.disabled = false;
        });
        ip_sel = false;
    }
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
    const prot_array = Array.from(protocolli.selectedOptions)
        .filter(option => !option.disabled)
        .map(option => option.value);

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
    [...protocolli.options].forEach((opt, index)=>{
        opt.selected = true;
        opt.disabled = index !== 0;
    });
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
        let router_name = selectedRow.cells[0].innerText;
        let line_number = selectedRow.cells[5].innerText;

        fetch(`/rimuovi?line_number=${encodeURIComponent(line_number)}&router_name=${encodeURIComponent(router_name)}`)
        .then(res => res.json())
        .then(data => {
            ricarica_tabella(data);
        });
        selectedRow = null;
        menu.style.display = "none";
    }
});

let editable = false;

document.getElementById("modifica").addEventListener("click", ()=>{
    if(selectedRow){
        for (let i = 3; i < 5; i++) {
            selectedRow.cells[i].setAttribute("contenteditable", "true");
        }
        editable = true;

        let td = selectedRow.cells[4];
        let select = crea_select(td.innerText, "proto");
        td.innerText = "";
        td.appendChild(select);

        td = selectedRow.cells[3];
        select = crea_select(td.innerText, "target");
        td.innerText = "";
        td.appendChild(select)
    }
});

document.addEventListener("keydown", (e)=>{
    if(e.key === "Enter" && selectedRow && editable){
        e.preventDefault();
        
        selectedRow.cells[4].innerText = selectedRow.cells[4].children[0].value;
        selectedRow.cells[3].innerText = selectedRow.cells[3].children[0].value;
        
        let router_name = selectedRow.cells[0].innerText;
        let line_number = selectedRow.cells[5].innerText;
        let source = selectedRow.cells[1].innerText;
        let dest = selectedRow.cells[2].innerText;
        let target = selectedRow.cells[3].innerText;
        let protocol = selectedRow.cells[4].innerText;

        const policy = {
            source: source,
            dest: dest,
            target: target,
            protocolli: protocol
        }

        editable = false;
        selectedRow = null;

        fetch(`/replace?line_number=${encodeURIComponent(line_number)}&router_name=${encodeURIComponent(router_name)}`,  {
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
    }
});


const test = document.getElementById("test");
test.addEventListener("click", ()=>{
    let overlay = document.getElementById("overlay")
    let blocco = document.getElementById("blocking-overlay")
    overlay.style.display = "block";
    blocco.style.display = "block";
    overlay.innerHTML = "Test in corso ...";
    fetch("/test").then(response => response.json())
    .then(data =>{
        blocco.style.display = "none";
        overlay.innerHTML = "<h1>Risultati dei test</h1><br>";
        let close = document.createElement("button");
        close.id = "close";
        close.innerHTML = "Chiudi";
        close.addEventListener("click", ()=>{
            overlay.style.display = "none";
        });
        overlay.appendChild(close);
        for(let i=0;i < data.length;i+=3){
            let div = document.createElement("div");
            div.classList.add("test_wrapper");
            let title = document.createElement("h3");
            title.innerHTML = data[i].src_node.nome + " (" + data[i].src_node.ip + ") --> " + data[i].dest_node.nome + " (" + data[i].dest_node.ip + ")";  
            div.appendChild(title);
            for(let j = 0;j < 3;j++){
                let test = document.createElement("div");
                let p = document.createElement("p");
                p.innerHTML = "<h4> Test del protocollo " + data[i + j].protocollo + ":</h4> <br> Esito: ";
                if(data[i + j].risultato){
                    p.innerHTML += "<b style='color: green'> test superato</b> <br><br>"
                    if(data[i + j].esito == "ACCEPT"){
                        p.innerHTML += "I pacchetti transitano correttamente!";
                    }
                    else{
                        p.innerHTML += "I pacchetti vengono correttamente bloccati!";
                    }
                }
                else{
                    p.innerHTML += "<b style='color: red'> test fallito</b> <br><br>"
                    if(data[i + j].esito != "ACCEPT"){
                        p.innerHTML += "I pacchetti transitano, ma dovrebbero essere bloccati!";
                    }
                    else{
                        p.innerHTML += "I pacchetti vengono bloccati, ma dovrebbero transitare!";
                    }
                }
                p.innerHTML += "<br><br>";
                test.appendChild(p);
                div.appendChild(test);
            }
            overlay.appendChild(div);
        }
    });
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
            let source = p["src_node"] != null ? p["src_node"]["nome"] : "qualsiasi";
            let dest = p["dest_node"] != null ? p["dest_node"]["nome"] : "qualsiasi";
            const row = document.createElement("tr");
            row.innerHTML = "<td>" + r["nome"] + "</td><td>" + 
            source + "</td><td>" + 
            dest + "</td><td>" + 
            p["target"] + "</td><td>" + p["protocollo"] + "</td><td>" + p["line_number"] + "</td>";

            tbody.appendChild(row);
        });
    });
}

function crea_select(value, tipo){
    const select = document.createElement("select");

    const protocolli = ["ip", "udp", "tcp", "icmp"];
    const target = ["ACCEPT", "DROP"];
    let options;

    if(tipo === "proto"){
        options = protocolli;
    }
    else{
        options = target;
    }

    options.forEach(p =>{
        const opt = document.createElement("option");
        opt.value = p;
        opt.textContent = p;
        if(p === value) opt.selected = true;
        select.appendChild(opt);
    });
    return select;
}