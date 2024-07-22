`include "package.sv"
//import my_package::*;

module main;
    my_package::state_t current_state;
    int sum;
    
    initial begin

        sum = my_package::add(5, 7);

        current_state = my_package::RUNNING;
    end

endmodule
