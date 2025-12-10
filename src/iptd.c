#include <zebra.h>
#include "command.h"
#include "vty.h"

void iptd_vty_init(void);

int main(int argc, char** argv){
    frr_init();
    iptd_vty_init();
    frr_run();
    return 0;
}