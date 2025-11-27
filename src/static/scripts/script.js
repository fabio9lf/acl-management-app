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
        console.log("Risposta dal server: ", data);
    });

    source_type.selectedIndex = 0;
    aggiorna(source_type, source_host, source_subnet);
    dest_type.selectedIndex = 0;
    aggiorna(dest_type, dest_host, dest_subnet);
    filtro.selectedIndex = 0;
    protocolli.selectedIndex = -1;
});

rimuovi.addEventListener("click", ()=>{
    console.log(line_number.value)

    fetch('/rimuovi?line_number=' + line_number.value)
    .then(response => response.text())
    .then(data => {
        console.log("Risposta dal server: ", data);
    });
    line_number.value = ""
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
            host.parentElement.classList.add("hide");
            subnet.parentElement.classList.add("hide");
        }
    }
}