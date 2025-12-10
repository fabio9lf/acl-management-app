#include <zebra.h>
#include "command.h"
#include "vty.h"
#include <stdlib.h>
#include <stdio.h>

DEFUN(iptables_cfg_cmd,
    iptables_cfg_cmd_cmd,
    "iptables CMD...",
    "Esegue comandi iptables\n", 
    "Argomenti iptables\n"
)
{
    char command[512];
    snprintf(command, sizeof(command), "iptables %s", argv_concat(argv, argc, 0));

    int ret = system(command);
    vty_out(vty, "Eseguito %s (ret = %d)\n", command, ret);

    return CMD_SUCCESS;
}

void iptd_vty_init(){
    install_element(CONFIG_NODE, &iptables_cfg_cmd);
}