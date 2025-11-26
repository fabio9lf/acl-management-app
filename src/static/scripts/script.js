let source_type  = document.getElementById("source_type");
let source_host = document.getElementById("source_host");
let source_subnet = document.getElementById("source_subnet");

let dest_type  = document.getElementById("dest_type");
let dest_host = document.getElementById("dest_host");
let dest_subnet = document.getElementById("dest_subnet");

let aggiungi = document.getElementById("aggiungi");

source_type.addEventListener("change", () => {
    aggiorna(source_type, source_host, source_subnet);
});

dest_type.addEventListener("change", ()=>{
    aggiorna(dest_type, dest_host, dest_subnet);
});

aggiungi.addEventListener("click", ()=>{
    
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